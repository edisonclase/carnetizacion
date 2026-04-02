from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class AttendanceDailySummaryGenerate(BaseModel):
    student_id: int
    date: date


class AttendanceDailySummaryResponse(BaseModel):
    id: int
    student_id: int
    date: date
    status: str
    has_excuse: bool
    excuse_note: str | None = None
    first_entry_time: datetime | None = None
    minutes_late: int | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)