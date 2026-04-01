from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AttendanceEventBase(BaseModel):
    student_id: int
    card_id: int | None = None
    event_type: str
    status: str | None = None
    event_time: datetime
    source: str = "scanner"
    notes: str | None = None
    recorded_by: str | None = None


class AttendanceEventCreate(AttendanceEventBase):
    pass


class AttendanceEventUpdate(BaseModel):
    card_id: int | None = None
    event_type: str | None = None
    status: str | None = None
    event_time: datetime | None = None
    source: str | None = None
    notes: str | None = None
    recorded_by: str | None = None


class AttendanceEventResponse(AttendanceEventBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)