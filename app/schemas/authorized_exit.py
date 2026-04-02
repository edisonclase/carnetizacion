from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AuthorizedExitBase(BaseModel):
    student_id: int
    authorized_by: str
    reason: str
    authorized_at: datetime
    notes: str | None = None


class AuthorizedExitCreate(AuthorizedExitBase):
    pass


class AuthorizedExitResponse(AuthorizedExitBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)