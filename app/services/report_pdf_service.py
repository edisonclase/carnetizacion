from fastapi.templating import Jinja2Templates

from app.services.pdf_service import render_pdf_from_html

templates = Jinja2Templates(directory="app/pdf/templates")


def build_report_pdf(
    *,
    template_name: str,
    context: dict,
    base_url: str,
) -> bytes:
    html = templates.get_template(template_name).render(context)
    return render_pdf_from_html(html, base_url=base_url)