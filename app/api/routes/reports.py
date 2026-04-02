from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.reports import (
    DailyGroupedReportResponse,
    DailyInstitutionalReportResponse,
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