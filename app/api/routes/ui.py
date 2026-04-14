from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.card import Card
from app.models.center import Center
from app.models.school_year import SchoolYear
from app.models.student import Student
from app.services.pdf_service import render_pdf_from_html

router = APIRouter(tags=["UI"])

templates = Jinja2Templates(directory="app/ui/templates")


CARD_DESIGN_TEMPLATES = {
    "classic_green_v1": {
        "front": "student_card_front.html",
        "back": "student_card_back.html",
    },
    "prestige_clean_v1": {
        "front": "student_card_front.html",
        "back": "student_card_back.html",
    },
    "nova_modern_v1": {
        "front": "student_card_front.html",
        "back": "student_card_back.html",
    },
}


def _normalize_school_year_name(value: str | None) -> str:
    if not value:
        return "-"
    return value.replace("Año Escolar", "").strip()


def _get_center_or_404(db: Session, center_id: int) -> Center:
    center = db.query(Center).filter(Center.id == center_id).first()
    if not center:
        raise HTTPException(status_code=404, detail="Centro no encontrado.")
    return center


def _get_student_or_404(db: Session, student_id: int) -> Student:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado.")
    return student


def _get_latest_card_for_student(db: Session, student_id: int) -> Card | None:
    card = (
        db.query(Card)
        .filter(Card.student_id == student_id, Card.is_active == True)
        .order_by(Card.id.desc())
        .first()
    )

    if card:
        return card

    return (
        db.query(Card)
        .filter(Card.student_id == student_id)
        .order_by(Card.id.desc())
        .first()
    )


def _resolve_card_design_templates(center: Center | None) -> dict:
    design_key = (
        center.card_design_key
        if center and getattr(center, "card_design_key", None)
        else "classic_green_v1"
    )
    return CARD_DESIGN_TEMPLATES.get(
        design_key,
        CARD_DESIGN_TEMPLATES["classic_green_v1"],
    )


def _resolve_card_text(
    center: Center | None,
    full_text: str | None,
    short_text: str | None,
    fallback_text: str,
    prefer_full: bool,
) -> str:
    if prefer_full and full_text:
        return full_text
    if short_text:
        return short_text
    if full_text:
        return full_text
    return fallback_text


def _build_center_theme(center: Center | None) -> dict:
    prefer_full_identity = (
        bool(center.show_full_card_identity)
        if center and hasattr(center, "show_full_card_identity")
        else True
    )

    mission = _resolve_card_text(
        center=center,
        full_text=center.mission if center else None,
        short_text=center.card_mission if center else None,
        fallback_text="Ofrecer una educación de calidad con enfoque humano, técnico y ético.",
        prefer_full=prefer_full_identity,
    )
    vision = _resolve_card_text(
        center=center,
        full_text=center.vision if center else None,
        short_text=center.card_vision if center else None,
        fallback_text="Ser un centro educativo modelo que ofrezca un servicio de alta calidad.",
        prefer_full=prefer_full_identity,
    )
    values = _resolve_card_text(
        center=center,
        full_text=center.values if center else None,
        short_text=center.card_values if center else None,
        fallback_text="Respeto, disciplina, responsabilidad, servicio y honestidad.",
        prefer_full=prefer_full_identity,
    )

    design_key = (
        center.card_design_key
        if center and getattr(center, "card_design_key", None)
        else "classic_green_v1"
    )

    return {
        "center_name": center.name if center else "Centro educativo",
        "center_logo_url": center.logo_url if center and center.logo_url else None,
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
        "phone": center.phone if center and center.phone else None,
        "email": center.email if center and center.email else None,
        "mission": mission,
        "vision": vision,
        "values": values,
        "card_footer_text": (
            center.card_footer_text
            if center and center.card_footer_text
            else "by Aula Nova"
        ),
        "report_footer_text": (
            center.report_footer_text
            if center and getattr(center, "report_footer_text", None)
            else "by Aula Nova"
        ),
        "card_design_key": design_key,
        "show_full_card_identity": prefer_full_identity,
    }


