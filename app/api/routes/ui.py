from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.card import Card
from app.models.center import Center
from app.models.school_year import SchoolYear
from app.models.student import Student

router = APIRouter(tags=["UI"])

templates = Jinja2Templates(directory="app/ui/templates")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"request": request},
    )


@router.get("/students/{student_id}/card/front", response_class=HTMLResponse)
def student_card_front(
    request: Request,
    student_id: int,
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado.")

    center = db.query(Center).filter(Center.id == student.center_id).first()
    school_year = db.query(SchoolYear).filter(
        SchoolYear.id == student.school_year_id
    ).first()

    card = (
        db.query(Card)
        .filter(Card.student_id == student.id, Card.is_active == True)
        .order_by(Card.id.desc())
        .first()
    )

    if not card:
        card = (
            db.query(Card)
            .filter(Card.student_id == student.id)
            .order_by(Card.id.desc())
            .first()
        )

    qr_image_url = None
    if card and card.qr_token:
        qr_image_url = str(request.url_for("get_card_qr", card_id=card.id))

    return templates.TemplateResponse(
        request=request,
        name="student_card_front.html",
        context={
            "request": request,
            "center_name": center.name if center else "Centro educativo",
            "center_code": center.code if center else None,
            "center_logo_url": center.logo_url if center and center.logo_url else None,
            "center_letterhead_url": (
                center.letterhead_url if center and center.letterhead_url else None
            ),
            "center_primary_color": (
                center.primary_color if center and center.primary_color else "#2563eb"
            ),
            "center_secondary_color": (
                center.secondary_color if center and center.secondary_color else "#1d4ed8"
            ),
            "center_accent_color": (
                center.accent_color if center and center.accent_color else "#e2e8f0"
            ),
            "center_text_color": (
                center.text_color if center and center.text_color else "#1e293b"
            ),
            "center_background_color": (
                center.background_color if center and center.background_color else "#ffffff"
            ),
            "address": center.address if center and center.address else None,
            "phone": center.phone if center and center.phone else None,
            "district_name": (
                center.district_name if center and center.district_name else None
            ),
            "management_code": (
                center.management_code if center and center.management_code else None
            ),
            "student_full_name": f"{student.first_name} {student.last_name}",
            "student_code": student.student_code,
            "minerd_id": student.minerd_id,
            "grade": student.grade,
            "section": student.section,
            "school_year_name": school_year.name if school_year else "-",
            "student_photo_url": student.photo_path,
            "qr_image_url": qr_image_url,
        },
    )


@router.get("/students/{student_id}/card/back", response_class=HTMLResponse)
def student_card_back(
    request: Request,
    student_id: int,
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado.")

    center = db.query(Center).filter(Center.id == student.center_id).first()

    return templates.TemplateResponse(
        request=request,
        name="student_card_back.html",
        context={
            "request": request,
            "center_name": center.name if center else "Centro educativo",
            "center_code": center.code if center else None,
            "center_logo_url": center.logo_url if center and center.logo_url else None,
            "center_letterhead_url": (
                center.letterhead_url if center and center.letterhead_url else None
            ),
            "center_primary_color": (
                center.primary_color if center and center.primary_color else "#2563eb"
            ),
            "center_secondary_color": (
                center.secondary_color if center and center.secondary_color else "#1d4ed8"
            ),
            "center_accent_color": (
                center.accent_color if center and center.accent_color else "#e2e8f0"
            ),
            "center_text_color": (
                center.text_color if center and center.text_color else "#1e293b"
            ),
            "center_background_color": (
                center.background_color if center and center.background_color else "#ffffff"
            ),
            "philosophy": (
                center.philosophy
                if center and center.philosophy
                else "Formar ciudadanos íntegros, críticos y comprometidos con su comunidad."
            ),
            "mission": (
                center.mission
                if center and center.mission
                else "Ofrecer una educación de calidad con enfoque humano, técnico y ético."
            ),
            "vision": (
                center.vision
                if center and center.vision
                else "Ser un centro educativo modelo que ofrezca un servicio de alta calidad."
            ),
            "values": (
                center.values
                if center and center.values
                else "Respeto, disciplina, responsabilidad, servicio y honestidad."
            ),
            "motto": center.motto if center and center.motto else None,
            "address": center.address if center and center.address else None,
            "phone": center.phone if center and center.phone else None,
            "email": center.email if center and center.email else None,
            "district_name": (
                center.district_name if center and center.district_name else None
            ),
            "management_code": (
                center.management_code if center and center.management_code else None
            ),
        },
    )