from app.schemas.resume import TailoredResume
from app.services.export_service import render_resume_html


def render_pdf_bytes(resume: TailoredResume) -> bytes:
    from weasyprint import HTML

    return HTML(string=render_resume_html(resume)).write_pdf()

