from datetime import datetime, time

from pydantic import BaseModel, ConfigDict


class CenterScheduleBase(BaseModel):
    center_id: int
    entry_time: time
    exit_time: time
    workdays: str
    late_tolerance_minutes: int = 0
    absence_cutoff_time: time
    early_dismissal_threshold_time: time
    minimum_attendance_for_school_day: int = 1
    early_dismissal_percentage_threshold: int = 40
    authorized_exit_tolerance_minutes: int = 15


class CenterScheduleCreate(CenterScheduleBase):
    pass


class CenterScheduleUpdate(BaseModel):
    entry_time: time | None = None
    exit_time: time | None = None
    workdays: str | None = None
    late_tolerance_minutes: int | None = None
    absence_cutoff_time: time | None = None
    early_dismissal_threshold_time: time | None = None
    minimum_attendance_for_school_day: int | None = None
    early_dismissal_percentage_threshold: int | None = None
    authorized_exit_tolerance_minutes: int | None = None


class CenterScheduleResponse(CenterScheduleBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)