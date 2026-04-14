from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from app.models.attendance_daily_summary import AttendanceDailySummary
from app.models.attendance_event import AttendanceEvent
from app.models.authorized_exit import AuthorizedExit
from app.models.card import Card
from app.models.center_attendance_day import CenterAttendanceDay
from app.models.center_schedule import CenterSchedule
from app.models.student import Student
from app.services.center_attendance_day_service import CenterAttendanceDayService
from app.services.daily_summary_service import DailySummaryService


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

        return self.db.query(Student).filter(Student.id == card.student_id).first()

    def get_card_by_qr_token(self, qr_token: str) -> Card | None:
        return (
            self.db.query(Card)
            .filter(Card.qr_token == qr_token)
            .first()
        )

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

    def has_entry_for_day(self, *, student_id: int, target_date: date) -> bool:
        day_start = datetime.combine(target_date, datetime.min.time())
        day_end = datetime.combine(target_date, datetime.max.time())

        record = (
            self.db.query(AttendanceEvent)
            .filter(
                AttendanceEvent.student_id == student_id,
                AttendanceEvent.event_type == "entry",
                AttendanceEvent.event_time >= day_start,
                AttendanceEvent.event_time <= day_end,
            )
            .first()
        )

        return record is not None

    def _refresh_attendance_aggregates(
        self,
        *,
        student: Student,
        event_time: datetime,
    ) -> dict:
        target_date = event_time.date()

        daily_summary_service = DailySummaryService(self.db)
        summary = daily_summary_service.create_or_update_summary(
            student_id=student.id,
            target_date=target_date,
        )

        center_day_service = CenterAttendanceDayService(self.db)
        center_day = center_day_service.create_or_update_center_attendance_day(
            center_id=student.center_id,
            school_year_id=student.school_year_id,
            target_date=target_date,
        )

        return {
            "summary": summary,
            "center_day": center_day,
        }

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

        if self.has_entry_for_day(student_id=student.id, target_date=event_time.date()):
            raise ValueError("El estudiante ya tiene una entrada registrada en esta fecha.")

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

        self._refresh_attendance_aggregates(
            student=student,
            event_time=event_time,
        )

        return event

    def create_entry_event_by_qr_token(
        self,
        *,
        qr_token: str,
        event_time: datetime,
        source: str = "scanner",
        notes: str | None = None,
        recorded_by: str | None = None,
    ) -> dict:
        card = self.get_card_by_qr_token(qr_token)
        if not card:
            raise ValueError("El QR no corresponde a un carnet válido.")

        student = self.db.query(Student).filter(Student.id == card.student_id).first()
        if not student:
            raise ValueError("El estudiante vinculado al carnet no existe.")

        event = self.create_entry_event(
            student_id=student.id,
            card_id=card.id,
            event_time=event_time,
            source=source,
            notes=notes,
            recorded_by=recorded_by,
        )

        refreshed_summary = (
            self.db.query(AttendanceDailySummary)
            .filter(
                AttendanceDailySummary.student_id == student.id,
                AttendanceDailySummary.date == event_time.date(),
            )
            .first()
        )

        refreshed_center_day = (
            self.db.query(CenterAttendanceDay)
            .filter(
                CenterAttendanceDay.center_id == student.center_id,
                CenterAttendanceDay.school_year_id == student.school_year_id,
                CenterAttendanceDay.date == event_time.date(),
            )
            .first()
        )

        return {
            "student": student,
            "card": card,
            "event": event,
            "summary": refreshed_summary,
            "center_day": refreshed_center_day,
        }

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

        self._refresh_attendance_aggregates(
            student=student,
            event_time=event_time,
        )

        return event