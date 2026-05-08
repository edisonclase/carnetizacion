from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.staff import Staff
from app.models.staff_attendance_event import StaffAttendanceEvent
from app.models.staff_card import StaffCard
from app.schemas.staff_attendance_event import (
    StaffAttendanceEventCreate,
    StaffAttendanceEventResponse,
)

router = APIRouter(prefix="/staff-attendance-events", tags=["Staff Attendance Events"])


DUPLICATE_SCAN_SECONDS = 45


def _day_range(target_date: date) -> tuple[datetime, datetime]:
    start = datetime.combine(target_date, time.min).replace(tzinfo=timezone.utc)
    end = start + timedelta(days=1)
    return start, end


def _staff_full_name(staff: Staff) -> str:
    full_name = getattr(staff, "full_name", None)
    if full_name:
        return full_name

    first_name = getattr(staff, "first_name", "") or ""
    last_name = getattr(staff, "last_name", "") or ""
    combined = f"{first_name} {last_name}".strip()

    return combined or f"Personal #{staff.id}"


def _normalize_gender(value: str | None) -> str:
    raw = str(value or "").strip().lower()

    if raw in ["m", "masculino", "male"]:
        return "masculino"

    if raw in ["f", "femenino", "female"]:
        return "femenino"

    if raw in ["otro", "o", "other"]:
        return "otro"

    return "sin_definir"


def _next_event_type(db: Session, staff_id: int, target_time: datetime) -> str:
    start, end = _day_range(target_time.date())

    last_event = (
        db.query(StaffAttendanceEvent)
        .filter(
            StaffAttendanceEvent.staff_id == staff_id,
            StaffAttendanceEvent.event_time >= start,
            StaffAttendanceEvent.event_time < end,
        )
        .order_by(StaffAttendanceEvent.event_time.desc())
        .first()
    )

    if not last_event:
        return "entry"

    if last_event.event_type == "entry":
        return "exit"

    return "entry"


def _get_active_staff_card_by_token(db: Session, qr_token: str) -> StaffCard:
    card = (
        db.query(StaffCard)
        .filter(
            StaffCard.qr_token == qr_token,
            StaffCard.is_active == True,
        )
        .first()
    )

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carnet de personal no encontrado o inactivo.",
        )

    return card


