from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class SchoolYearBase(BaseModel):
    center_id: int
    name: str
    start_date: date
    end_date: date
    is_active: bool = True


class SchoolYearCreate(SchoolYearBase):
    pass


class SchoolYearUpdate(BaseModel):
    name: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None


class SchoolYearResponse(SchoolYearBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)