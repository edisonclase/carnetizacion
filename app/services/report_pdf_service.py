from fastapi.templating import Jinja2Templates
from app.services.pdf_service import render_pdf_from_html

templates = Jinja2Templates(directory="app/pdf/templates")


def build_daily_report_pdf(context: dict, request):
    html = templates.get_template("daily_report.html").render(context)
    return render_pdf_from_html(html, base_url=str(request.base_url))