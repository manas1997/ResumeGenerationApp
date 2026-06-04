from app.schemas.resume import TailoredResume
from app.schemas.template import TemplateFidelityReport, TemplateReplacement
from app.services.template_preserving_renderer import render_pdf_with_text_replacements


def render_pdf_bytes(resume: TailoredResume) -> bytes:
    raise RuntimeError(
        "Generic PDF rendering is disabled for production output. "
        "Use render_template_preserved_pdf_bytes with the source resume PDF."
    )


def render_template_preserved_pdf_bytes(
    source_pdf_bytes: bytes,
    replacements: list[TemplateReplacement],
    threshold: float = 99.0,
) -> tuple[bytes, TemplateFidelityReport]:
    return render_pdf_with_text_replacements(
        source_pdf_bytes=source_pdf_bytes,
        replacements=replacements,
        threshold=threshold,
    )
