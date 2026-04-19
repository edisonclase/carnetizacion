import secrets
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.staff import Staff
from app.models.staff_card import StaffCard
from app.schemas.staff_card import StaffCardCreate, StaffCardResponse, StaffCardUpdate

router = APIRouter(prefix="/staff-cards", tags=["Staff Cards"])


def _get_staff_or_404(db: Session, staff_id: int) -> Staff:
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal no encontrado.",
        )
    return staff


def _get_staff_card_or_404(db: Session, card_id: int) -> StaffCard:
    card = db.query(StaffCard).filter(StaffCard.id == card_id).first()
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carnet del personal no encontrado.",
        )
    return card


def _get_by_card_code(db: Session, card_code: str) -> StaffCard | None:
    return db.query(StaffCard).filter(StaffCard.card_code == card_code).first()


def _get_by_qr_token(db: Session, qr_token: str) -> StaffCard | None:
    return db.query(StaffCard).filter(StaffCard.qr_token == qr_token).first()


def _generate_staff_card_code(staff_id: int) -> str:
    return f"STF-{staff_id}-{secrets.token_hex(3).upper()}"


def _generate_qr_token() -> str:
    return secrets.token_urlsafe(24)


@router.post("/auto/{staff_id}", response_model=StaffCardResponse, status_code=status.HTTP_201_CREATED)
def create_staff_card_auto(staff_id: int, db: Session = Depends(get_db)):
    _get_staff_or_404(db, staff_id)

    active_card = (
        db.query(StaffCard)
        .filter(StaffCard.staff_id == staff_id, StaffCard.is_active == True)
        .first()
    )
    if active_card:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este miembro del personal ya tiene un carnet activo.",
        )

    card_code = _generate_staff_card_code(staff_id)
    while _get_by_card_code(db, card_code):
        card_code = _generate_staff_card_code(staff_id)

    qr_token = _generate_qr_token()
    while _get_by_qr_token(db, qr_token):
        qr_token = _generate_qr_token()

    card = StaffCard(
        staff_id=staff_id,
        card_code=card_code,
        qr_token=qr_token,
        is_active=True,
    )

    db.add(card)
    db.commit()
    db.refresh(card)
    return card


@router.post("/", response_model=StaffCardResponse, status_code=status.HTTP_201_CREATED)
def create_staff_card(payload: StaffCardCreate, db: Session = Depends(get_db)):
    _get_staff_or_404(db, payload.staff_id)

    if _get_by_card_code(db, payload.card_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un carnet con ese código.",
        )

    if _get_by_qr_token(db, payload.qr_token):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un carnet con ese QR token.",
        )

    card = StaffCard(
        staff_id=payload.staff_id,
        card_code=payload.card_code,
        qr_token=payload.qr_token,
        expires_at=payload.expires_at,
        is_active=payload.is_active,
    )

    db.add(card)
    db.commit()
    db.refresh(card)
    return card


@router.get("/by-staff/{staff_id}", response_model=list[StaffCardResponse])
def list_staff_cards_by_staff(staff_id: int, db: Session = Depends(get_db)):
    _get_staff_or_404(db, staff_id)

    cards = (
        db.query(StaffCard)
        .filter(StaffCard.staff_id == staff_id)
        .order_by(StaffCard.id.desc())
        .all()
    )
    return cards


@router.get("/{card_id}", response_model=StaffCardResponse)
def get_staff_card(card_id: int, db: Session = Depends(get_db)):
    return _get_staff_card_or_404(db, card_id)


@router.put("/{card_id}", response_model=StaffCardResponse)
def update_staff_card(card_id: int, payload: StaffCardUpdate, db: Session = Depends(get_db)):
    card = _get_staff_card_or_404(db, card_id)

    update_data = payload.model_dump(exclude_unset=True)

    new_card_code = update_data.get("card_code", card.card_code)
    new_qr_token = update_data.get("qr_token", card.qr_token)

    existing_by_code = _get_by_card_code(db, new_card_code)
    if existing_by_code and existing_by_code.id != card.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe otro carnet con ese código.",
        )

    existing_by_qr = _get_by_qr_token(db, new_qr_token)
    if existing_by_qr and existing_by_qr.id != card.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe otro carnet con ese QR token.",
        )

    for field, value in update_data.items():
        setattr(card, field, value)

    db.commit()
    db.refresh(card)
    return card


@router.post("/{card_id}/deactivate", response_model=StaffCardResponse)
def deactivate_staff_card(card_id: int, db: Session = Depends(get_db)):
    card = _get_staff_card_or_404(db, card_id)
    card.is_active = False
    db.commit()
    db.refresh(card)
    return card