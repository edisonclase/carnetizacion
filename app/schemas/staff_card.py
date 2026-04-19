from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class StaffCardBase(BaseModel):
    staff_id: int
    card_code: str
    qr_token: str
    expires_at: datetime | None = None
    is_active: bool = True

    @field_validator("card_code", "qr_token", mode="before")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if value is None:
            raise ValueError("Este campo es obligatorio.")
        value = value.strip()
        if not value:
            raise ValueError("Este campo no puede estar vacío.")
        return value


class StaffCardCreate(StaffCardBase):
    pass


class StaffCardUpdate(BaseModel):
    card_code: str | None = None
    qr_token: str | None = None
    expires_at: datetime | None = None
    is_active: bool | None = None

    @field_validator("card_code", "qr_token", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Este campo no puede estar vacío.")
        return value


class StaffCardResponse(StaffCardBase):
    id: int
    issued_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)