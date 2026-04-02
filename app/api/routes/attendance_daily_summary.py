from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.attendance_daily_summary import AttendanceDailySummary
from app.schemas.attendance_daily_summary import (
    AttendanceDailySummaryGenerate,
    AttendanceDailySummaryResponse,
)
from app.services.daily_summary_service import DailySummaryService

router = APIRouter(
    prefix="/attendance-daily-summary",
    tags=["Attendance Daily Summary"],
)


@router.post(
    "/generate",
    response_model=AttendanceDailySummaryResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_daily_summary(
    payload: AttendanceDailySummaryGenerate,
    db: Session = Depends(get_db),
):
    service = DailySummaryService(db)

    try:
        summary = service.create_or_update_summary(
            student_id=payload.student_id,
            target_date=payload.date,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return summary


@router.get("/", response_model=list[AttendanceDailySummaryResponse])
def list_daily_summaries(db: Session = Depends(get_db)):
    summaries = (
        db.query(AttendanceDailySummary)
        .order_by(AttendanceDailySummary.date.desc(), AttendanceDailySummary.id.asc())
        .all()
    )
    return summaries


@router.get("/{summary_id}", response_model=AttendanceDailySummaryResponse)
def get_daily_summary(summary_id: int, db: Session = Depends(get_db)):
    summary = (
        db.query(AttendanceDailySummary)
        .filter(AttendanceDailySummary.id == summary_id)
        .first()
    )
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resumen diario no encontrado.",
        )

    return summary