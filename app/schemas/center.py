from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CenterBase(BaseModel):
    name: str
    code: str

    # Identidad visual
    logo_url: str | None = None
    letterhead_url: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    accent_color: str | None = None
    text_color: str | None = None
    background_color: str | None = None

    # Identidad institucional
    philosophy: str | None = None
    mission: str | None = None
    vision: str | None = None
    values: str | None = None

    # Datos institucionales
    motto: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    district_name: str | None = None
    management_code: str | None = None

    is_active: bool = True


class CenterCreate(CenterBase):
    pass


class CenterUpdate(BaseModel):
    name: str | None = None
    code: str | None = None

    # Identidad visual
    logo_url: str | None = None
    letterhead_url: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    accent_color: str | None = None
    text_color: str | None = None
    background_color: str | None = None

    # Identidad institucional
    philosophy: str | None = None
    mission: str | None = None
    vision: str | None = None
    values: str | None = None

    # Datos institucionales
    motto: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    district_name: str | None = None
    management_code: str | None = None

    is_active: bool | None = None


class CenterResponse(CenterBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)