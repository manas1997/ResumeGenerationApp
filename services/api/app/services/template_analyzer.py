import hashlib

from app.schemas.template import BoundingBox, TemplatePage, TemplateSnapshot, TemplateTextBox


def extract_template_snapshot(source_pdf_bytes: bytes) -> TemplateSnapshot:
    fitz = _load_fitz()
    document = fitz.open(stream=source_pdf_bytes, filetype="pdf")
    pages: list[TemplatePage] = []

    for page_index, page in enumerate(document, start=1):
        page_dict = page.get_text("dict")
        text_boxes: list[TemplateTextBox] = []
        span_index = 0

        for block in page_dict.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span.get("text", "")
                    if not text.strip():
                        continue
                    span_index += 1
                    bbox = span.get("bbox", [0, 0, 0, 0])
                    text_boxes.append(
                        TemplateTextBox(
                            id=f"p{page_index}_t{span_index}",
                            page_number=page_index,
                            text=text,
                            bbox=BoundingBox(x0=bbox[0], y0=bbox[1], x1=bbox[2], y1=bbox[3]),
                            font_name=span.get("font", ""),
                            font_size=float(span.get("size", 0)),
                            color_hex=_int_color_to_hex(int(span.get("color", 0))),
                        )
                    )

        pages.append(
            TemplatePage(
                page_number=page_index,
                width=float(page.rect.width),
                height=float(page.rect.height),
                text_boxes=text_boxes,
            )
        )

    return TemplateSnapshot(
        source_checksum=hashlib.sha256(source_pdf_bytes).hexdigest(),
        pages=pages,
    )


def _int_color_to_hex(value: int) -> str:
    red = (value >> 16) & 255
    green = (value >> 8) & 255
    blue = value & 255
    return f"#{red:02x}{green:02x}{blue:02x}"


def _load_fitz():
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is required for template analysis. Install pymupdf.") from exc
    return fitz

