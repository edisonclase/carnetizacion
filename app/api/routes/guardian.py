from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, require_roles, resolve_center_scope
from app.models.guardian import Guardian
from app.models.student import Student
from app.models.user import User, UserRole
from app.schemas.guardian import GuardianCreate, GuardianResponse, GuardianUpdate

router = APIRouter(prefix="/guardians", tags=["Guardians"])


def _get_student_or_404(db: Session, student_id: int) -> Student:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El estudiante indicado no existe.",
        )
    return student


def _get_guardian_or_404(db: Session, guardian_id: int) -> Guardian:
    guardian = db.query(Guardian).filter(Guardian.id == guardian_id).first()
    if not guardian:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tutor no encontrado.",
        )
    return guardian


def _get_guardian_student_or_404(db: Session, guardian: Guardian) -> Student:
    student = db.query(Student).filter(Student.id == guardian.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El estudiante asociado al tutor no existe.",
        )
    return student


@router.post("/", response_model=GuardianResponse, status_code=status.HTTP_201_CREATED)
def create_guardian(
    payload: GuardianCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.REGISTRO)),
):
    student = _get_student_or_404(db, payload.student_id)
    resolve_center_scope(current_user, student.center_id)

    if payload.is_primary:
        existing_primary = (
            db.query(Guardian)
            .filter(
                Guardian.student_id == payload.student_id,
                Guardian.is_primary == True,
                Guardian.is_active == True,
            )
            .first()
        )
        if existing_primary:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un tutor principal activo para este estudiante.",
            )

    guardian = Guardian(
        student_id=payload.student_id,
        full_name=payload.full_name,
        relationship_type=payload.relationship_type,
        phone=payload.phone,
        whatsapp=payload.whatsapp,
        email=payload.email,
        is_primary=payload.is_primary,
        is_active=payload.is_active,
    )

    db.add(guardian)
    db.commit()
    db.refresh(guardian)

    return guardian


@router.get("/", response_model=list[GuardianResponse])
def list_guardians(
    student_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.SUPER_ADMIN, UserRole.REGISTRO, UserRole.CONSULTA)
    ),
):
    query = db.query(Guardian).join(Student, Guardian.student_id == Student.id)

    if current_user.role != UserRole.SUPER_ADMIN:
        query = query.filter(Student.center_id == current_user.center_id)

    if student_id is not None:
        student = _get_student_or_404(db, student_id)
        resolve_center_scope(current_user, student.center_id)
        query = query.filter(Guardian.student_id == student_id)

    guardians = query.order_by(Guardian.id.asc()).all()
    return guardians


@router.get("/{guardian_id}", response_model=GuardianResponse)
def get_guardian(
    guardian_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.SUPER_ADMIN, UserRole.REGISTRO, UserRole.CONSULTA)
    ),
):
    guardian = _get_guardian_or_404(db, guardian_id)
    student = _get_guardian_student_or_404(db, guardian)
    resolve_center_scope(current_user, student.center_id)

    return guardian


@router.put("/{guardian_id}", response_model=GuardianResponse)
def update_guardian(
    guardian_id: int,
    payload: GuardianUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.SUPER_ADMIN, UserRole.REGISTRO)),
):
    guardian = _get_guardian_or_404(db, guardian_id)
    student = _get_guardian_student_or_404(db, guardian)
    resolve_center_scope(current_user, student.center_id)

    update_data = payload.model_dump(exclude_unset=True)

    new_is_primary = update_data.get("is_primary")
    if new_is_primary is True and guardian.is_primary is not True:
        existing_primary = (
            db.query(Guardian)
            .filter(
                Guardian.student_id == guardian.student_id,
                Guardian.is_primary == True,
                Guardian.is_active == True,
                Guardian.id != guardian.id,
            )
            .first()
        )
        if existing_primary:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe otro tutor principal activo para este estudiante.",
            )

    for field, value in update_data.items():
        setattr(guardian, field, value)

    db.commit()
    db.refresh(guardian)

    return guardian