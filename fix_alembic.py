from sqlalchemy import create_engine, text
from app.core.settings import settings

engine = create_engine(settings.database_url)

with engine.connect() as connection:
    result = connection.execute(text("SELECT version_num FROM alembic_version"))
    current = result.scalar()

    print(f"Versión actual en DB: {current}")

    if current == "3763e846ccb5":
        connection.execute(
            text("UPDATE alembic_version SET version_num = :new_version"),
            {"new_version": "420c14ec7d11"},
        )
        connection.commit()
        print("✅ Corregido a 420c14ec7d11")
    else:
        print("⚠️ No fue necesario corregir")