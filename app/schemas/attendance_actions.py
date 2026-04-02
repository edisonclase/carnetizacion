from datetime import datetime

from pydantic import BaseModel


class AttendanceEntryRegister(BaseModel):
    student_id: int
    card_id: int | None = None
    event_time: datetime
    source: str = "scanner"
    notes: str | None = None
    recorded_by: str | None = None


class AttendanceExitRegister(BaseModel):
    student_id: int
    card_id: int | None = None
    event_time: datetime
    source: str = "scanner"
    status: str = "normal_exit"
    notes: str | None = None
    recorded_by: str | None = None