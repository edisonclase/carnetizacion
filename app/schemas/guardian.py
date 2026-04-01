from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GuardianBase(BaseModel):
    student_id: int
    full_name: str
    relationship_type: str
    phone: str | None = None
    whatsapp: str | None = None
    email: str | None = None
    is_primary: bool = False
    is_active: bool = True


class GuardianCreate(GuardianBase):
    pass


class GuardianUpdate(BaseModel):
    full_name: str | None = None
    relationship_type: str | None = None
    phone: str | None = None
    whatsapp: str | None = None
    email: str | None = None
    is_primary: bool | None = None
    is_active: bool | None = None


class GuardianResponse(GuardianBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)