def _build_student_card_data(
    request: Request,
    db: Session,
    student: Student,
) -> dict:
    school_year = (
        db.query(SchoolYear)
        .filter(SchoolYear.id == student.school_year_id)
        .first()
    )

    card = _get_latest_card_for_student(db, student.id)

    qr_image_url = None
    if card and card.qr_token:
        qr_image_url = str(request.url_for("get_card_qr", card_id=card.id))

    return {
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


def _chunk_list(items: list, chunk_size: int) -> list[list]:
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def _build_students_query(
    db: Session,
    center_id: int,
    school_year_id: int | None = None,
    grade: str | None = None,
    section: str | None = None,
):
    query = db.query(Student).filter(Student.center_id == center_id)

    if school_year_id is not None:
        query = query.filter(Student.school_year_id == school_year_id)

    if grade:
        query = query.filter(Student.grade == grade)

    if section:
        query = query.filter(Student.section == section)

    return query.order_by(Student.last_name.asc(), Student.first_name.asc())


def _build_student_cards_print_context(
    request: Request,
    center_id: int,
    school_year_id: int | None,
    grade: str | None,
    section: str | None,
    db: Session,
) -> dict:
    center = _get_center_or_404(db, center_id)

    students = _build_students_query(
        db=db,
        center_id=center_id,
        school_year_id=school_year_id,
        grade=grade,
        section=section,
    ).all()

    if not students:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron estudiantes para los filtros indicados.",
        )

    student_cards = [
        _build_student_card_data(
            request=request,
            db=db,
            student=student,
        )
        for student in students
    ]

    pages = _chunk_list(student_cards, 6)

    return {
        "request": request,
        "pages": pages,
        **_build_center_theme(center),
    }


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request},
    )


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"request": request},
    )


@router.get("/attendance/scanner", response_class=HTMLResponse)
def attendance_scanner_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="attendance_scanner.html",
        context={"request": request},
    )


@router.get("/admin/centers/{center_id}/settings", response_class=HTMLResponse)
def center_settings_page(
    request: Request,
    center_id: int,
    db: Session = Depends(get_db),
):
    center = _get_center_or_404(db, center_id)

    return templates.TemplateResponse(
        request=request,
        name="center_settings.html",
        context={
            "request": request,
            "center_id": center.id,
            "center_name": center.name,
        },
    )


@router.get("/admin/students/register", response_class=HTMLResponse)
def student_register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="student_register.html",
        context={"request": request},
    )


@router.get("/admin/students", response_class=HTMLResponse)
def student_list_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="student_list.html",
        context={"request": request},
    )


