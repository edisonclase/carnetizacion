from io import BytesIO
import re

import qrcode
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.card import Card
from app.models.center import Center
from app.models.school_year import SchoolYear
from app.models.staff import Staff
from app.models.staff_card import StaffCard
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
    "premium_institutional_v1": {
        "front": "cards/student_card_front_premium.html",
        "back": "cards/student_card_back_premium.html",
    },
    "tech_modern_v1": {
        "front": "cards/student_card_front_tech.html",
        "back": "cards/student_card_back_tech.html",
    },
}


CARD_PREVIEW_TEMPLATES = {
    "classic_green_v1": {
        "front": "student_card_front.html",
        "back": "student_card_back.html",
        "title": "Diseño actual",
    },
    "prestige_clean_v1": {
        "front": "student_card_front.html",
        "back": "student_card_back.html",
        "title": "Prestige Clean v1",
    },
    "nova_modern_v1": {
        "front": "student_card_front.html",
        "back": "student_card_back.html",
        "title": "Nova Modern v1",
    },
    "premium_institutional_v1": {
        "front": "cards/student_card_front_premium.html",
        "back": "cards/student_card_back_premium.html",
        "title": "Premium institucional",
    },
    "tech_modern_v1": {
        "front": "cards/student_card_front_tech.html",
        "back": "cards/student_card_back_tech.html",
        "title": "Moderno tecnológico",
    },
}


