from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class CenterAttendanceDayGenerate(BaseModel):
    center_id: int
    school_year_id: int
    date: date


class CenterAttendanceDayResponse(BaseModel):
    id: int
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
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)