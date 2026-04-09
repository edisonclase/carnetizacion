from pydantic import BaseModel

from app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class BootstrapSuperAdminRequest(BaseModel):
    bootstrap_secret: str
    full_name: str
    email: str
    password: str