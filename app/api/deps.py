from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import extract_subject_from_token
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _raise_unauthorized(detail: str = "No autenticado o token inválido.") -> None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        subject = extract_subject_from_token(token)
    except ValueError as exc:
        _raise_unauthorized("No autenticado o token inválido.")

    user = db.query(User).filter(User.email == subject).first()

    if not user:
        _raise_unauthorized("Usuario no autorizado.")

    if not user.is_active:
        _raise_unauthorized("Usuario inactivo o no autorizado.")

    return user


def require_roles(*allowed_roles: str):
    invalid_roles = [role for role in allowed_roles if role not in UserRole.ALL]
    if invalid_roles:
        raise ValueError(f"Roles inválidos en require_roles: {invalid_roles}")

    def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para realizar esta acción.",
            )
        return current_user

    return checker


def resolve_center_scope(
    current_user: User,
    requested_center_id: int | None = None,
) -> int | None:
    if current_user.role == UserRole.SUPER_ADMIN:
        return requested_center_id

    if current_user.center_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Este usuario no tiene un centro asignado.",
        )

    if requested_center_id is not None and int(requested_center_id) != int(current_user.center_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No puedes acceder a información de otro centro.",
        )

    return current_user.center_id