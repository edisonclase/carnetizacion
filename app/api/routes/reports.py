from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
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
from app.services.report_pdf_service import build_report_pdf
from app.services.reporting_service import ReportingService

router = APIRouter(prefix="/reports", tags=["Reports"])


def _reporting_user_dependency():
    return require_roles(
        UserRole.SUPER_ADMIN,
        UserRole.ADMIN_CENTRO,
        UserRole.CONSULTA,
    )


def _safe_filename(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value.strip())
    return cleaned.strip("_") or "reporte"


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


@router.get("/print/global.pdf")
def get_printable_global_pdf(
    request: Request,
    center_id: int = Query(...),
    school_year_id: int = Query(...),
    date_value: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(_reporting_user_dependency()),
):
    service = ReportingService(db)
    effective_center_id = resolve_center_scope(current_user, center_id)

    try:
        report = service.get_printable_center_full_report(
            center_id=effective_center_id,
            school_year_id=school_year_id,
            target_date=date_value,
        )
        context = service.build_daily_pdf_context(
            center_id=effective_center_id,
            school_year_id=school_year_id,
            target_date=date_value,
            rows=report["students"],
            total_present=report["totals"]["present"]["total"],
            total_late=report["totals"]["late"]["total"],
            total_absent=report["totals"]["absent"]["total"],
            total_with_excuse=report["totals"]["excuse"]["total"],
            report_title="Reporte global del centro",
        )
        pdf_bytes = build_report_pdf(
            template_name="daily_report.html",
            context=context,
            base_url=str(request.base_url),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    filename = f"{_safe_filename(context['center_name'])}_global_{date_value.isoformat()}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.get("/print/by-course.pdf")
def get_printable_course_pdf(
    request: Request,
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
        report = service.get_printable_course_report(
            center_id=effective_center_id,
            school_year_id=school_year_id,
            target_date=date_value,
            grade=grade,
            section=section,
        )
        title = f"Reporte por curso - {grade}" + (f" Sección {section}" if section else "")
        context = service.build_daily_pdf_context(
            center_id=effective_center_id,
            school_year_id=school_year_id,
            target_date=date_value,
            rows=report["students"],
            total_present=report["totals"]["present"]["total"],
            total_late=report["totals"]["late"]["total"],
            total_absent=report["totals"]["absent"]["total"],
            total_with_excuse=report["totals"]["excuse"]["total"],
            report_title=title,
        )
        pdf_bytes = build_report_pdf(
            template_name="daily_report.html",
            context=context,
            base_url=str(request.base_url),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    filename = f"curso_{_safe_filename(grade)}_{date_value.isoformat()}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.get("/print/by-section.pdf")
def get_printable_section_pdf(
    request: Request,
    center_id: int = Query(...),
    school_year_id: int = Query(...),
    section: str = Query(...),
    date_value: date = Query(..., alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(_reporting_user_dependency()),
):
    service = ReportingService(db)
    effective_center_id = resolve_center_scope(current_user, center_id)

    try:
        report = service.get_printable_section_report(
            center_id=effective_center_id,
            school_year_id=school_year_id,
            target_date=date_value,
            section=section,
        )
        context = service.build_daily_pdf_context(
            center_id=effective_center_id,
            school_year_id=school_year_id,
            target_date=date_value,
            rows=report["students"],
            total_present=report["totals"]["present"]["total"],
            total_late=report["totals"]["late"]["total"],
            total_absent=report["totals"]["absent"]["total"],
            total_with_excuse=report["totals"]["excuse"]["total"],
            report_title=f"Reporte por sección - {section}",
        )
        pdf_bytes = build_report_pdf(
            template_name="daily_report.html",
            context=context,
            base_url=str(request.base_url),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    filename = f"seccion_{_safe_filename(section)}_{date_value.isoformat()}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.get("/print/by-multi-course.pdf")
def get_printable_multi_course_pdf(
    request: Request,
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
        report = service.get_printable_multi_course_report(
            center_id=effective_center_id,
            school_year_id=school_year_id,
            target_date=date_value,
            grades=grades,
        )
        title = "Reporte por varios cursos - " + ", ".join(report["grades"])
        context = service.build_daily_pdf_context(
            center_id=effective_center_id,
            school_year_id=school_year_id,
            target_date=date_value,
            rows=report["students"],
            total_present=report["totals"]["present"]["total"],
            total_late=report["totals"]["late"]["total"],
            total_absent=report["totals"]["absent"]["total"],
            total_with_excuse=report["totals"]["excuse"]["total"],
            report_title=title,
        )
        pdf_bytes = build_report_pdf(
            template_name="daily_report.html",
            context=context,
            base_url=str(request.base_url),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    filename = f"multi_curso_{date_value.isoformat()}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.get("/print/excuses.pdf")
def get_printable_excuses_pdf(
    request: Request,
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
        report = service.get_printable_excuses_report(
            center_id=effective_center_id,
            school_year_id=school_year_id,
            target_date=date_value,
            grade=grade,
            section=section,
        )
        title = "Reporte de excusas"
        if grade:
            title += f" - {grade}"
        if section:
            title += f" Sección {section}"

        context = service.build_daily_pdf_context(
            center_id=effective_center_id,
            school_year_id=school_year_id,
            target_date=date_value,
            rows=report["students"],
            total_present=0,
            total_late=0,
            total_absent=0,
            total_with_excuse=report["total_students_with_excuse"],
            report_title=title,
        )
        pdf_bytes = build_report_pdf(
            template_name="daily_report.html",
            context=context,
            base_url=str(request.base_url),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    filename = f"excusas_{date_value.isoformat()}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )