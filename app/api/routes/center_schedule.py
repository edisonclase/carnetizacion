from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.center import Center
from app.models.center_schedule import CenterSchedule
from app.schemas.center_schedule import (
    CenterScheduleCreate,
    CenterScheduleResponse,
    CenterScheduleUpdate,
)

router = APIRouter(prefix="/center-schedules", tags=["Center Schedules"])


@router.post("/", response_model=CenterScheduleResponse, status_code=status.HTTP_201_CREATED)
def create_center_schedule(payload: CenterScheduleCreate, db: Session = Depends(get_db)):
    center = db.query(Center).filter(Center.id == payload.center_id).first()
    if not center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El centro educativo indicado no existe.",
        )

    existing_schedule = (
        db.query(CenterSchedule)
        .filter(CenterSchedule.center_id == payload.center_id)
        .first()
    )
    if existing_schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este centro ya tiene una configuración horaria registrada.",
        )

    schedule = CenterSchedule(
        center_id=payload.center_id,
        entry_time=payload.entry_time,
        exit_time=payload.exit_time,
        workdays=payload.workdays,
        late_tolerance_minutes=payload.late_tolerance_minutes,
        absence_cutoff_time=payload.absence_cutoff_time,
        early_dismissal_threshold_time=payload.early_dismissal_threshold_time,
        minimum_attendance_for_school_day=payload.minimum_attendance_for_school_day,
        early_dismissal_percentage_threshold=payload.early_dismissal_percentage_threshold,
    )

    db.add(schedule)
    db.commit()
    db.refresh(schedule)

    return schedule


@router.get("/", response_model=list[CenterScheduleResponse])
def list_center_schedules(db: Session = Depends(get_db)):
    schedules = db.query(CenterSchedule).order_by(CenterSchedule.id.asc()).all()
    return schedules


@router.get("/{schedule_id}", response_model=CenterScheduleResponse)
def get_center_schedule(schedule_id: int, db: Session = Depends(get_db)):
    schedule = db.query(CenterSchedule).filter(CenterSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración horaria no encontrada.",
        )

    return schedule


@router.put("/{schedule_id}", response_model=CenterScheduleResponse)
def update_center_schedule(
    schedule_id: int,
    payload: CenterScheduleUpdate,
    db: Session = Depends(get_db),
):
    schedule = db.query(CenterSchedule).filter(CenterSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuración horaria no encontrada.",
        )

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(schedule, field, value)

    db.commit()
    db.refresh(schedule)

    return schedule