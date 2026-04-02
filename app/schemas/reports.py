from datetime import date, datetime

from pydantic import BaseModel


class DailyInstitutionalReportQuery(BaseModel):
    center_id: int
    school_year_id: int
    date: date


class StudentDailyStatusItem(BaseModel):
    student_id: int
    student_code: str
    minerd_id: str | None = None
    full_name: str
    gender: str | None = None
    grade: str
    section: str
    status: str
    has_excuse: bool
    excuse_note: str | None = None
    first_entry_time: datetime | None = None
    minutes_late: int | None = None


class DailyInstitutionalReportResponse(BaseModel):
    center_id: int
    school_year_id: int
    date: date
    is_workday: bool
    had_attendance_activity: bool
    possible_no_school_day: bool
    possible_early_dismissal: bool
    total_entries: int
    total_exits: int
    total_present: int
    total_late: int
    total_absent: int
    total_with_excuse: int
    present_students: list[StudentDailyStatusItem]
    late_students: list[StudentDailyStatusItem]
    absent_students: list[StudentDailyStatusItem]
    students_with_excuse: list[StudentDailyStatusItem]