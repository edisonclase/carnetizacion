from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.center import Center
from app.schemas.center import CenterCreate, CenterResponse, CenterUpdate

router = APIRouter(prefix="/centers", tags=["Centers"])


@router.post("/", response_model=CenterResponse, status_code=status.HTTP_201_CREATED)
def create_center(payload: CenterCreate, db: Session = Depends(get_db)):
    existing_center = db.query(Center).filter(Center.code == payload.code).first()
    if existing_center:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un centro con ese código.",
        )

    center = Center(
        name=payload.name,
        code=payload.code,
        logo_url=payload.logo_url,
        letterhead_url=payload.letterhead_url,
        primary_color=payload.primary_color,
        secondary_color=payload.secondary_color,
        accent_color=payload.accent_color,
        text_color=payload.text_color,
        background_color=payload.background_color,
        philosophy=payload.philosophy,
        mission=payload.mission,
        vision=payload.vision,
        values=payload.values,
        motto=payload.motto,
        address=payload.address,
        phone=payload.phone,
        email=payload.email,
        district_name=payload.district_name,
        management_code=payload.management_code,
        is_active=payload.is_active,
    )

    db.add(center)
    db.commit()
    db.refresh(center)

    return center


@router.get("/", response_model=list[CenterResponse])
def list_centers(db: Session = Depends(get_db)):
    centers = db.query(Center).order_by(Center.id.asc()).all()
    return centers


@router.get("/{center_id}", response_model=CenterResponse)
def get_center(center_id: int, db: Session = Depends(get_db)):
    center = db.query(Center).filter(Center.id == center_id).first()
    if not center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Centro no encontrado.",
        )

    return center


@router.put("/{center_id}", response_model=CenterResponse)
def update_center(center_id: int, payload: CenterUpdate, db: Session = Depends(get_db)):
    center = db.query(Center).filter(Center.id == center_id).first()
    if not center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Centro no encontrado.",
        )

    if payload.code is not None and payload.code != center.code:
        existing_center = db.query(Center).filter(Center.code == payload.code).first()
        if existing_center:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro centro con ese código.",
            )

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(center, field, value)

    db.commit()
    db.refresh(center)

    return center