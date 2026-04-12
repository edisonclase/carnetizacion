from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_roles, resolve_center_scope
from app.models.user import User, UserRole
from app.schemas.reports import (
    DailyGroupedReportResponse,
    DailyInstitutionalReportResponse,
    MonthlyInstitutionalReportResponse,
    PrintableCourseReportResponse,
    PrintableExcusesReportResponse,
    PrintableGlobalReportResponse,
    PrintableMultiCourseReportResponse,
    StudentsSummaryResponse,
)
from app.services.reporting_service import ReportingService

router = APIRouter(prefix="/reports", tags=["Reports"])


def _reporting_user_dependency():
    return require_roles(
        UserRole.SUPER_ADMIN,
        UserRole.ADMIN_CENTRO,
        UserRole.CONSULTA,
    )


@router.get("/daily-institutional", response_model=DailyInstitutionalReportResponse)
def get_daily_institutional_report(
    center_id: int = Query(...),
    school_year_id: int = Query(...),
    date_value: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(_reporting_user_dependency()),
):
    service = ReportingService(db)
    effective_center_id = resolve_center_scope(current_user, center_id)

    try:
        report = service.get_daily_institutional_report(
            center_id=effective_center_id,
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
    current_user: User = Depends(_reporting_user_dependency()),
):
    service = ReportingService(db)
    effective_center_id = resolve_center_scope(current_user, center_id)

    try:
        report = service.get_daily_grouped_report(
            center_id=effective_center_id,
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
    current_user: User = Depends(_reporting_user_dependency()),
):
    service = ReportingService(db)
    effective_center_id = resolve_center_scope(current_user, center_id)

    try:
        report = service.get_monthly_institutional_report(
            center_id=effective_center_id,
            school_year_id=school_year_id,
            year=year,
            month=month,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return report


@router.get("/students/summary", response_model=StudentsSummaryResponse)
def get_students_summary(
    center_id: int | None = Query(default=None),
    school_year_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(_reporting_user_dependency()),
):
    service = ReportingService(db)
    effective_center_id = resolve_center_scope(current_user, center_id)

    return service.get_students_summary(
        center_id=effective_center_id,
        school_year_id=school_year_id,
    )


@router.get("/print/global-data", response_model=PrintableGlobalReportResponse)
def get_printable_global_report(
    center_id: int = Query(...),
    school_year_id: int = Query(...),
    date_value: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(_reporting_user_dependency()),
):
    service = ReportingService(db)
    effective_center_id = resolve_center_scope(current_user, center_id)

    try:
        return service.get_printable_global_report(
            center_id=effective_center_id,
            school_year_id=school_year_id,
            target_date=date_value,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/print/by-course-data", response_model=PrintableCourseReportResponse)
def get_printable_course_report(
    center_id: int = Query(...),
    school_year_id: int = Query(...),
    grade: str = Query(...),
    section: str | None = Query(default=None),
    date_value: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(_reporting_user_dependency()),
):
    service = ReportingService(db)
    effective_center_id = resolve_center_scope(current_user, center_id)

    try:
        return service.get_printable_course_report(
            center_id=effective_center_id,
            school_year_id=school_year_id,
            target_date=date_value,
            grade=grade,
            section=section,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/print/by-multi-course-data", response_model=PrintableMultiCourseReportResponse)
def get_printable_multi_course_report(
    center_id: int = Query(...),
    school_year_id: int = Query(...),
    grades: list[str] = Query(...),
    date_value: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(_reporting_user_dependency()),
):
    service = ReportingService(db)
    effective_center_id = resolve_center_scope(current_user, center_id)

    try:
        return service.get_printable_multi_course_report(
            center_id=effective_center_id,
            school_year_id=school_year_id,
            target_date=date_value,
            grades=grades,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/print/excuses-by-course-data", response_model=PrintableExcusesReportResponse)
def get_printable_excuses_report(
    center_id: int = Query(...),
    school_year_id: int = Query(...),
    date_value: date = Query(..., alias="date"),
    grade: str | None = Query(default=None),
    section: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(_reporting_user_dependency()),
):
    service = ReportingService(db)
    effective_center_id = resolve_center_scope(current_user, center_id)

    try:
        return service.get_printable_excuses_report(
            center_id=effective_center_id,
            school_year_id=school_year_id,
            target_date=date_value,
            grade=grade,
            section=section,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc