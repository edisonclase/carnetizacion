from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles, resolve_center_scope
from app.models.student import Student
from app.models.user import User, UserRole
from app.schemas.reports import (
    DailyGroupedReportResponse,
    DailyInstitutionalReportResponse,
    MonthlyInstitutionalReportResponse,
)
from app.services.reporting_service import ReportingService

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/daily-institutional", response_model=DailyInstitutionalReportResponse)
def get_daily_institutional_report(
    center_id: int = Query(...),
    school_year_id: int = Query(...),
    date_value: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
):
    service = ReportingService(db)

    try:
        report = service.get_daily_institutional_report(
            center_id=center_id,
            school_year_id=school_year_id,
            target_date=date_value,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return report


@router.get("/daily-grouped", response_model=DailyGroupedReportResponse)
def get_daily_grouped_report(
    center_id: int = Query(...),
    school_year_id: int = Query(...),
    date_value: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
):
    service = ReportingService(db)

    try:
        report = service.get_daily_grouped_report(
            center_id=center_id,
            school_year_id=school_year_id,
            target_date=date_value,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return report


@router.get("/monthly-institutional", response_model=MonthlyInstitutionalReportResponse)
def get_monthly_institutional_report(
    center_id: int = Query(...),
    school_year_id: int = Query(...),
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db),
):
    service = ReportingService(db)

    try:
        report = service.get_monthly_institutional_report(
            center_id=center_id,
            school_year_id=school_year_id,
            year=year,
            month=month,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return report


@router.get("/students/summary")
def get_students_summary(
    center_id: int | None = Query(default=None),
    school_year_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.SUPER_ADMIN, UserRole.REGISTRO)
    ),
):
    effective_center_id = resolve_center_scope(current_user, center_id)

    base_query = db.query(Student)

    if effective_center_id is not None:
        base_query = base_query.filter(Student.center_id == effective_center_id)

    if school_year_id is not None:
        base_query = base_query.filter(Student.school_year_id == school_year_id)

    total_students = base_query.count()

    gender_query = db.query(
        Student.gender,
        func.count(Student.id),
    )

    if effective_center_id is not None:
        gender_query = gender_query.filter(Student.center_id == effective_center_id)

    if school_year_id is not None:
        gender_query = gender_query.filter(Student.school_year_id == school_year_id)

    gender_rows = (
        gender_query
        .group_by(Student.gender)
        .order_by(Student.gender.asc())
        .all()
    )

    grade_query = db.query(
        Student.grade,
        func.count(Student.id),
    )

    if effective_center_id is not None:
        grade_query = grade_query.filter(Student.center_id == effective_center_id)

    if school_year_id is not None:
        grade_query = grade_query.filter(Student.school_year_id == school_year_id)

    grade_rows = (
        grade_query
        .group_by(Student.grade)
        .order_by(Student.grade.asc())
        .all()
    )

    by_gender = {
        (gender if gender else "No especificado"): count
        for gender, count in gender_rows
    }

    by_grade = {
        (grade if grade else "No especificado"): count
        for grade, count in grade_rows
    }

    return {
        "total_students": total_students,
        "by_gender": by_gender,
        "by_grade": by_grade,
    }