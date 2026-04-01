from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CardBase(BaseModel):
    student_id: int
    card_code: str
    qr_token: str
    is_active: bool = True
    deactivation_reason: str | None = None


class CardCreate(CardBase):
    pass


class CardUpdate(BaseModel):
    card_code: str | None = None
    qr_token: str | None = None
    is_active: bool | None = None
    deactivation_reason: str | None = None


class CardResponse(CardBase):
    id: int
    issued_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)