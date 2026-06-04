from statistics import mean

from app.schemas.template import TemplateFidelityReport, TemplateSnapshot, TemplateTextBox


def score_template_fidelity(
    source: TemplateSnapshot,
    generated: TemplateSnapshot,
    threshold: float = 99.0,
) -> TemplateFidelityReport:
    violations: list[str] = []

    page_structure_score = _page_structure_score(source, generated, violations)
    position_score = _position_score(source, generated, violations)
    font_score = _font_score(source, generated, violations)
    spacing_score = _spacing_score(source, generated, violations)
    margin_score = _margin_score(source, generated, violations)

    overall = mean(
        [font_score, margin_score, spacing_score, position_score, page_structure_score]
    )

    return TemplateFidelityReport(
        overall_score=round(overall, 2),
        font_score=round(font_score, 2),
        margin_score=round(margin_score, 2),
        spacing_score=round(spacing_score, 2),
        position_score=round(position_score, 2),
        page_structure_score=round(page_structure_score, 2),
        passed=overall >= threshold and not violations,
        threshold=threshold,
        violations=violations,
    )


def _page_structure_score(
    source: TemplateSnapshot,
    generated: TemplateSnapshot,
    violations: list[str],
) -> float:
    if len(source.pages) != len(generated.pages):
        violations.append("Page count changed.")
        return 0.0

    scores: list[float] = []
    for source_page, generated_page in zip(source.pages, generated.pages, strict=True):
        width_delta = abs(source_page.width - generated_page.width)
        height_delta = abs(source_page.height - generated_page.height)
        box_delta = abs(len(source_page.text_boxes) - len(generated_page.text_boxes))
        if width_delta > 0.5 or height_delta > 0.5:
            violations.append(f"Page size changed on page {source_page.page_number}.")
        if box_delta > 0:
            violations.append(f"Text box count changed on page {source_page.page_number}.")
        scores.append(max(0.0, 100.0 - width_delta - height_delta - box_delta * 3))
    return mean(scores) if scores else 0.0


def _position_score(
    source: TemplateSnapshot,
    generated: TemplateSnapshot,
    violations: list[str],
) -> float:
    deltas = []
    for source_box, generated_box in _paired_boxes(source, generated):
        delta = (
            abs(source_box.bbox.x0 - generated_box.bbox.x0)
            + abs(source_box.bbox.y0 - generated_box.bbox.y0)
            + abs(source_box.bbox.x1 - generated_box.bbox.x1)
            + abs(source_box.bbox.y1 - generated_box.bbox.y1)
        )
        if delta > 1.0:
            violations.append(f"Text position changed for {source_box.id}.")
        deltas.append(delta)
    return _score_from_deltas(deltas, penalty_multiplier=2.0)


def _font_score(
    source: TemplateSnapshot,
    generated: TemplateSnapshot,
    violations: list[str],
) -> float:
    penalties = []
    for source_box, generated_box in _paired_boxes(source, generated):
        penalty = 0.0
        if source_box.font_name != generated_box.font_name:
            violations.append(f"Font family changed for {source_box.id}.")
            penalty += 8.0
        if abs(source_box.font_size - generated_box.font_size) > 0.1:
            violations.append(f"Font size changed for {source_box.id}.")
            penalty += 8.0
        if source_box.color_hex.lower() != generated_box.color_hex.lower():
            violations.append(f"Text color changed for {source_box.id}.")
            penalty += 6.0
        penalties.append(penalty)
    return max(0.0, 100.0 - (mean(penalties) if penalties else 0.0))


def _spacing_score(
    source: TemplateSnapshot,
    generated: TemplateSnapshot,
    violations: list[str],
) -> float:
    source_gaps = _vertical_gaps(source)
    generated_gaps = _vertical_gaps(generated)
    if len(source_gaps) != len(generated_gaps):
        violations.append("Vertical spacing structure changed.")
        return 0.0
    deltas = [abs(left - right) for left, right in zip(source_gaps, generated_gaps, strict=True)]
    for index, delta in enumerate(deltas):
        if delta > 0.5:
            violations.append(f"Vertical spacing changed near text run {index + 1}.")
    return _score_from_deltas(deltas, penalty_multiplier=4.0)


def _margin_score(
    source: TemplateSnapshot,
    generated: TemplateSnapshot,
    violations: list[str],
) -> float:
    deltas = []
    for source_page, generated_page in zip(source.pages, generated.pages, strict=False):
        source_margins = _page_margins(source_page.text_boxes, source_page.width, source_page.height)
        generated_margins = _page_margins(
            generated_page.text_boxes,
            generated_page.width,
            generated_page.height,
        )
        for source_margin, generated_margin in zip(source_margins, generated_margins, strict=True):
            deltas.append(abs(source_margin - generated_margin))
    for delta in deltas:
        if delta > 0.5:
            violations.append("Page margin changed.")
            break
    return _score_from_deltas(deltas, penalty_multiplier=6.0)


def _paired_boxes(
    source: TemplateSnapshot,
    generated: TemplateSnapshot,
) -> list[tuple[TemplateTextBox, TemplateTextBox]]:
    pairs: list[tuple[TemplateTextBox, TemplateTextBox]] = []
    for source_page, generated_page in zip(source.pages, generated.pages, strict=False):
        pairs.extend(zip(source_page.text_boxes, generated_page.text_boxes, strict=False))
    return pairs


def _vertical_gaps(snapshot: TemplateSnapshot) -> list[float]:
    gaps: list[float] = []
    for page in snapshot.pages:
        boxes = sorted(page.text_boxes, key=lambda box: (box.bbox.y0, box.bbox.x0))
        for previous, current in zip(boxes, boxes[1:], strict=False):
            gaps.append(current.bbox.y0 - previous.bbox.y1)
    return gaps


def _page_margins(boxes: list[TemplateTextBox], width: float, height: float) -> tuple[float, ...]:
    if not boxes:
        return (width, height, width, height)
    return (
        min(box.bbox.x0 for box in boxes),
        min(box.bbox.y0 for box in boxes),
        width - max(box.bbox.x1 for box in boxes),
        height - max(box.bbox.y1 for box in boxes),
    )


def _score_from_deltas(deltas: list[float], penalty_multiplier: float) -> float:
    if not deltas:
        return 100.0
    return max(0.0, 100.0 - mean(deltas) * penalty_multiplier)

