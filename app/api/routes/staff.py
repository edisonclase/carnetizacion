from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.center import Center
from app.models.school_year import SchoolYear
from app.models.staff import Staff
from app.schemas.staff import StaffCreate, StaffResponse, StaffUpdate

router = APIRouter(prefix="/staff", tags=["Staff"])


def _get_staff_or_404(db: Session, staff_id: int) -> Staff:
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personal no encontrado.",
        )
    return staff


def _get_center_or_404(db: Session, center_id: int) -> Center:
    center = db.query(Center).filter(Center.id == center_id).first()
    if not center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Centro no encontrado.",
        )
    return center


def _validate_school_year_if_present(db: Session, school_year_id: int | None) -> None:
    if school_year_id is None:
        return

    school_year = db.query(SchoolYear).filter(SchoolYear.id == school_year_id).first()
    if not school_year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Año escolar no encontrado.",
        )


def _get_staff_by_center_and_code(db: Session, center_id: int, staff_code: str) -> Staff | None:
    return (
        db.query(Staff)
        .filter(
            Staff.center_id == center_id,
            Staff.staff_code == staff_code,
        )
        .first()
    )


@router.post("/", response_model=StaffResponse, status_code=status.HTTP_201_CREATED)
def create_staff(payload: StaffCreate, db: Session = Depends(get_db)):
    _get_center_or_404(db, payload.center_id)
    _validate_school_year_if_present(db, payload.school_year_id)

    existing_staff = _get_staff_by_center_and_code(
        db=db,
        center_id=payload.center_id,
        staff_code=payload.staff_code,
    )
    if existing_staff:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un miembro del personal con ese código en este centro.",
        )

    staff = Staff(
        center_id=payload.center_id,
        school_year_id=payload.school_year_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        staff_code=payload.staff_code,
        national_id=payload.national_id,
        photo_path=payload.photo_path,
        staff_group=payload.staff_group,
        staff_position=payload.staff_position,
        department=payload.department,
        is_active=payload.is_active,
    )

    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


@router.get("/", response_model=list[StaffResponse])
def list_staff(
    center_id: int | None = Query(default=None),
    school_year_id: int | None = Query(default=None),
    staff_group: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Staff)

    if center_id is not None:
        query = query.filter(Staff.center_id == center_id)

    if school_year_id is not None:
        query = query.filter(Staff.school_year_id == school_year_id)

    if staff_group is not None:
        query = query.filter(Staff.staff_group == staff_group.strip().lower())

    if is_active is not None:
        query = query.filter(Staff.is_active == is_active)

    staff_members = (
        query.order_by(Staff.last_name.asc(), Staff.first_name.asc())
        .all()
    )
    return staff_members


@router.get("/{staff_id}", response_model=StaffResponse)
def get_staff(staff_id: int, db: Session = Depends(get_db)):
    return _get_staff_or_404(db, staff_id)


@router.put("/{staff_id}", response_model=StaffResponse)
def update_staff(staff_id: int, payload: StaffUpdate, db: Session = Depends(get_db)):
    staff = _get_staff_or_404(db, staff_id)

    update_data = payload.model_dump(exclude_unset=True)

    new_center_id = update_data.get("center_id", staff.center_id)
    new_staff_code = update_data.get("staff_code", staff.staff_code)
    new_school_year_id = update_data.get("school_year_id", staff.school_year_id)

    _get_center_or_404(db, new_center_id)
    _validate_school_year_if_present(db, new_school_year_id)

    if new_center_id != staff.center_id or new_staff_code != staff.staff_code:
        existing_staff = _get_staff_by_center_and_code(
            db=db,
            center_id=new_center_id,
            staff_code=new_staff_code,
        )
        if existing_staff and existing_staff.id != staff.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro miembro del personal con ese código en este centro.",
            )

    for field, value in update_data.items():
        setattr(staff, field, value)

    db.commit()
    db.refresh(staff)
    return staff


@router.delete("/{staff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_staff(staff_id: int, db: Session = Depends(get_db)):
    staff = _get_staff_or_404(db, staff_id)
    db.delete(staff)
    db.commit()
    return None