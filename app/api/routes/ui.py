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

    # Busca primero un carnet activo
    card = (
        db.query(Card)
        .filter(Card.student_id == student.id, Card.is_active == True)
        .order_by(Card.id.desc())
        .first()
    )

    # Si no encuentra activo, intenta tomar el último carnet existente del estudiante
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
            "center_logo_url": "/static/logo.png",
            "center_primary_color": "#2563eb",
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
            "center_logo_url": "/static/logo.png",
            "center_primary_color": "#2563eb",
            "philosophy": "Formar ciudadanos íntegros, críticos y comprometidos con su comunidad.",
            "mission": "Ofrecer una educación de calidad con enfoque humano, técnico y ético.",
            "values": "Respeto, disciplina, responsabilidad, servicio y honestidad.",
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
            "center_primary_color": "#2563eb",
            "philosophy": "Formar ciudadanos íntegros, críticos y comprometidos con su comunidad.",
            "mission": "Ofrecer una educación de calidad con enfoque humano, técnico y ético.",
            "values": "Respeto, disciplina, responsabilidad, servicio y honestidad.",
        },
    )