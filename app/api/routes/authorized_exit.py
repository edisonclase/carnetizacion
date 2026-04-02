from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.authorized_exit import AuthorizedExit
from app.models.student import Student
from app.schemas.authorized_exit import (
    AuthorizedExitCreate,
    AuthorizedExitResponse,
)

router = APIRouter(
    prefix="/authorized-exits",
    tags=["Authorized Exits"],
)


@router.post("/", response_model=AuthorizedExitResponse, status_code=status.HTTP_201_CREATED)
def create_authorized_exit(
    payload: AuthorizedExitCreate,
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == payload.student_id).first()

    if not student:
        raise HTTPException(
            status_code=404,
            detail="El estudiante no existe.",
        )

    record = AuthorizedExit(
        student_id=payload.student_id,
        authorized_by=payload.authorized_by,
        reason=payload.reason,
        authorized_at=payload.authorized_at,
        notes=payload.notes,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


@router.get("/", response_model=list[AuthorizedExitResponse])
def list_authorized_exits(db: Session = Depends(get_db)):
    return db.query(AuthorizedExit).all()