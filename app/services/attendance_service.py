from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.attendance_event import AttendanceEvent
from app.models.authorized_exit import AuthorizedExit
from app.models.card import Card
from app.models.center_schedule import CenterSchedule
from app.models.student import Student


WORKDAY_MAP = {
    0: "mon",
    1: "tue",
    2: "wed",
    3: "thu",
    4: "fri",
    5: "sat",
    6: "sun",
}


class AttendanceService:
    def __init__(self, db: Session):
        self.db = db

    def get_student_by_card_id(self, card_id: int) -> Student | None:
        card = self.db.query(Card).filter(Card.id == card_id).first()
        if not card:
            return None

        student = self.db.query(Student).filter(Student.id == card.student_id).first()
        return student

    def get_schedule_for_center(self, center_id: int) -> CenterSchedule | None:
        return (
            self.db.query(CenterSchedule)
            .filter(CenterSchedule.center_id == center_id)
            .first()
        )

    def is_workday(self, event_time: datetime, workdays: str) -> bool:
        day_code = WORKDAY_MAP[event_time.weekday()]
        configured_days = [day.strip().lower() for day in workdays.split(",") if day.strip()]
        return day_code in configured_days

    def classify_entry_status(self, event_time: datetime, schedule: CenterSchedule) -> str:
        event_clock = event_time.time()
        entry_clock = schedule.entry_time

        event_minutes = event_clock.hour * 60 + event_clock.minute
        entry_minutes = entry_clock.hour * 60 + entry_clock.minute
        allowed_minutes = entry_minutes + schedule.late_tolerance_minutes

        if event_minutes <= allowed_minutes:
            return "on_time"

        return "late"

    def validate_card_belongs_to_student(self, student_id: int, card_id: int | None) -> None:
        if card_id is None:
            return

        card = self.db.query(Card).filter(Card.id == card_id).first()
        if not card:
            raise ValueError("El carnet indicado no existe.")

        if card.student_id != student_id:
            raise ValueError("El carnet indicado no pertenece al estudiante.")

    def has_valid_authorized_exit(
        self,
        *,
        student_id: int,
        event_time: datetime,
        center_id: int,
    ) -> bool:
        schedule = self.get_schedule_for_center(center_id)
        if not schedule:
            raise ValueError("El centro no tiene configuración horaria registrada.")

        tolerance_minutes = schedule.authorized_exit_tolerance_minutes

        start_window = event_time - timedelta(minutes=tolerance_minutes)
        end_window = event_time + timedelta(minutes=tolerance_minutes)

        record = (
            self.db.query(AuthorizedExit)
            .filter(
                AuthorizedExit.student_id == student_id,
                AuthorizedExit.authorized_at >= start_window,
                AuthorizedExit.authorized_at <= end_window,
            )
            .order_by(AuthorizedExit.authorized_at.desc())
            .first()
        )

        return record is not None

    def create_entry_event(
        self,
        *,
        student_id: int,
        card_id: int | None,
        event_time: datetime,
        source: str = "scanner",
        notes: str | None = None,
        recorded_by: str | None = None,
    ) -> AttendanceEvent:
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError("El estudiante no existe.")

        self.validate_card_belongs_to_student(student_id=student.id, card_id=card_id)

        schedule = self.get_schedule_for_center(student.center_id)
        if not schedule:
            raise ValueError("El centro no tiene configuración horaria registrada.")

        if not self.is_workday(event_time, schedule.workdays):
            raise ValueError("La fecha indicada no corresponde a un día laborable del centro.")

        status = self.classify_entry_status(event_time, schedule)

        event = AttendanceEvent(
            student_id=student.id,
            card_id=card_id,
            event_type="entry",
            status=status,
            event_time=event_time,
            source=source,
            notes=notes,
            recorded_by=recorded_by,
        )

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        return event

    def create_exit_event(
        self,
        *,
        student_id: int,
        card_id: int | None,
        event_time: datetime,
        source: str = "scanner",
        status: str = "normal_exit",
        notes: str | None = None,
        recorded_by: str | None = None,
    ) -> AttendanceEvent:
        student = self.db.query(Student).filter(Student.id == student_id).first()
        if not student:
            raise ValueError("El estudiante no existe.")

        self.validate_card_belongs_to_student(student_id=student.id, card_id=card_id)

        schedule = self.get_schedule_for_center(student.center_id)
        if not schedule:
            raise ValueError("El centro no tiene configuración horaria registrada.")

        if not self.is_workday(event_time, schedule.workdays):
            raise ValueError("La fecha indicada no corresponde a un día laborable del centro.")

        if status == "authorized_exit":
            authorized = self.has_valid_authorized_exit(
                student_id=student.id,
                event_time=event_time,
                center_id=student.center_id,
            )
            if not authorized:
                raise ValueError(
                    "No existe una autorización válida de salida para este estudiante en un rango cercano a la hora indicada."
                )

        event = AttendanceEvent(
            student_id=student.id,
            card_id=card_id,
            event_type="exit",
            status=status,
            event_time=event_time,
            source=source,
            notes=notes,
            recorded_by=recorded_by,
        )

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        return event