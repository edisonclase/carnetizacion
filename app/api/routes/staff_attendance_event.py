from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.staff import Staff
from app.models.staff_attendance_event import StaffAttendanceEvent
from app.models.staff_card import StaffCard
from app.schemas.staff_attendance_actions import (
    StaffAttendanceEntryRegister,
    StaffAttendanceExitRegister,
    StaffAttendanceQrEntryRegister,
)
from app.schemas.staff_attendance_event import (
    StaffAttendanceEventCreate,
    StaffAttendanceEventResponse,
    StaffAttendanceEventUpdate,
)
from app.services.staff_attendance_service import StaffAttendanceService

router = APIRouter(prefix="/staff-attendance-events", tags=["Staff Attendance Events"])


@router.post("/", response_model=StaffAttendanceEventResponse, status_code=status.HTTP_201_CREATED)
def create_staff_attendance_event(payload: StaffAttendanceEventCreate, db: Session = Depends(get_db)):
    staff = db.query(Staff).filter(Staff.id == payload.staff_id).first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El personal indicado no existe.",
        )

    if payload.staff_card_id is not None:
        card = db.query(StaffCard).filter(StaffCard.id == payload.staff_card_id).first()
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El carnet del personal indicado no existe.",
            )

        if card.staff_id != payload.staff_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El carnet indicado no pertenece al personal.",
            )

    event = StaffAttendanceEvent(
        staff_id=payload.staff_id,
        staff_card_id=payload.staff_card_id,
        center_id=payload.center_id,
        school_year_id=payload.school_year_id,
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


@router.post("/register-entry", response_model=StaffAttendanceEventResponse, status_code=status.HTTP_201_CREATED)
def register_staff_entry(payload: StaffAttendanceEntryRegister, db: Session = Depends(get_db)):
    service = StaffAttendanceService(db)

    try:
        event = service.create_entry_event(
            staff_id=payload.staff_id,
            staff_card_id=payload.staff_card_id,
            event_time=payload.event_time,
            source=payload.source,
            notes=payload.notes,
            recorded_by=payload.recorded_by,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return event


@router.post("/scan-qr-entry", status_code=status.HTTP_201_CREATED)
def scan_staff_qr_entry(payload: StaffAttendanceQrEntryRegister, db: Session = Depends(get_db)):
    service = StaffAttendanceService(db)

    try:
        result = service.create_entry_event_by_qr_token(
            qr_token=payload.qr_token,
            event_time=payload.event_time,
            source=payload.source,
            notes=payload.notes,
            recorded_by=payload.recorded_by,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    staff = result["staff"]
    event = result["event"]

    return {
        "message": "Entrada de personal registrada correctamente.",
        "staff": {
            "id": staff.id,
            "full_name": f"{staff.first_name} {staff.last_name}",
            "staff_code": staff.staff_code,
            "staff_group": staff.staff_group,
            "staff_position": staff.staff_position,
            "department": staff.department,
        },
        "event": {
            "id": event.id,
            "event_type": event.event_type,
            "status": event.status,
            "event_time": event.event_time,
            "source": event.source,
        },
    }


@router.post("/register-exit", response_model=StaffAttendanceEventResponse, status_code=status.HTTP_201_CREATED)
def register_staff_exit(payload: StaffAttendanceExitRegister, db: Session = Depends(get_db)):
    service = StaffAttendanceService(db)

    try:
        event = service.create_exit_event(
            staff_id=payload.staff_id,
            staff_card_id=payload.staff_card_id,
            event_time=payload.event_time,
            source=payload.source,
            status=payload.status,
            notes=payload.notes,
            recorded_by=payload.recorded_by,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return event


@router.get("/", response_model=list[StaffAttendanceEventResponse])
def list_staff_attendance_events(db: Session = Depends(get_db)):
    return db.query(StaffAttendanceEvent).order_by(StaffAttendanceEvent.id.asc()).all()


@router.get("/summary")
def staff_attendance_summary(
    center_id: int,
    school_year_id: int | None = None,
    date: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = (
        db.query(StaffAttendanceEvent, Staff)
        .join(Staff, Staff.id == StaffAttendanceEvent.staff_id)
        .filter(StaffAttendanceEvent.center_id == center_id)
    )

    if school_year_id is not None:
        query = query.filter(StaffAttendanceEvent.school_year_id == school_year_id)

    if date:
        query = query.filter(func.date(StaffAttendanceEvent.event_time) == date)

    rows = query.all()

    total_events = len(rows)
    total_entries = sum(1 for event, _ in rows if event.event_type == "entry")
    total_exits = sum(1 for event, _ in rows if event.event_type == "exit")

    by_gender = {
        "masculino": 0,
        "femenino": 0,
        "otro": 0,
        "sin_definir": 0,
    }

    by_department = {}
    unique_staff_ids = set()

    for event, staff in rows:
        unique_staff_ids.add(staff.id)

        gender = (staff.gender or "").strip().lower()
        if gender in by_gender:
            by_gender[gender] += 1
        else:
            by_gender["sin_definir"] += 1

        department = (staff.department or "Sin departamento").strip()
        if department not in by_department:
            by_department[department] = 0
        by_department[department] += 1

    return {
        "center_id": center_id,
        "school_year_id": school_year_id,
        "date": date,
        "total_events": total_events,
        "total_entries": total_entries,
        "total_exits": total_exits,
        "unique_staff_count": len(unique_staff_ids),
        "by_gender": by_gender,
        "by_department": by_department,
    }


@router.get("/{event_id}", response_model=StaffAttendanceEventResponse)
def get_staff_attendance_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(StaffAttendanceEvent).filter(StaffAttendanceEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento de asistencia del personal no encontrado.",
        )
    return event


@router.put("/{event_id}", response_model=StaffAttendanceEventResponse)
def update_staff_attendance_event(
    event_id: int,
    payload: StaffAttendanceEventUpdate,
    db: Session = Depends(get_db),
):
    event = db.query(StaffAttendanceEvent).filter(StaffAttendanceEvent.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento de asistencia del personal no encontrado.",
        )

    update_data = payload.model_dump(exclude_unset=True)

    if "staff_card_id" in update_data and update_data["staff_card_id"] is not None:
        card = db.query(StaffCard).filter(StaffCard.id == update_data["staff_card_id"]).first()
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El carnet del personal indicado no existe.",
            )

        if card.staff_id != event.staff_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El carnet indicado no pertenece al personal del evento.",
            )

    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)
    return event