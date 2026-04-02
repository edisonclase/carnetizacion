from datetime import date, datetime, time

from sqlalchemy.orm import Session

from app.models.attendance_daily_summary import AttendanceDailySummary
from app.models.attendance_event import AttendanceEvent
from app.models.center_schedule import CenterSchedule
from app.models.student import Student


class DailySummaryService:
    def __init__(self, db: Session):
        self.db = db

    def get_student(self, student_id: int) -> Student | None:
        return self.db.query(Student).filter(Student.id == student_id).first()

    def get_schedule_for_student(self, student: Student) -> CenterSchedule | None:
        return (
            self.db.query(CenterSchedule)
            .filter(CenterSchedule.center_id == student.center_id)
            .first()
        )

    def get_day_events(self, student_id: int, target_date: date) -> list[AttendanceEvent]:
        start_dt = datetime.combine(target_date, time.min)
        end_dt = datetime.combine(target_date, time.max)

        return (
            self.db.query(AttendanceEvent)
            .filter(
                AttendanceEvent.student_id == student_id,
                AttendanceEvent.event_time >= start_dt,
                AttendanceEvent.event_time <= end_dt,
            )
            .order_by(AttendanceEvent.event_time.asc())
            .all()
        )

    def calculate_minutes_late(self, first_entry_time: datetime, entry_time: time) -> int:
        actual_minutes = first_entry_time.hour * 60 + first_entry_time.minute
        expected_minutes = entry_time.hour * 60 + entry_time.minute

        return max(0, actual_minutes - expected_minutes)

    def determine_daily_status(
        self,
        *,
        first_entry: AttendanceEvent | None,
        schedule: CenterSchedule,
    ) -> tuple[str, int | None, datetime | None]:
        if not first_entry:
            return "absent", None, None

        actual_minutes = first_entry.event_time.hour * 60 + first_entry.event_time.minute
        expected_minutes = schedule.entry_time.hour * 60 + schedule.entry_time.minute
        allowed_minutes = expected_minutes + schedule.late_tolerance_minutes

        if actual_minutes <= allowed_minutes:
            return "present", 0, first_entry.event_time

        minutes_late = self.calculate_minutes_late(first_entry.event_time, schedule.entry_time)
        return "late", minutes_late, first_entry.event_time

    def create_or_update_summary(self, student_id: int, target_date: date) -> AttendanceDailySummary:
        student = self.get_student(student_id)
        if not student:
            raise ValueError("El estudiante no existe.")

        schedule = self.get_schedule_for_student(student)
        if not schedule:
            raise ValueError("El centro del estudiante no tiene configuración horaria.")

        events = self.get_day_events(student_id, target_date)
        first_entry = next((event for event in events if event.event_type == "entry"), None)

        status, minutes_late, first_entry_time = self.determine_daily_status(
            first_entry=first_entry,
            schedule=schedule,
        )

        summary = (
            self.db.query(AttendanceDailySummary)
            .filter(
                AttendanceDailySummary.student_id == student_id,
                AttendanceDailySummary.date == target_date,
            )
            .first()
        )

        if summary:
            summary.status = status
            summary.first_entry_time = first_entry_time
            summary.minutes_late = minutes_late
        else:
            summary = AttendanceDailySummary(
                student_id=student_id,
                date=target_date,
                status=status,
                has_excuse=False,
                excuse_note=None,
                first_entry_time=first_entry_time,
                minutes_late=minutes_late,
            )
            self.db.add(summary)

        self.db.commit()
        self.db.refresh(summary)

        return summary