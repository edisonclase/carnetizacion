from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CenterBase(BaseModel):
    name: str
    code: str
    logo_url: str | None = None
    is_active: bool = True


class CenterCreate(CenterBase):
    pass


class CenterUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    logo_url: str | None = None
    is_active: bool | None = None


class CenterResponse(CenterBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)