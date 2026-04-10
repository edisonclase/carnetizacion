from app.core.database import SessionLocal
from app.models.user import User

db = SessionLocal()

try:
    users = db.query(User).order_by(User.id.asc()).all()

    if not users:
        print("No hay usuarios.")
    else:
        for user in users:
            print({
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "is_active": user.is_active,
            })
finally:
    db.close()