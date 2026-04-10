from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import verify_password

EMAIL = "clasedison@gmail.com"
PASSWORD = "123456"

db = SessionLocal()

try:
    user = db.query(User).filter(User.email == EMAIL).first()

    if not user:
        print("❌ Usuario no encontrado")
    else:
        print("✅ Usuario encontrado")
        print("Email:", user.email)
        print("Role:", user.role)
        print("Activo:", user.is_active)
        print("Hash actual:", user.password_hash)
        print("Verificación con 123456:", verify_password(PASSWORD, user.password_hash))
finally:
    db.close()