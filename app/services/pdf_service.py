try:
    from weasyprint import HTML
except Exception:
    HTML = None


def render_pdf_from_html(html_content: str, base_url: str) -> bytes:
    pdf_bytes = HTML(string=html_content, base_url=base_url).write_pdf()
    return pdf_bytes