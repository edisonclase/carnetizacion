from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.center import Center
from app.models.school_year import SchoolYear
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)):
    center = db.query(Center).filter(Center.id == payload.center_id).first()
    if not center:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El centro educativo indicado no existe.",
        )

    school_year = (
        db.query(SchoolYear)
        .filter(
            SchoolYear.id == payload.school_year_id,
            SchoolYear.center_id == payload.center_id,
        )
        .first()
    )
    if not school_year:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El año escolar indicado no existe para este centro.",
        )

    existing_student = (
        db.query(Student)
        .filter(
            Student.center_id == payload.center_id,
            Student.school_year_id == payload.school_year_id,
            Student.student_code == payload.student_code,
        )
        .first()
    )
    if existing_student:
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
        existing_student = (
            db.query(Student)
            .filter(
                Student.center_id == student.center_id,
                Student.school_year_id == student.school_year_id,
                Student.student_code == update_data["student_code"],
            )
            .first()
        )
        if existing_student:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un estudiante con ese código en este centro y año escolar.",
            )

    for field, value in update_data.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)

    return student