NEW_PREMIUM_DESIGNS = {
    "premium_institutional_v1",
    "tech_modern_v1",
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


def _get_staff_or_404(db: Session, staff_id: int) -> Staff:
    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Personal no encontrado.")
    return staff


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


def _get_latest_card_for_staff(db: Session, staff_id: int) -> StaffCard | None:
    card = (
        db.query(StaffCard)
        .filter(StaffCard.staff_id == staff_id, StaffCard.is_active == True)
        .order_by(StaffCard.id.desc())
        .first()
    )

    if card:
        return card

    return (
        db.query(StaffCard)
        .filter(StaffCard.staff_id == staff_id)
        .order_by(StaffCard.id.desc())
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


def _resolve_preview_card_templates(design_key: str) -> dict:
    return CARD_PREVIEW_TEMPLATES.get(
        design_key,
        CARD_PREVIEW_TEMPLATES["classic_green_v1"],
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


def _normalize_grade_value(value: str | None) -> str:
    if not value:
        return ""
    return str(value).strip().lower()


def _extract_grade_number(value: str | None) -> int | None:
    normalized = _normalize_grade_value(value)
    if not normalized:
        return None

    digit_match = re.search(r"\d+", normalized)
    if digit_match:
        try:
            return int(digit_match.group())
        except ValueError:
            pass

    mapping = {
        "primero": 1,
        "primer": 1,
        "1ro": 1,
        "1ero": 1,
        "1er": 1,
        "segundo": 2,
        "2do": 2,
        "tercero": 3,
        "3ro": 3,
        "cuarto": 4,
        "4to": 4,
        "quinto": 5,
        "5to": 5,
        "sexto": 6,
        "6to": 6,
    }

    for key, number in mapping.items():
        if key in normalized:
            return number

    return None


def _build_cycle_label(grade: str | None) -> str:
    grade_number = _extract_grade_number(grade)
    if grade_number is None:
        return "Ciclo no definido"
    if grade_number in {1, 2, 3}:
        return "Primer Ciclo"
    return "Segundo Ciclo"


def _pick_first_non_empty(*values) -> str | None:
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def _build_student_area_label(student: Student) -> str | None:
    raw_value = _pick_first_non_empty(
        getattr(student, "technical_area", None),
        getattr(student, "technical_program", None),
        getattr(student, "program_name", None),
        getattr(student, "specialty", None),
        getattr(student, "speciality", None),
        getattr(student, "vocational_area", None),
        getattr(student, "major_name", None),
    )

    if not raw_value:
        return None

    return raw_value


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
        "motto": center.motto if center and center.motto else None,
        "address": center.address if center and center.address else None,
        "mission": mission,
        "vision": vision,
        "values": values,
        "card_footer_text": (
            center.card_footer_text
            if center and center.card_footer_text
            else "by Aula Nova"
        ),
        "card_loss_notice": (
            center.card_loss_notice
            if center and getattr(center, "card_loss_notice", None)
            else "Si encuentra este carnet, favor devolverlo al centro."
        ),
        "card_loss_contact": (
            center.card_loss_contact
            if center and getattr(center, "card_loss_contact", None)
            else _pick_first_non_empty(
                center.phone if center else None,
                center.email if center else None,
                "Contacte al centro educativo.",
            )
        ),
        "card_show_technical_area": (
            bool(center.card_show_technical_area)
            if center and hasattr(center, "card_show_technical_area")
            else True
        ),
        "card_technical_area_label": (
            center.card_technical_area_label
            if center and getattr(center, "card_technical_area_label", None)
            else "Área técnica"
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

    center = db.query(Center).filter(Center.id == student.center_id).first()

    card = _get_latest_card_for_student(db, student.id)

    qr_image_url = None
    if card and card.qr_token:
        qr_image_url = str(request.url_for("get_card_qr", card_id=card.id))

    student_full_name = " ".join(
        [
            str(student.first_name or "").strip(),
            str(student.last_name or "").strip(),
        ]
    ).strip()

    cycle_label = _build_cycle_label(student.grade)
    technical_area = _build_student_area_label(student)

    show_technical_area = (
        bool(center.card_show_technical_area)
        if center and hasattr(center, "card_show_technical_area")
        else True
    )

    if not show_technical_area:
        technical_area = None

    technical_area_label = (
        center.card_technical_area_label
        if center and getattr(center, "card_technical_area_label", None)
        else "Área técnica"
    )

    return {
        "student_id": student.id,
        "student_full_name": student_full_name,
        "student_code": student.student_code,
        "minerd_id": student.minerd_id,
        "grade": student.grade,
        "section": student.section,
        "school_year_name": _normalize_school_year_name(
            school_year.name if school_year else "-"
        ),
        "student_photo_url": student.photo_path,
        "qr_image_url": qr_image_url,
        "student_role_label": "Estudiante",
        "student_cycle_label": cycle_label,
        "student_technical_area": technical_area,
        "student_technical_area_label": technical_area_label,
        "student_cycle_and_area": (
            f"{cycle_label} · {technical_area}"
            if cycle_label == "Segundo Ciclo" and technical_area
            else cycle_label
        ),
    }


def _build_card_full_context(
    request: Request,
    db: Session,
    student: Student,
) -> dict:
    center = db.query(Center).filter(Center.id == student.center_id).first()

    return {
        "request": request,
        **_build_center_theme(center),
        **_build_student_card_data(request=request, db=db, student=student),
    }


def _design_requires_full_back_context(center: Center | None) -> bool:
    design_key = (
        center.card_design_key
        if center and getattr(center, "card_design_key", None)
        else "classic_green_v1"
    )
    return design_key in NEW_PREMIUM_DESIGNS


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


def _build_staff_group_label(value: str | None) -> str:
    mapping = {
        "administrativo": "Personal administrativo",
        "apoyo": "Personal de apoyo",
        "docente_tecnico": "Personal docente / técnico",
    }
    return mapping.get(str(value or "").strip().lower(), "Personal institucional")


def _build_staff_position_label(value: str | None) -> str:
    mapping = {
        "secretaria": "Secretaria",
        "digitador": "Digitador",
        "administrativo_otro": "Administrativo",
        "conserje": "Conserje",
        "mayordomo": "Mayordomo",
        "jardinero": "Jardinero",
        "portero": "Portero",
        "sereno": "Sereno",
        "apoyo_otro": "Personal de apoyo",
        "docente": "Docente",
        "director": "Director",
        "subdirector": "Subdirector",
        "coordinador": "Coordinador",
        "psicologo": "Psicólogo",
        "psicologa": "Psicóloga",
        "orientador": "Orientador",
        "orientadora": "Orientadora",
        "tecnico_otro": "Técnico",
    }
    return mapping.get(
        str(value or "").strip().lower(),
        str(value or "Personal").replace("_", " ").title(),
    )


def _build_staff_qr_payload(card: StaffCard, staff: Staff) -> str:
    payload_lines = [
        "NOVA_ID_STAFF_CARD",
        f"card_id={card.id}",
        f"staff_id={staff.id}",
        f"staff_code={staff.staff_code}",
        f"card_code={card.card_code}",
        f"qr_token={card.qr_token}",
        f"full_name={staff.first_name} {staff.last_name}".strip(),
        f"group={staff.staff_group}",
        f"position={staff.staff_position}",
        f"is_active={card.is_active}",
    ]
    return "\n".join(payload_lines)


def _build_staff_card_context(request: Request, db: Session, staff: Staff) -> dict:
    center = db.query(Center).filter(Center.id == staff.center_id).first()
    card = _get_latest_card_for_staff(db, staff.id)

    return {
        "request": request,
        **_build_center_theme(center),
        "staff_id": staff.id,
        "staff_full_name": f"{staff.first_name} {staff.last_name}".strip(),
        "staff_code": staff.staff_code,
        "staff_card_code": card.card_code if card else None,
        "staff_photo_url": staff.photo_path,
        "staff_group": staff.staff_group,
        "staff_group_label": _build_staff_group_label(staff.staff_group),
        "staff_position": staff.staff_position,
        "staff_position_label": _build_staff_position_label(staff.staff_position),
        "staff_department": staff.department,
        "qr_image_url": str(request.url_for("staff_card_qr", staff_id=staff.id)) if card else None,
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


@router.get("/billing/view", response_class=HTMLResponse)
def billing_view(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="billing.html",
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

    if _design_requires_full_back_context(center):
        context = {
            "request": request,
            **_build_center_theme(center),
            **_build_student_card_data(request=request, db=db, student=student),
        }
    else:
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


@router.get("/preview/students/{student_id}/card/{design_key}/{side}", response_class=HTMLResponse)
def student_card_preview_render(
    request: Request,
    student_id: int,
    design_key: str,
    side: str,
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(db, student_id)

    side = side.lower().strip()
    if side not in {"front", "back"}:
        raise HTTPException(status_code=400, detail="El lado debe ser 'front' o 'back'.")

    templates_for_design = _resolve_preview_card_templates(design_key)
    context = _build_card_full_context(request=request, db=db, student=student)

    return templates.TemplateResponse(
        request=request,
        name=templates_for_design[side],
        context=context,
    )


@router.get("/preview/students/{student_id}/cards", response_class=HTMLResponse)
def student_cards_preview_gallery(
    request: Request,
    student_id: int,
    db: Session = Depends(get_db),
):
    student = _get_student_or_404(db, student_id)

    center = db.query(Center).filter(Center.id == student.center_id).first()
    school_year = (
        db.query(SchoolYear)
        .filter(SchoolYear.id == student.school_year_id)
        .first()
        if student.school_year_id
        else None
    )

    preview_items = [
        {
            "title": "Classic Green v1 · Frente",
            "subtitle": "Diseño actual operativo",
            "url": request.url_for(
                "student_card_preview_render",
                student_id=student.id,
                design_key="classic_green_v1",
                side="front",
            ),
        },
        {
            "title": "Classic Green v1 · Reverso",
            "subtitle": "Diseño actual operativo",
            "url": request.url_for(
                "student_card_preview_render",
                student_id=student.id,
                design_key="classic_green_v1",
                side="back",
            ),
        },
        {
            "title": "Premium institucional · Frente",
            "subtitle": "Institucional, elegante y comercial",
            "url": request.url_for(
                "student_card_preview_render",
                student_id=student.id,
                design_key="premium_institutional_v1",
                side="front",
            ),
        },
        {
            "title": "Premium institucional · Reverso",
            "subtitle": "Reverso premium con identidad del centro",
            "url": request.url_for(
                "student_card_preview_render",
                student_id=student.id,
                design_key="premium_institutional_v1",
                side="back",
            ),
        },
        {
            "title": "Tech Modern · Frente",
            "subtitle": "Tecnológico, premium y digital",
            "url": request.url_for(
                "student_card_preview_render",
                student_id=student.id,
                design_key="tech_modern_v1",
                side="front",
            ),
        },
        {
            "title": "Tech Modern · Reverso",
            "subtitle": "Reverso tecnológico institucional",
            "url": request.url_for(
                "student_card_preview_render",
                student_id=student.id,
                design_key="tech_modern_v1",
                side="back",
            ),
        },
    ]

    return templates.TemplateResponse(
        request=request,
        name="cards/card_preview_gallery.html",
        context={
            "request": request,
            "student": student,
            "center": center,
            "school_year": school_year,
            "preview_items": preview_items,
        },
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


@router.get("/admin/staff", response_class=HTMLResponse)
def staff_list_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="staff_list.html",
        context={"request": request},
    )


@router.get("/admin/staff/register", response_class=HTMLResponse)
def staff_register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="staff_register.html",
        context={"request": request},
    )


@router.get("/admin/staff/{staff_id}/print", response_class=HTMLResponse)
def staff_single_print_page(
    request: Request,
    staff_id: int,
    db: Session = Depends(get_db),
):
    staff = _get_staff_or_404(db, staff_id)

    return templates.TemplateResponse(
        request=request,
        name="staff_card_single_print.html",
        context={
            "request": request,
            "staff_id": staff.id,
        },
    )


@router.get("/staff/{staff_id}/card/qr", name="staff_card_qr")
def staff_card_qr(
    staff_id: int,
    db: Session = Depends(get_db),
):
    staff = _get_staff_or_404(db, staff_id)
    card = _get_latest_card_for_staff(db, staff_id)

    if not card:
        raise HTTPException(
            status_code=404,
            detail="Este miembro del personal no tiene un carnet emitido.",
        )

    payload = _build_staff_qr_payload(card=card, staff=staff)

    qr = qrcode.QRCode(
        version=2,
        box_size=8,
        border=2,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    image = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="image/png",
    )


@router.get("/staff/{staff_id}/card/front", response_class=HTMLResponse)
def staff_card_front(
    request: Request,
    staff_id: int,
    db: Session = Depends(get_db),
):
    staff = _get_staff_or_404(db, staff_id)

    return templates.TemplateResponse(
        request=request,
        name="staff_card_front.html",
        context=_build_staff_card_context(request=request, db=db, staff=staff),
    )


@router.get("/staff/{staff_id}/card/back", response_class=HTMLResponse)
def staff_card_back(
    request: Request,
    staff_id: int,
    db: Session = Depends(get_db),
):
    staff = _get_staff_or_404(db, staff_id)

    return templates.TemplateResponse(
        request=request,
        name="staff_card_back.html",
        context=_build_staff_card_context(request=request, db=db, staff=staff),
    )