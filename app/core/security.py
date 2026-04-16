from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.settings import settings

# Se mantiene bcrypt para no invalidar contraseñas ya registradas.
# Más adelante, si quieres migrar a argon2, se puede hacer de forma controlada.
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    expire_minutes = expires_minutes or settings.access_token_expire_minutes
    now_utc = datetime.now(timezone.utc)
    expire = now_utc + timedelta(minutes=expire_minutes)

    payload = {
        "sub": str(subject).strip().lower(),
        "iat": int(now_utc.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access",
    }

    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )


def extract_subject_from_token(token: str) -> str:
    try:
        payload = decode_access_token(token)

        token_type = payload.get("type")
        if token_type != "access":
            raise ValueError("Tipo de token inválido.")

        subject = payload.get("sub")
        if not subject or not str(subject).strip():
            raise ValueError("Token sin sujeto.")

        return str(subject).strip().lower()
    except JWTError as exc:
        raise ValueError("Token inválido o expirado.") from exc