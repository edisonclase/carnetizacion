from fastapi import FastAPI
from sqlalchemy import text

from app.api.routes.center import router as center_router
from app.core.database import engine
from app.core.settings import settings

app = FastAPI(title=settings.app_name)

app.include_router(center_router)


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