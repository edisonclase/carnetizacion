from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.card import Card
from app.models.student import Student
from app.schemas.card import CardCreate, CardResponse, CardUpdate

router = APIRouter(prefix="/cards", tags=["Cards"])


@router.post("/", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
def create_card(payload: CardCreate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == payload.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El estudiante indicado no existe.",
        )

    existing_card_code = db.query(Card).filter(Card.card_code == payload.card_code).first()
    if existing_card_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un carnet con ese código.",
        )

    existing_qr_token = db.query(Card).filter(Card.qr_token == payload.qr_token).first()
    if existing_qr_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un carnet con ese token QR.",
        )

    card = Card(
        student_id=payload.student_id,
        card_code=payload.card_code,
        qr_token=payload.qr_token,
        is_active=payload.is_active,
        deactivation_reason=payload.deactivation_reason,
    )

    db.add(card)
    db.commit()
    db.refresh(card)

    return card


@router.get("/", response_model=list[CardResponse])
def list_cards(db: Session = Depends(get_db)):
    cards = db.query(Card).order_by(Card.id.asc()).all()
    return cards


@router.get("/{card_id}", response_model=CardResponse)
def get_card(card_id: int, db: Session = Depends(get_db)):
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carnet no encontrado.",
        )

    return card


@router.put("/{card_id}", response_model=CardResponse)
def update_card(
    card_id: int,
    payload: CardUpdate,
    db: Session = Depends(get_db),
):
    card = db.query(Card).filter(Card.id == card_id).first()
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carnet no encontrado.",
        )

    update_data = payload.model_dump(exclude_unset=True)

    if "card_code" in update_data and update_data["card_code"] != card.card_code:
        existing_card_code = db.query(Card).filter(Card.card_code == update_data["card_code"]).first()
        if existing_card_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un carnet con ese código.",
            )

    if "qr_token" in update_data and update_data["qr_token"] != card.qr_token:
        existing_qr_token = db.query(Card).filter(Card.qr_token == update_data["qr_token"]).first()
        if existing_qr_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un carnet con ese token QR.",
            )

    for field, value in update_data.items():
        setattr(card, field, value)

    db.commit()
    db.refresh(card)

    return card