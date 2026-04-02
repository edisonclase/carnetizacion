from datetime import date, datetime, time

from sqlalchemy.orm import Session

from app.models.attendance_daily_summary import AttendanceDailySummary
from app.models.attendance_event import AttendanceEvent
from app.models.center_attendance_day import CenterAttendanceDay
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


class CenterAttendanceDayService:
    def __init__(self, db: Session):
        self.db = db

    def get_schedule(self, center_id: int) -> CenterSchedule | None:
        return (
            self.db.query(CenterSchedule)
            .filter(CenterSchedule.center_id == center_id)
            .first()
        )

    def is_workday(self, target_date: date, workdays: str) -> bool:
        day_code = WORKDAY_MAP[target_date.weekday()]
        configured_days = [day.strip().lower() for day in workdays.split(",") if day.strip()]
        return day_code in configured_days

    def get_day_events(self, center_id: int, target_date: date) -> list[AttendanceEvent]:
        start_dt = datetime.combine(target_date, time.min)
        end_dt = datetime.combine(target_date, time.max)

        return (
            self.db.query(AttendanceEvent)
            .join(Student, Student.id == AttendanceEvent.student_id)
            .filter(
                Student.center_id == center_id,
                AttendanceEvent.event_time >= start_dt,
                AttendanceEvent.event_time <= end_dt,
            )
            .all()
        )

    def get_day_summaries(self, center_id: int, school_year_id: int, target_date: date) -> list[AttendanceDailySummary]:
        return (
            self.db.query(AttendanceDailySummary)
            .join(Student, Student.id == AttendanceDailySummary.student_id)
            .filter(
                Student.center_id == center_id,
                Student.school_year_id == school_year_id,
                AttendanceDailySummary.date == target_date,
            )
            .all()
        )

    def calculate_possible_early_dismissal(
        self,
        *,
        events: list[AttendanceEvent],
        schedule: CenterSchedule,
    ) -> bool:
        exit_events = [event for event in events if event.event_type == "exit"]
        if not exit_events:
            return False

        threshold_minutes = (
            schedule.early_dismissal_threshold_time.hour * 60
            + schedule.early_dismissal_threshold_time.minute
        )

        early_exits = []
        for event in exit_events:
            event_minutes = event.event_time.hour * 60 + event.event_time.minute
            if event_minutes < threshold_minutes:
                early_exits.append(event)

        if len(exit_events) == 0:
            return False

        percentage = (len(early_exits) / len(exit_events)) * 100
        return percentage >= schedule.early_dismissal_percentage_threshold

    def create_or_update_center_attendance_day(
        self,
        *,
        center_id: int,
        school_year_id: int,
        target_date: date,
    ) -> CenterAttendanceDay:
        schedule = self.get_schedule(center_id)
        if not schedule:
            raise ValueError("El centro no tiene configuración horaria registrada.")

        is_workday = self.is_workday(target_date, schedule.workdays)
        events = self.get_day_events(center_id, target_date)
        summaries = self.get_day_summaries(center_id, school_year_id, target_date)

        total_entries = len([event for event in events if event.event_type == "entry"])
        total_exits = len([event for event in events if event.event_type == "exit"])

        total_present = len([summary for summary in summaries if summary.status == "present"])
        total_late = len([summary for summary in summaries if summary.status == "late"])
        total_absent = len([summary for summary in summaries if summary.status == "absent"])
        total_with_excuse = len([summary for summary in summaries if summary.has_excuse])

        had_attendance_activity = total_entries >= schedule.minimum_attendance_for_school_day
        possible_no_school_day = is_workday and total_entries == 0
        possible_early_dismissal = self.calculate_possible_early_dismissal(
            events=events,
            schedule=schedule,
        )

        record = (
            self.db.query(CenterAttendanceDay)
            .filter(
                CenterAttendanceDay.center_id == center_id,
                CenterAttendanceDay.school_year_id == school_year_id,
                CenterAttendanceDay.date == target_date,
            )
            .first()
        )

        if record:
            record.is_workday = is_workday
            record.had_attendance_activity = had_attendance_activity
            record.possible_no_school_day = possible_no_school_day
            record.possible_early_dismissal = possible_early_dismissal
            record.total_entries = total_entries
            record.total_exits = total_exits
            record.total_present = total_present
            record.total_late = total_late
            record.total_absent = total_absent
            record.total_with_excuse = total_with_excuse
        else:
            record = CenterAttendanceDay(
                center_id=center_id,
                school_year_id=school_year_id,
                date=target_date,
                is_workday=is_workday,
                had_attendance_activity=had_attendance_activity,
                possible_no_school_day=possible_no_school_day,
                possible_early_dismissal=possible_early_dismissal,
                total_entries=total_entries,
                total_exits=total_exits,
                total_present=total_present,
                total_late=total_late,
                total_absent=total_absent,
                total_with_excuse=total_with_excuse,
            )
            self.db.add(record)

        self.db.commit()
        self.db.refresh(record)

        return record