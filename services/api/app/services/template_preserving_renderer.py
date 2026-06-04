from app.schemas.template import TemplateFidelityReport, TemplateReplacement
from app.services.template_analyzer import extract_template_snapshot
from app.services.template_fidelity import score_template_fidelity


class TemplateFidelityError(RuntimeError):
    def __init__(self, report: TemplateFidelityReport):
        self.report = report
        super().__init__(
            f"Template fidelity score {report.overall_score} is below threshold {report.threshold}."
        )


def render_pdf_with_text_replacements(
    source_pdf_bytes: bytes,
    replacements: list[TemplateReplacement],
    threshold: float = 99.0,
) -> tuple[bytes, TemplateFidelityReport]:
    fitz = _load_fitz()
    source_snapshot = extract_template_snapshot(source_pdf_bytes)
    boxes_by_id = {
        text_box.id: text_box
        for page in source_snapshot.pages
        for text_box in page.text_boxes
    }

    document = fitz.open(stream=source_pdf_bytes, filetype="pdf")
    for replacement in replacements:
        target = boxes_by_id.get(replacement.target_box_id)
        if target is None:
            raise ValueError(f"Unknown template text box: {replacement.target_box_id}")
        if target.text.strip() != replacement.original_text.strip():
            raise ValueError(f"Original text mismatch for {replacement.target_box_id}")

        page = document[target.page_number - 1]
        rect = fitz.Rect(target.bbox.x0, target.bbox.y0, target.bbox.x1, target.bbox.y1)

        page.add_redact_annot(rect, fill=(1, 1, 1))
        page.apply_redactions()
        page.insert_textbox(
            rect,
            replacement.replacement_text,
            fontsize=target.font_size,
            fontname=_safe_font(target.font_name),
            color=_hex_to_rgb(target.color_hex),
            align=fitz.TEXT_ALIGN_LEFT,
        )

    generated_pdf = document.tobytes(deflate=True)
    generated_snapshot = extract_template_snapshot(generated_pdf)
    report = score_template_fidelity(source_snapshot, generated_snapshot, threshold=threshold)
    if not report.passed:
        raise TemplateFidelityError(report)
    return generated_pdf, report


def _safe_font(font_name: str) -> str:
    lowered = font_name.lower()
    if "times" in lowered:
        return "Times-Roman"
    if "courier" in lowered:
        return "Courier"
    return "Helvetica"


def _hex_to_rgb(value: str) -> tuple[float, float, float]:
    cleaned = value.lstrip("#")
    red = int(cleaned[0:2], 16) / 255
    green = int(cleaned[2:4], 16) / 255
    blue = int(cleaned[4:6], 16) / 255
    return (red, green, blue)


def _load_fitz():
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required for template-preserving rendering.") from exc
    return fitz

