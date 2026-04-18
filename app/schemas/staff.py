from datetime import datetime
import re

from pydantic import BaseModel, ConfigDict, field_validator


ALLOWED_STAFF_GROUPS = {
    "administrativo",
    "apoyo",
    "docente_tecnico",
}

ALLOWED_STAFF_POSITIONS = {
    "secretaria",
    "digitador",
    "administrativo_otro",

    "conserje",
    "mayordomo",
    "jardinero",
    "portero",
    "sereno",
    "apoyo_otro",

    "docente",
    "director",
    "subdirector",
    "coordinador",
    "psicologo",
    "psicologa",
    "orientador",
    "orientadora",
    "tecnico_otro",
}

NATIONAL_ID_RE = re.compile(r"^[0-9A-Za-z\- ]+$")


def _normalize_optional_string(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value if value else None


class StaffBase(BaseModel):
    center_id: int
    school_year_id: int | None = None

    first_name: str
    last_name: str
    staff_code: str
    national_id: str | None = None
    photo_path: str | None = None

    staff_group: str
    staff_position: str
    department: str | None = None

    is_active: bool = True

    @field_validator("first_name", "last_name", "staff_code", "staff_group", "staff_position", mode="before")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if value is None:
            raise ValueError("Este campo es obligatorio.")
        value = value.strip()
        if not value:
            raise ValueError("Este campo no puede estar vacío.")
        return value

    @field_validator("national_id", "photo_path", "department", mode="before")
    @classmethod
    def normalize_optional_fields(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @field_validator("staff_code")
    @classmethod
    def normalize_staff_code(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("staff_group")
    @classmethod
    def validate_staff_group(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in ALLOWED_STAFF_GROUPS:
            raise ValueError("Grupo de personal no válido.")
        return normalized

    @field_validator("staff_position")
    @classmethod
    def validate_staff_position(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in ALLOWED_STAFF_POSITIONS:
            raise ValueError("Cargo de personal no válido.")
        return normalized

    @field_validator("national_id")
    @classmethod
    def validate_national_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not NATIONAL_ID_RE.match(value):
            raise ValueError("El documento de identidad contiene caracteres no válidos.")
        return value


class StaffCreate(StaffBase):
    pass


class StaffUpdate(BaseModel):
    center_id: int | None = None
    school_year_id: int | None = None

    first_name: str | None = None
    last_name: str | None = None
    staff_code: str | None = None
    national_id: str | None = None
    photo_path: str | None = None

    staff_group: str | None = None
    staff_position: str | None = None
    department: str | None = None

    is_active: bool | None = None

    @field_validator("first_name", "last_name", "staff_code", "staff_group", "staff_position", mode="before")
    @classmethod
    def normalize_required_updates(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Este campo no puede estar vacío.")
        return value

    @field_validator("national_id", "photo_path", "department", mode="before")
    @classmethod
    def normalize_optional_fields(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @field_validator("staff_code")
    @classmethod
    def normalize_staff_code(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().upper()

    @field_validator("staff_group")
    @classmethod
    def validate_staff_group(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if normalized not in ALLOWED_STAFF_GROUPS:
            raise ValueError("Grupo de personal no válido.")
        return normalized

    @field_validator("staff_position")
    @classmethod
    def validate_staff_position(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().lower()
        if normalized not in ALLOWED_STAFF_POSITIONS:
            raise ValueError("Cargo de personal no válido.")
        return normalized

    @field_validator("national_id")
    @classmethod
    def validate_national_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not NATIONAL_ID_RE.match(value):
            raise ValueError("El documento de identidad contiene caracteres no válidos.")
        return value


class StaffResponse(StaffBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)