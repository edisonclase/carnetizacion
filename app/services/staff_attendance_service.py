from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.staff import Staff
from app.models.staff_attendance_event import StaffAttendanceEvent
from app.models.staff_card import StaffCard


class StaffAttendanceService:
    def __init__(self, db: Session):
        self.db = db

    def get_staff_by_card_id(self, staff_card_id: int) -> Staff | None:
        card = self.db.query(StaffCard).filter(StaffCard.id == staff_card_id).first()
        if not card:
            return None
        return self.db.query(Staff).filter(Staff.id == card.staff_id).first()

    def get_card_by_qr_token(self, qr_token: str) -> StaffCard | None:
        return (
            self.db.query(StaffCard)
            .filter(StaffCard.qr_token == qr_token, StaffCard.is_active == True)
            .first()
        )

    def validate_card_belongs_to_staff(self, staff_id: int, staff_card_id: int | None) -> None:
        if staff_card_id is None:
            return

        card = self.db.query(StaffCard).filter(StaffCard.id == staff_card_id).first()
        if not card:
            raise ValueError("El carnet del personal indicado no existe.")

        if card.staff_id != staff_id:
            raise ValueError("El carnet indicado no pertenece al miembro del personal.")

        if not card.is_active:
            raise ValueError("El carnet del personal está inactivo.")

    def has_entry_for_day(self, *, staff_id: int, target_date: date) -> bool:
        count = (
            self.db.query(StaffAttendanceEvent)
            .filter(
                StaffAttendanceEvent.staff_id == staff_id,
                StaffAttendanceEvent.event_type == "entry",
                func.date(StaffAttendanceEvent.event_time) == target_date,
            )
            .count()
        )
        return count > 0

    def create_entry_event(
        self,
        *,
        staff_id: int,
        staff_card_id: int | None,
        event_time: datetime,
        source: str = "scanner",
        notes: str | None = None,
        recorded_by: str | None = None,
    ) -> StaffAttendanceEvent:
        staff = self.db.query(Staff).filter(Staff.id == staff_id).first()
        if not staff:
            raise ValueError("El miembro del personal no existe.")

        self.validate_card_belongs_to_staff(staff_id=staff.id, staff_card_id=staff_card_id)

        if self.has_entry_for_day(staff_id=staff.id, target_date=event_time.date()):
            raise ValueError("El personal ya tiene una entrada registrada en esta fecha.")

        event = StaffAttendanceEvent(
            staff_id=staff.id,
            staff_card_id=staff_card_id,
            center_id=staff.center_id,
            school_year_id=staff.school_year_id,
            event_type="entry",
            status="on_time",
            event_time=event_time,
            source=source,
            notes=notes,
            recorded_by=recorded_by,
        )

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def create_entry_event_by_qr_token(
        self,
        *,
        qr_token: str,
        event_time: datetime,
        source: str = "scanner",
        notes: str | None = None,
        recorded_by: str | None = None,
    ) -> dict:
        card = self.get_card_by_qr_token(qr_token)
        if not card:
            raise ValueError("El QR no corresponde a un carnet de personal válido.")

        staff = self.db.query(Staff).filter(Staff.id == card.staff_id).first()
        if not staff:
            raise ValueError("El personal vinculado al carnet no existe.")

        event = self.create_entry_event(
            staff_id=staff.id,
            staff_card_id=card.id,
            event_time=event_time,
            source=source,
            notes=notes,
            recorded_by=recorded_by,
        )

        return {
            "staff": staff,
            "card": card,
            "event": event,
        }

    def create_exit_event(
        self,
        *,
        staff_id: int,
        staff_card_id: int | None,
        event_time: datetime,
        source: str = "scanner",
        status: str = "normal_exit",
        notes: str | None = None,
        recorded_by: str | None = None,
    ) -> StaffAttendanceEvent:
        staff = self.db.query(Staff).filter(Staff.id == staff_id).first()
        if not staff:
            raise ValueError("El miembro del personal no existe.")

        self.validate_card_belongs_to_staff(staff_id=staff.id, staff_card_id=staff_card_id)

        event = StaffAttendanceEvent(
            staff_id=staff.id,
            staff_card_id=staff_card_id,
            center_id=staff.center_id,
            school_year_id=staff.school_year_id,
            event_type="exit",
            status=status,
            event_time=event_time,
            source=source,
            notes=notes,
            recorded_by=recorded_by,
        )

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event