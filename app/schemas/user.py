from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    center_id: int | None
    full_name: str
    email: str
    role: str
    is_active: bool
    last_login_at: datetime | None
    created_at: datetime


class UserCreateRequest(BaseModel):
    center_id: int | None = None
    full_name: str
    email: str
    password: str
    role: str
    is_active: bool = True