from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StaffAttendanceEventBase(BaseModel):
    staff_id: int
    staff_card_id: int | None = None
    center_id: int
    school_year_id: int | None = None
    event_type: str
    status: str | None = None
    event_time: datetime
    source: str = "scanner"
    notes: str | None = None
    recorded_by: str | None = None


class StaffAttendanceEventCreate(StaffAttendanceEventBase):
    pass


class StaffAttendanceEventUpdate(BaseModel):
    staff_card_id: int | None = None
    event_type: str | None = None
    status: str | None = None
    event_time: datetime | None = None
    source: str | None = None
    notes: str | None = None
    recorded_by: str | None = None


class StaffAttendanceEventResponse(StaffAttendanceEventBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)