from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.center import Center
from app.models.school_year import SchoolYear
from app.schemas.school_year import SchoolYearCreate, SchoolYearResponse, SchoolYearUpdate

router = APIRouter(prefix="/school-years", tags=["School Years"])


@router.post("/", response_model=SchoolYearResponse, status_code=status.HTTP_201_CREATED)
def create_school_year(payload: SchoolYearCreate, db: Session = Depends(get_db)):
    center = db.query(Center).filter(Center.id == payload.center_id).first()
    if not center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El centro educativo indicado no existe.",
        )

    existing_school_year = (
        db.query(SchoolYear)
        .filter(
            SchoolYear.center_id == payload.center_id,
            SchoolYear.name == payload.name,
        )
        .first()
    )
    if existing_school_year:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un año escolar con ese nombre para este centro.",
        )

    school_year = SchoolYear(
        center_id=payload.center_id,
        name=payload.name,
        start_date=payload.start_date,
        end_date=payload.end_date,
        is_active=payload.is_active,
    )

    db.add(school_year)
    db.commit()
    db.refresh(school_year)

    return school_year


@router.get("/", response_model=list[SchoolYearResponse])
def list_school_years(db: Session = Depends(get_db)):
    school_years = db.query(SchoolYear).order_by(SchoolYear.id.asc()).all()
    return school_years


@router.get("/{school_year_id}", response_model=SchoolYearResponse)
def get_school_year(school_year_id: int, db: Session = Depends(get_db)):
    school_year = db.query(SchoolYear).filter(SchoolYear.id == school_year_id).first()
    if not school_year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Año escolar no encontrado.",
        )

    return school_year


@router.put("/{school_year_id}", response_model=SchoolYearResponse)
def update_school_year(
    school_year_id: int,
    payload: SchoolYearUpdate,
    db: Session = Depends(get_db),
):
    school_year = db.query(SchoolYear).filter(SchoolYear.id == school_year_id).first()
    if not school_year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Año escolar no encontrado.",
        )

    update_data = payload.model_dump(exclude_unset=True)

    if "name" in update_data and update_data["name"] != school_year.name:
        existing_school_year = (
            db.query(SchoolYear)
            .filter(
                SchoolYear.center_id == school_year.center_id,
                SchoolYear.name == update_data["name"],
            )
            .first()
        )
        if existing_school_year:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un año escolar con ese nombre para este centro.",
            )

    for field, value in update_data.items():
        setattr(school_year, field, value)

    db.commit()
    db.refresh(school_year)

    return school_year