@router.post("/", response_model=StaffAttendanceEventResponse, status_code=status.HTTP_201_CREATED)
def create_staff_attendance_event(
    payload: StaffAttendanceEventCreate,
    db: Session = Depends(get_db),
):
    staff = db.query(Staff).filter(Staff.id == payload.staff_id).first()

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal no encontrado.",
        )

    event = StaffAttendanceEvent(**payload.model_dump())

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@router.post("/scan/{qr_token}", status_code=status.HTTP_201_CREATED)
def scan_staff_qr(
    qr_token: str,
    school_year_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    card = _get_active_staff_card_by_token(db, qr_token)

    staff = db.query(Staff).filter(Staff.id == card.staff_id).first()

    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El carnet existe, pero el personal asociado no fue encontrado.",
        )

    if hasattr(staff, "is_active") and not staff.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El personal asociado a este carnet está inactivo.",
        )

    now = datetime.now(timezone.utc)

    last_event = (
        db.query(StaffAttendanceEvent)
        .filter(StaffAttendanceEvent.staff_id == staff.id)
        .order_by(StaffAttendanceEvent.event_time.desc())
        .first()
    )

    if last_event:
        seconds_diff = abs((now - last_event.event_time).total_seconds())
        if seconds_diff <= DUPLICATE_SCAN_SECONDS:
            return {
                "created": False,
                "duplicate_ignored": True,
                "message": "Lectura duplicada ignorada.",
                "event": StaffAttendanceEventResponse.model_validate(last_event).model_dump(mode="json"),
                "staff": {
                    "id": staff.id,
                    "full_name": _staff_full_name(staff),
                    "gender": getattr(staff, "gender", None),
                    "department": getattr(staff, "department", None),
                },
            }

    event_type = _next_event_type(db, staff.id, now)

    event = StaffAttendanceEvent(
        staff_id=staff.id,
        staff_card_id=card.id,
        center_id=staff.center_id,
        school_year_id=school_year_id,
        event_type=event_type,
        status="registered",
        event_time=now,
        source="scanner",
        notes="Registro automático mediante QR de personal.",
        recorded_by="qr_scanner",
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return {
        "created": True,
        "duplicate_ignored": False,
        "message": "Entrada registrada correctamente." if event_type == "entry" else "Salida registrada correctamente.",
        "event": StaffAttendanceEventResponse.model_validate(event).model_dump(mode="json"),
        "staff": {
            "id": staff.id,
            "full_name": _staff_full_name(staff),
            "gender": getattr(staff, "gender", None),
            "department": getattr(staff, "department", None),
        },
    }


@router.get("/", response_model=list[StaffAttendanceEventResponse])
def list_staff_attendance_events(
    center_id: int | None = Query(default=None),
    school_year_id: int | None = Query(default=None),
    staff_id: int | None = Query(default=None),
    event_date: date | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    query = db.query(StaffAttendanceEvent)

    if center_id:
        query = query.filter(StaffAttendanceEvent.center_id == center_id)

    if school_year_id:
        query = query.filter(StaffAttendanceEvent.school_year_id == school_year_id)

    if staff_id:
        query = query.filter(StaffAttendanceEvent.staff_id == staff_id)

    if event_date:
        start, end = _day_range(event_date)
        query = query.filter(
            StaffAttendanceEvent.event_time >= start,
            StaffAttendanceEvent.event_time < end,
        )

    return (
        query.order_by(StaffAttendanceEvent.event_time.desc())
        .limit(limit)
        .all()
    )


@router.get("/summary")
def get_staff_attendance_summary(
    center_id: int = Query(...),
    school_year_id: int | None = Query(default=None),
    date: date = Query(...),
    db: Session = Depends(get_db),
):
    start, end = _day_range(date)

    base_query = (
        db.query(StaffAttendanceEvent)
        .join(Staff, Staff.id == StaffAttendanceEvent.staff_id)
        .filter(
            StaffAttendanceEvent.center_id == center_id,
            StaffAttendanceEvent.event_time >= start,
            StaffAttendanceEvent.event_time < end,
        )
    )

    if school_year_id:
        base_query = base_query.filter(StaffAttendanceEvent.school_year_id == school_year_id)

    events = base_query.all()

    total_events = len(events)
    total_entries = sum(1 for event in events if event.event_type == "entry")
    total_exits = sum(1 for event in events if event.event_type == "exit")
    unique_staff_ids = {event.staff_id for event in events}

    gender_rows = (
        base_query.with_entities(
            Staff.gender,
            func.count(distinct(StaffAttendanceEvent.staff_id)),
        )
        .group_by(Staff.gender)
        .all()
    )

    department_rows = (
        base_query.with_entities(
            Staff.department,
            func.count(StaffAttendanceEvent.id),
        )
        .group_by(Staff.department)
        .all()
    )

    by_gender = {
        "masculino": 0,
        "femenino": 0,
        "otro": 0,
        "sin_definir": 0,
    }

    for gender, count in gender_rows:
        normalized = _normalize_gender(gender)
        by_gender[normalized] = by_gender.get(normalized, 0) + int(count or 0)

    by_department = {}

    for department, count in department_rows:
        key = str(department or "Sin departamento").strip() or "Sin departamento"
        by_department[key] = int(count or 0)

    latest_events = (
        base_query.order_by(StaffAttendanceEvent.event_time.desc())
        .limit(10)
        .all()
    )

    latest = []

    for event in latest_events:
        staff = db.query(Staff).filter(Staff.id == event.staff_id).first()
        latest.append(
            {
                "id": event.id,
                "staff_id": event.staff_id,
                "staff_name": _staff_full_name(staff) if staff else f"Personal #{event.staff_id}",
                "event_type": event.event_type,
                "status": event.status,
                "event_time": event.event_time,
                "department": getattr(staff, "department", None) if staff else None,
                "gender": getattr(staff, "gender", None) if staff else None,
            }
        )

    return {
        "date": date.isoformat(),
        "center_id": center_id,
        "school_year_id": school_year_id,
        "total_events": total_events,
        "total_entries": total_entries,
        "total_exits": total_exits,
        "unique_staff_count": len(unique_staff_ids),
        "by_gender": by_gender,
        "by_department": by_department,
        "latest_events": latest,
    }