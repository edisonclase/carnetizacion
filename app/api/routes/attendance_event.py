from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.attendance_event import AttendanceEvent
from app.models.card import Card
from app.models.student import Student
from app.schemas.attendance_event import (
    AttendanceEventCreate,
    AttendanceEventResponse,
    AttendanceEventUpdate,
)

router = APIRouter(prefix="/attendance-events", tags=["Attendance Events"])


@router.post("/", response_model=AttendanceEventResponse, status_code=status.HTTP_201_CREATED)
def create_attendance_event(payload: AttendanceEventCreate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == payload.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El estudiante indicado no existe.",
        )

    if payload.card_id is not None:
        card = db.query(Card).filter(Card.id == payload.card_id).first()
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El carnet indicado no existe.",
            )

        if card.student_id != payload.student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El carnet indicado no pertenece al estudiante.",
            )

    event = AttendanceEvent(
        student_id=payload.student_id,
        card_id=payload.card_id,
        event_type=payload.event_type,
        status=payload.status,
        event_time=payload.event_time,
        source=payload.source,
        notes=payload.notes,
        recorded_by=payload.recorded_by,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@router.get("/", response_model=list[AttendanceEventResponse])
def list_attendance_events(db: Session = Depends(get_db)):
    events = db.query(AttendanceEvent).order_by(AttendanceEvent.id.asc()).all()
    return events


@router.get("/{event_id}", response_model=AttendanceEventResponse)
def get_attendance_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(AttendanceEvent).filter(AttendanceEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento de asistencia no encontrado.",
        )

    return event


@router.put("/{event_id}", response_model=AttendanceEventResponse)
def update_attendance_event(
    event_id: int,
    payload: AttendanceEventUpdate,
    db: Session = Depends(get_db),
):
    event = db.query(AttendanceEvent).filter(AttendanceEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento de asistencia no encontrado.",
        )

    update_data = payload.model_dump(exclude_unset=True)

    if "card_id" in update_data and update_data["card_id"] is not None:
        card = db.query(Card).filter(Card.id == update_data["card_id"]).first()
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El carnet indicado no existe.",
            )

        student_id_to_validate = update_data.get("student_id", event.student_id)
        if card.student_id != student_id_to_validate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El carnet indicado no pertenece al estudiante del evento.",
            )

    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    return event