from datetime import datetime

from pydantic import BaseModel


class StaffAttendanceEntryRegister(BaseModel):
    staff_id: int
    staff_card_id: int | None = None
    event_time: datetime
    source: str = "scanner"
    notes: str | None = None
    recorded_by: str | None = None


class StaffAttendanceExitRegister(BaseModel):
    staff_id: int
    staff_card_id: int | None = None
    event_time: datetime
    source: str = "scanner"
    status: str = "normal_exit"
    notes: str | None = None
    recorded_by: str | None = None


class StaffAttendanceQrEntryRegister(BaseModel):
    qr_token: str
    event_time: datetime
    source: str = "scanner"
    notes: str | None = None
    recorded_by: str | None = None