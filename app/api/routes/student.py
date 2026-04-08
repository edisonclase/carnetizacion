from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.card import Card
from app.models.center import Center
from app.models.guardian import Guardian
from app.models.school_year import SchoolYear
from app.models.student import Student
from app.schemas.student import (
    StudentCreate,
    StudentRegisterRequest,
    StudentRegisterResponse,
    StudentResponse,
    StudentUpdate,
)

router = APIRouter(prefix="/students", tags=["Students"])


def _get_center_or_404(db: Session, center_id: int) -> Center:
    center = db.query(Center).filter(Center.id == center_id).first()
    if not center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El centro educativo indicado no existe.",
        )
    return center


def _get_school_year_or_404(db: Session, center_id: int, school_year_id: int) -> SchoolYear:
    school_year = (
        db.query(SchoolYear)
        .filter(
            SchoolYear.id == school_year_id,
            SchoolYear.center_id == center_id,
        )
        .first()
    )
    if not school_year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El año escolar indicado no existe para este centro.",
        )
    return school_year


def _student_code_exists(
    db: Session,
    center_id: int,
    school_year_id: int,
    student_code: str,
    exclude_student_id: int | None = None,
) -> bool:
    query = db.query(Student).filter(
        Student.center_id == center_id,
        Student.school_year_id == school_year_id,
        Student.student_code == student_code,
    )

    if exclude_student_id is not None:
        query = query.filter(Student.id != exclude_student_id)

    return db.query(query.exists()).scalar()


def _generate_card_code(student: Student) -> str:
    return f"CARD-{student.center_id}-{student.school_year_id}-{student.student_code}-{student.id}"


def _generate_qr_token() -> str:
    return uuid4().hex


def _create_card_for_student(db: Session, student: Student) -> Card:
    card_code = _generate_card_code(student)
    qr_token = _generate_qr_token()

    existing_card_code = db.query(Card).filter(Card.card_code == card_code).first()
    if existing_card_code:
        card_code = f"{card_code}-{uuid4().hex[:6].upper()}"

    existing_qr_token = db.query(Card).filter(Card.qr_token == qr_token).first()
    while existing_qr_token:
        qr_token = _generate_qr_token()
        existing_qr_token = db.query(Card).filter(Card.qr_token == qr_token).first()

    card = Card(
        student_id=student.id,
        card_code=card_code,
        qr_token=qr_token,
        is_active=True,
        deactivation_reason=None,
    )

    db.add(card)
    db.flush()
    db.refresh(card)
    return card


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    _get_center_or_404(db, payload.center_id)
    _get_school_year_or_404(db, payload.center_id, payload.school_year_id)

    if _student_code_exists(
        db=db,
        center_id=payload.center_id,
        school_year_id=payload.school_year_id,
        student_code=payload.student_code,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un estudiante con ese código en este centro y año escolar.",
        )

    student = Student(
        center_id=payload.center_id,
        school_year_id=payload.school_year_id,
        student_code=payload.student_code,
        minerd_id=payload.minerd_id,
        first_name=payload.first_name,
        last_name=payload.last_name,
        birth_date=payload.birth_date,
        gender=payload.gender,
        grade=payload.grade,
        section=payload.section,
        photo_path=payload.photo_path,
        is_active=payload.is_active,
    )

    db.add(student)
    db.commit()
    db.refresh(student)

    return student


@router.post(
    "/with-guardian-and-card",
    response_model=StudentRegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_student_with_guardian_and_card(
    payload: StudentRegisterRequest,
    db: Session = Depends(get_db),
):
    _get_center_or_404(db, payload.center_id)
    _get_school_year_or_404(db, payload.center_id, payload.school_year_id)

    if _student_code_exists(
        db=db,
        center_id=payload.center_id,
        school_year_id=payload.school_year_id,
        student_code=payload.student_code,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un estudiante con ese código en este centro y año escolar.",
        )

    try:
        student = Student(
            center_id=payload.center_id,
            school_year_id=payload.school_year_id,
            student_code=payload.student_code,
            minerd_id=payload.minerd_id,
            first_name=payload.first_name,
            last_name=payload.last_name,
            birth_date=payload.birth_date,
            gender=payload.gender,
            grade=payload.grade,
            section=payload.section,
            photo_path=payload.photo_path,
            is_active=payload.is_active,
        )
        db.add(student)
        db.flush()
        db.refresh(student)

        guardian = Guardian(
            student_id=student.id,
            full_name=payload.guardian.full_name,
            relationship_type=payload.guardian.relationship_type,
            phone=payload.guardian.phone,
            whatsapp=payload.guardian.whatsapp,
            email=payload.guardian.email,
            is_primary=True,
            is_active=True,
        )
        db.add(guardian)
        db.flush()
        db.refresh(guardian)

        card = _create_card_for_student(db, student)

        db.commit()

        db.refresh(student)
        db.refresh(guardian)
        db.refresh(card)

        return StudentRegisterResponse(
            student=student,
            guardian=guardian,
            card=card,
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error al registrar el estudiante, tutor y carnet.",
        )


@router.get("/", response_model=list[StudentResponse])
def list_students(db: Session = Depends(get_db)):
    students = db.query(Student).order_by(Student.id.asc()).all()
    return students


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado.",
        )

    return student


@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: int,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Estudiante no encontrado.",
        )

    update_data = payload.model_dump(exclude_unset=True)

    if "student_code" in update_data and update_data["student_code"] != student.student_code:
        if _student_code_exists(
            db=db,
            center_id=student.center_id,
            school_year_id=student.school_year_id,
            student_code=update_data["student_code"],
            exclude_student_id=student.id,
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un estudiante con ese código en este centro y año escolar.",
            )

    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)

    return student