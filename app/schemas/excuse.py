from pydantic import BaseModel


class AttendanceExcuseApply(BaseModel):
    has_excuse: bool
    excuse_note: str | None = None