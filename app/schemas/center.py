from datetime import datetime
import re

from pydantic import BaseModel, ConfigDict, field_validator


HEX_COLOR_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _normalize_optional_string(value: str | None) -> str | None:
    if value is None:
        return None

    value = value.strip()
    return value if value else None


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

    # Configuración de diseño del carnet
    card_design_key: str = "classic_green_v1"
    show_full_card_identity: bool = True

    # Identidad institucional general
    philosophy: str | None = None
    mission: str | None = None
    vision: str | None = None
    values: str | None = None

    # Textos cortos para carnet
    card_philosophy: str | None = None
    card_mission: str | None = None
    card_vision: str | None = None
    card_values: str | None = None
    card_footer_text: str | None = None

    # Datos institucionales
    motto: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    district_name: str | None = None
    management_code: str | None = None

    is_active: bool = True

    @field_validator(
        "name",
        "code",
        mode="before",
    )
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        if value is None:
            raise ValueError("Este campo es obligatorio.")
        value = value.strip()
        if not value:
            raise ValueError("Este campo no puede estar vacío.")
        return value

    @field_validator(
        "logo_url",
        "letterhead_url",
        "primary_color",
        "secondary_color",
        "accent_color",
        "text_color",
        "background_color",
        "philosophy",
        "mission",
        "vision",
        "values",
        "card_philosophy",
        "card_mission",
        "card_vision",
        "card_values",
        "card_footer_text",
        "motto",
        "address",
        "phone",
        "email",
        "district_name",
        "management_code",
        mode="before",
    )
    @classmethod
    def normalize_optional_fields(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @field_validator(
        "primary_color",
        "secondary_color",
        "accent_color",
        "text_color",
        "background_color",
    )
    @classmethod
    def validate_hex_colors(cls, value: str | None) -> str | None:
        if value is None:
            return None

        if not HEX_COLOR_RE.match(value):
            raise ValueError("Debe ser un color HEX válido, por ejemplo: #1f8f4a")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return None

        if not EMAIL_RE.match(value):
            raise ValueError("Debe ser un correo electrónico válido.")
        return value

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("card_design_key")
    @classmethod
    def validate_card_design_key(cls, value: str) -> str:
        allowed = {
            "classic_green_v1",
            "prestige_clean_v1",
            "nova_modern_v1",
        }
        normalized = value.strip()
        if normalized not in allowed:
            raise ValueError("Diseño de carnet no válido.")
        return normalized


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

    # Configuración de diseño del carnet
    card_design_key: str | None = None
    show_full_card_identity: bool | None = None

    # Identidad institucional general
    philosophy: str | None = None
    mission: str | None = None
    vision: str | None = None
    values: str | None = None

    # Textos cortos para carnet
    card_philosophy: str | None = None
    card_mission: str | None = None
    card_vision: str | None = None
    card_values: str | None = None
    card_footer_text: str | None = None

    # Datos institucionales
    motto: str | None = None
    address: str | None = None
    phone: str | None = None
    email: str | None = None
    district_name: str | None = None
    management_code: str | None = None

    is_active: bool | None = None

    @field_validator(
        "name",
        "code",
        mode="before",
    )
    @classmethod
    def normalize_optional_required_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("Este campo no puede estar vacío.")
        return value

    @field_validator(
        "logo_url",
        "letterhead_url",
        "primary_color",
        "secondary_color",
        "accent_color",
        "text_color",
        "background_color",
        "philosophy",
        "mission",
        "vision",
        "values",
        "card_philosophy",
        "card_mission",
        "card_vision",
        "card_values",
        "card_footer_text",
        "motto",
        "address",
        "phone",
        "email",
        "district_name",
        "management_code",
        mode="before",
    )
    @classmethod
    def normalize_optional_fields(cls, value: str | None) -> str | None:
        return _normalize_optional_string(value)

    @field_validator(
        "primary_color",
        "secondary_color",
        "accent_color",
        "text_color",
        "background_color",
    )
    @classmethod
    def validate_hex_colors(cls, value: str | None) -> str | None:
        if value is None:
            return None

        if not HEX_COLOR_RE.match(value):
            raise ValueError("Debe ser un color HEX válido, por ejemplo: #1f8f4a")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str | None) -> str | None:
        if value is None:
            return None

        if not EMAIL_RE.match(value):
            raise ValueError("Debe ser un correo electrónico válido.")
        return value

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip().upper()

    @field_validator("card_design_key")
    @classmethod
    def validate_card_design_key(cls, value: str | None) -> str | None:
        if value is None:
            return None

        allowed = {
            "classic_green_v1",
            "prestige_clean_v1",
            "nova_modern_v1",
        }
        normalized = value.strip()
        if normalized not in allowed:
            raise ValueError("Diseño de carnet no válido.")
        return normalized


class CenterResponse(CenterBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)