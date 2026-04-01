from fastapi import FastAPI
from sqlalchemy import text

from app.core.database import Base, engine
from app.core.settings import settings
from app.models import Center

app = FastAPI(title=settings.app_name)


@app.get("/")
def read_root():
    return {
        "message": f"{settings.app_name} activo",
        "environment": settings.app_env,
        "debug": settings.app_debug,
    }


@app.get("/health")
def health_check():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected",
    }


@app.post("/setup/create-tables")
def create_tables():
    Base.metadata.create_all(bind=engine)
    return {"message": "Tablas creadas correctamente"}