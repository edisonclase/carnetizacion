from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()

try:
    user = db.query(User).filter(User.email == "tu_correo@ejemplo.com").first()

    if not user:
        print("Usuario no encontrado")
    else:
        user.password_hash = "$2b$12$Jc2McW78kk2ekkclq3OZsunwitPl6tKWh1O3LzvqmaKW7rUgvnTba"
        db.commit()
        print("Contraseña actualizada correctamente")
finally:
    db.close()