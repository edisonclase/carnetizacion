from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.attendance_event import AttendanceEvent
from app.models.card import Card
from app.models.student import Student
from app.schemas.attendance_actions import (
    AttendanceEntryRegister,
    AttendanceExitRegister,
    AttendanceQrEntryRegister,
)
from app.schemas.attendance_event import (
    AttendanceEventCreate,
    AttendanceEventResponse,
    AttendanceEventUpdate,
)
from app.services.attendance_service import AttendanceService

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


@router.post(
    "/register-entry",
    response_model=AttendanceEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_entry(payload: AttendanceEntryRegister, db: Session = Depends(get_db)):
    service = AttendanceService(db)

    try:
        event = service.create_entry_event(
            student_id=payload.student_id,
            card_id=payload.card_id,
            event_time=payload.event_time,
            source=payload.source,
            notes=payload.notes,
            recorded_by=payload.recorded_by,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return event


@router.post(
    "/scan-qr-entry",
    status_code=status.HTTP_201_CREATED,
)
def scan_qr_entry(payload: AttendanceQrEntryRegister, db: Session = Depends(get_db)):
    service = AttendanceService(db)

    try:
        result = service.create_entry_event_by_qr_token(
            qr_token=payload.qr_token,
            event_time=payload.event_time,
            source=payload.source,
            notes=payload.notes,
            recorded_by=payload.recorded_by,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    student = result["student"]
    event = result["event"]
    summary = result["summary"]
    center_day = result["center_day"]

    return {
        "message": "Entrada registrada correctamente.",
        "student": {
            "id": student.id,
            "full_name": f"{student.first_name} {student.last_name}",
            "student_code": student.student_code,
            "grade": student.grade,
            "section": student.section,
        },
        "event": {
            "id": event.id,
            "event_type": event.event_type,
            "status": event.status,
            "event_time": event.event_time,
            "source": event.source,
        },
        "daily_summary": {
            "id": summary.id if summary else None,
            "date": summary.date if summary else None,
            "status": summary.status if summary else None,
            "first_entry_time": summary.first_entry_time if summary else None,
            "minutes_late": summary.minutes_late if summary else None,
            "has_excuse": summary.has_excuse if summary else False,
        },
        "center_day": {
            "id": center_day.id if center_day else None,
            "date": center_day.date if center_day else None,
            "total_entries": center_day.total_entries if center_day else 0,
            "total_present": center_day.total_present if center_day else 0,
            "total_late": center_day.total_late if center_day else 0,
            "total_absent": center_day.total_absent if center_day else 0,
            "total_with_excuse": center_day.total_with_excuse if center_day else 0,
        },
    }


@router.post(
    "/register-exit",
    response_model=AttendanceEventResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_exit(payload: AttendanceExitRegister, db: Session = Depends(get_db)):
    service = AttendanceService(db)

    try:
        event = service.create_exit_event(
            student_id=payload.student_id,
            card_id=payload.card_id,
            event_time=payload.event_time,
            source=payload.source,
            status=payload.status,
            notes=payload.notes,
            recorded_by=payload.recorded_by,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

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

        if card.student_id != event.student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El carnet indicado no pertenece al estudiante del evento.",
            )

    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    return event