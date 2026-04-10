from app.core.database import SessionLocal
from app.models.user import User

OLD_EMAIL = "tu_correo@ejemplo.com"
NEW_EMAIL = "clasedison@gmail.com"

db = SessionLocal()

try:
    user = db.query(User).filter(User.email == OLD_EMAIL).first()

    if not user:
        print("❌ Usuario no encontrado")
    else:
        user.email = NEW_EMAIL.lower().strip()
        db.commit()
        db.refresh(user)
        print("✅ Correo actualizado correctamente")
        print("Nuevo correo:", user.email)
finally:
    db.close()