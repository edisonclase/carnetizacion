from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.card import CardResponse
from app.schemas.guardian import GuardianResponse


class StudentBase(BaseModel):
    center_id: int
    school_year_id: int
    student_code: str
    minerd_id: str | None = None
    first_name: str
    last_name: str
    birth_date: date | None = None
    gender: str | None = None
    grade: str
    section: str
    photo_path: str | None = None
    is_active: bool = True


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    student_code: str | None = None
    minerd_id: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    gender: str | None = None
    grade: str | None = None
    section: str | None = None
    photo_path: str | None = None
    is_active: bool | None = None


class StudentResponse(StudentBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StudentRegisterGuardianInput(BaseModel):
    full_name: str
    relationship_type: str
    phone: str | None = None
    whatsapp: str | None = None
    email: str | None = None


class StudentRegisterRequest(StudentCreate):
    guardian: StudentRegisterGuardianInput


class StudentRegisterResponse(BaseModel):
    student: StudentResponse
    guardian: GuardianResponse
    card: CardResponse