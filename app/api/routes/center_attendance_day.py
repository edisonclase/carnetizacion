from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.center_attendance_day import CenterAttendanceDay
from app.schemas.center_attendance_day import (
    CenterAttendanceDayGenerate,
    CenterAttendanceDayResponse,
)
from app.services.center_attendance_day_service import CenterAttendanceDayService

router = APIRouter(
    prefix="/center-attendance-days",
    tags=["Center Attendance Days"],
)


@router.post(
    "/generate",
    response_model=CenterAttendanceDayResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_center_attendance_day(
    payload: CenterAttendanceDayGenerate,
    db: Session = Depends(get_db),
):
    service = CenterAttendanceDayService(db)

    try:
        record = service.create_or_update_center_attendance_day(
            center_id=payload.center_id,
            school_year_id=payload.school_year_id,
            target_date=payload.date,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return record


@router.get("/", response_model=list[CenterAttendanceDayResponse])
def list_center_attendance_days(db: Session = Depends(get_db)):
    records = (
        db.query(CenterAttendanceDay)
        .order_by(CenterAttendanceDay.date.desc(), CenterAttendanceDay.id.asc())
        .all()
    )
    return records


@router.get("/{record_id}", response_model=CenterAttendanceDayResponse)
def get_center_attendance_day(record_id: int, db: Session = Depends(get_db)):
    record = (
        db.query(CenterAttendanceDay)
        .filter(CenterAttendanceDay.id == record_id)
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consolidado institucional no encontrado.",
        )

    return record