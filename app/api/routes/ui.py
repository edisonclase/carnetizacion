from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from math import ceil

from app.api.deps import get_db
from app.models.card import Card
from app.models.center import Center
from app.models.school_year import SchoolYear
from app.models.student import Student

router = APIRouter(tags=["UI"])

templates = Jinja2Templates(directory="app/ui/templates")


def _normalize_school_year_name(value: str | None) -> str:
    if not value:
        return "-"
    return value.replace("Año Escolar", "").strip()


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
            "center_logo_url": center.logo_url if center and center.logo_url else None,
            "center_primary_color": (
                center.primary_color if center and center.primary_color else "#2563eb"
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
            "phone": center.phone if center and center.phone else None,
            "email": center.email if center and center.email else None,
            "student_full_name": f"{student.first_name} {student.last_name}",
            "student_code": student.student_code,
            "minerd_id": student.minerd_id,
            "grade": student.grade,
            "section": student.section,
            "school_year_name": _normalize_school_year_name(
                school_year.name if school_year else "-"
            ),
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
            "center_primary_color": (
                center.primary_color if center and center.primary_color else "#2563eb"
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
        },
    )

def _chunk_list(items: list, chunk_size: int) -> list[list]:
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


@router.get("/students/cards/print-sheet", response_class=HTMLResponse)
def student_cards_print_sheet(
    request: Request,
    center_id: int,
    school_year_id: int | None = None,
    grade: str | None = None,
    section: str | None = None,
    db: Session = Depends(get_db),
):
    center = db.query(Center).filter(Center.id == center_id).first()
    if not center:
        raise HTTPException(status_code=404, detail="Centro no encontrado.")

    query = db.query(Student).filter(Student.center_id == center_id)

    if school_year_id is not None:
        query = query.filter(Student.school_year_id == school_year_id)

    if grade:
        query = query.filter(Student.grade == grade)

    if section:
        query = query.filter(Student.section == section)

    students = query.order_by(Student.last_name.asc(), Student.first_name.asc()).all()

    if not students:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron estudiantes para los filtros indicados.",
        )

    student_cards = []
    for student in students:
        school_year = (
            db.query(SchoolYear)
            .filter(SchoolYear.id == student.school_year_id)
            .first()
        )

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

        student_cards.append(
            {
                "student_id": student.id,
                "student_full_name": f"{student.first_name} {student.last_name}",
                "student_code": student.student_code,
                "minerd_id": student.minerd_id,
                "grade": student.grade,
                "section": student.section,
                "school_year_name": _normalize_school_year_name(
                    school_year.name if school_year else "-"
                ),
                "student_photo_url": student.photo_path,
                "qr_image_url": qr_image_url,
            }
        )

    cards_per_page = 8
    pages = _chunk_list(student_cards, cards_per_page)

    return templates.TemplateResponse(
        request=request,
        name="student_cards_print_sheet.html",
        context={
            "request": request,
            "pages": pages,
            "center_name": center.name,
            "center_logo_url": center.logo_url,
            "center_primary_color": center.primary_color or "#2563eb",
            "center_accent_color": center.accent_color or "#e2e8f0",
            "center_text_color": center.text_color or "#1e293b",
            "center_background_color": center.background_color or "#ffffff",
            "phone": center.phone,
            "email": center.email,
            "philosophy": center.philosophy or "",
            "mission": center.mission or "",
            "vision": center.vision or "",
            "values": center.values or "",
        },
    )