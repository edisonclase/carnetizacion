from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text

from app.api.routes.attendance_daily_summary import router as attendance_daily_summary_router
from app.api.routes.attendance_event import router as attendance_event_router
from app.api.routes.auth import router as auth_router
from app.api.routes.authorized_exit import router as authorized_exit_router
from app.api.routes.card import router as card_router
from app.api.routes.card_qr import router as card_qr_router
from app.api.routes.center import router as center_router
from app.api.routes.center_attendance_day import router as center_attendance_day_router
from app.api.routes.center_schedule import router as center_schedule_router
from app.api.routes.guardian import router as guardian_router
from app.api.routes.reports import router as reports_router
from app.api.routes.school_year import router as school_year_router
from app.api.routes.student import router as student_router
from app.api.routes.ui import router as ui_router
from app.api.routes.uploads import router as uploads_router
from app.core.database import engine
from app.core.settings import settings
from app.models.user import User  # noqa: F401
from app.api.routes.billing import router as billing_router
from app.models.billing_invoice import BillingInvoice  # noqa: F401
from app.models.billing_payment import BillingPayment  # noqa: F401
from app.api.routes import staff
from app.api.routes import staff_card

app = FastAPI(title=settings.app_name)

# Archivos estáticos para CSS, JS e imágenes estáticas
app.mount("/static", StaticFiles(directory="app/ui/static"), name="static")

# REGISTRO DE ROUTERS
# Se coloca card_qr_router al inicio para evitar conflictos con rutas de ID en card_router
app.include_router(card_qr_router)

app.include_router(auth_router)
app.include_router(center_router)
app.include_router(school_year_router)
app.include_router(student_router)
app.include_router(guardian_router)
app.include_router(card_router)
app.include_router(center_schedule_router)
app.include_router(attendance_event_router)
app.include_router(attendance_daily_summary_router)
app.include_router(center_attendance_day_router)
app.include_router(authorized_exit_router)
app.include_router(reports_router)
app.include_router(ui_router)
app.include_router(uploads_router)
app.include_router(billing_router)
app.include_router(staff.router)
app.include_router(staff_card.router)

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