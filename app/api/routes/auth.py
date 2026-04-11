from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_current_user, get_db, require_roles, resolve_center_scope
from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.settings import settings
from app.models.center import Center
from app.models.user import User, UserRole
from app.schemas.auth import BootstrapSuperAdminRequest, LoginRequest, TokenResponse
from app.schemas.user import UserCreateRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["Auth"])


def _ensure_valid_role(role: str) -> None:
    if role not in UserRole.ALL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El rol indicado no es válido.",
        )


def _get_center_or_404(db: Session, center_id: int) -> Center:
    center = db.query(Center).filter(Center.id == center_id).first()
    if not center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El centro educativo indicado no existe.",
        )
    return center


@router.post("/bootstrap-super-admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def bootstrap_super_admin(
    payload: BootstrapSuperAdminRequest,
    db: Session = Depends(get_db),
):
    existing_users_count = db.query(User).count()

    if existing_users_count > 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La inicialización del super administrador ya fue realizada.",
        )

    if not settings.bootstrap_superadmin_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="BOOTSTRAP_SUPERADMIN_SECRET no está configurado en el entorno.",
        )

    if payload.bootstrap_secret != settings.bootstrap_superadmin_secret:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bootstrap secret inválido.",
        )

    normalized_email = payload.email.lower().strip()

    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con ese correo.",
        )

    user = User(
        center_id=None,
        full_name=payload.full_name.strip(),
        email=normalized_email,
        password_hash=get_password_hash(payload.password),
        role=UserRole.SUPER_ADMIN,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    normalized_email = payload.email.lower().strip()

    user = db.query(User).filter(User.email == normalized_email).first()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo.",
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.email)

    return TokenResponse(
        access_token=token,
        user=user,
    )
    
@router.post("/token")
def login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    normalized_email = form_data.username.lower().strip()

    user = db.query(User).filter(User.email == normalized_email).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo.",
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    token = create_access_token(subject=user.email)

    return {
        "access_token": token,
        "token_type": "bearer",
    }

@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN)),
):
    _ensure_valid_role(payload.role)

    normalized_email = payload.email.lower().strip()

    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con ese correo.",
        )

    if payload.role == UserRole.SUPER_ADMIN:
        center_id = None
    else:
        if payload.center_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Los usuarios que no son super_admin deben tener un centro asignado.",
            )

        resolve_center_scope(current_user, payload.center_id)
        _get_center_or_404(db, payload.center_id)
        center_id = payload.center_id

    user = User(
        center_id=center_id,
        full_name=payload.full_name.strip(),
        email=normalized_email,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        is_active=payload.is_active,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.get("/users", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN)),
):
    return db.query(User).order_by(User.created_at.desc(), User.id.desc()).all()