@router.get("/admin/students/{student_id}/print", response_class=HTMLResponse)
def student_single_print_page(
    request: Request,
    student_id: int,
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(db, student_id)
    center = db.query(Center).filter(Center.id == student.center_id).first()

    context = {
        "request": request,
        **_build_center_theme(center),
        **_build_student_card_data(request=request, db=db, student=student),
    }

    return templates.TemplateResponse(
        request=request,
        name="student_card_single_print.html",
        context=context,
    )


@router.get("/students/{student_id}/card/front", response_class=HTMLResponse)
def student_card_front(
    request: Request,
    student_id: int,
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(db, student_id)
    center = db.query(Center).filter(Center.id == student.center_id).first()
    templates_for_design = _resolve_card_design_templates(center)

    context = {
        "request": request,
        **_build_center_theme(center),
        **_build_student_card_data(request=request, db=db, student=student),
    }

    return templates.TemplateResponse(
        request=request,
        name=templates_for_design["front"],
        context=context,
    )


@router.get("/students/{student_id}/card/back", response_class=HTMLResponse)
def student_card_back(
    request: Request,
    student_id: int,
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(db, student_id)
    center = db.query(Center).filter(Center.id == student.center_id).first()
    templates_for_design = _resolve_card_design_templates(center)

    context = {
        "request": request,
        **_build_center_theme(center),
        "student_id": student.id,
    }

    return templates.TemplateResponse(
        request=request,
        name=templates_for_design["back"],
        context=context,
    )


@router.get("/students/cards/print-sheet", response_class=HTMLResponse)
def student_cards_print_sheet(
    request: Request,
    center_id: int,
    school_year_id: int | None = None,
    grade: str | None = None,
    section: str | None = None,
    db: Session = Depends(get_db),
):
    context = _build_student_cards_print_context(
        request=request,
        center_id=center_id,
        school_year_id=school_year_id,
        grade=grade,
        section=section,
        db=db,
    )

    return templates.TemplateResponse(
        request=request,
        name="student_cards_print_sheet.html",
        context=context,
    )


@router.get("/students/cards/print-sheet.pdf")
def student_cards_print_sheet_pdf(
    request: Request,
    center_id: int,
    school_year_id: int | None = None,
    grade: str | None = None,
    section: str | None = None,
    db: Session = Depends(get_db),
):
    context = _build_student_cards_print_context(
        request=request,
        center_id=center_id,
        school_year_id=school_year_id,
        grade=grade,
        section=section,
        db=db,
    )

    html_content = templates.get_template("student_cards_print_sheet.html").render(context)
    pdf_bytes = render_pdf_from_html(html_content, base_url=str(request.base_url))

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'inline; filename="carnets_print_sheet.pdf"'
        },
    )


@router.get("/students/cards/print-multiple", response_class=HTMLResponse)
def student_cards_multiple_print(
    request: Request,
    ids: list[int],
    db: Session = Depends(get_db),
):
    if not ids:
        raise HTTPException(
            status_code=400,
            detail="Debes indicar al menos un estudiante.",
        )

    students = (
        db.query(Student)
        .filter(Student.id.in_(ids))
        .order_by(Student.last_name.asc(), Student.first_name.asc())
        .all()
    )

    if not students:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron estudiantes para imprimir.",
        )

    cards_data = []
    for student in students:
        center = db.query(Center).filter(Center.id == student.center_id).first()

        cards_data.append(
            {
                "student_id": student.id,
                "theme": _build_center_theme(center),
                "card": _build_student_card_data(
                    request=request,
                    db=db,
                    student=student,
                ),
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="student_cards_multiple_print.html",
        context={
            "request": request,
            "cards_data": cards_data,
        },
    )


@router.get("/admin/students/{student_id}/edit", response_class=HTMLResponse)
def edit_student_view(
    request: Request,
    student_id: int,
):
    return templates.TemplateResponse(
        request=request,
        name="student_edit.html",
        context={
            "request": request,
            "student_id": student_id,
        },
    )


@router.get("/students/cards/print-selected", response_class=HTMLResponse)
def student_cards_print_selected(
    request: Request,
    ids: list[int] = Query(...),
    db: Session = Depends(get_db),
):
    if not ids:
        raise HTTPException(
            status_code=400,
            detail="Debes indicar al menos un estudiante.",
        )

    students = (
        db.query(Student)
        .filter(Student.id.in_(ids))
        .order_by(Student.last_name.asc(), Student.first_name.asc())
        .all()
    )

    if not students:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron estudiantes.",
        )

    center = db.query(Center).filter(Center.id == students[0].center_id).first()

    student_cards = [
        _build_student_card_data(
            request=request,
            db=db,
            student=student,
        )
        for student in students
    ]

    pages = _chunk_list(student_cards, 6)

    context = {
        "request": request,
        "pages": pages,
        **_build_center_theme(center),
    }

    return templates.TemplateResponse(
        request=request,
        name="student_cards_print_sheet.html",
        context=context,
    )


@router.get("/reports/view", response_class=HTMLResponse)
def reports_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="reports.html",
        context={"request": request},
    )