from app.schemas.template import BoundingBox, TemplatePage, TemplateSnapshot, TemplateTextBox
from app.services.template_fidelity import score_template_fidelity


def test_identical_template_snapshot_passes_99_threshold() -> None:
    source = _snapshot()
    report = score_template_fidelity(source, source, threshold=99.0)

    assert report.passed is True
    assert report.overall_score == 100
    assert report.violations == []


def test_position_change_fails_template_fidelity_gate() -> None:
    source = _snapshot()
    generated = _snapshot(x_offset=3)

    report = score_template_fidelity(source, generated, threshold=99.0)

    assert report.passed is False
    assert report.position_score < 99
    assert any("Text position changed" in violation for violation in report.violations)


def test_font_change_fails_template_fidelity_gate() -> None:
    source = _snapshot()
    generated = _snapshot(font_name="Helvetica")

    report = score_template_fidelity(source, generated, threshold=99.0)

    assert report.passed is False
    assert report.font_score < 100
    assert any("Font family changed" in violation for violation in report.violations)


def _snapshot(x_offset: float = 0, font_name: str = "Inter-Regular") -> TemplateSnapshot:
    return TemplateSnapshot(
        source_checksum="checksum",
        pages=[
            TemplatePage(
                page_number=1,
                width=612,
                height=792,
                text_boxes=[
                    TemplateTextBox(
                        id="p1_t1",
                        page_number=1,
                        text="Built APIs with Python.",
                        bbox=BoundingBox(
                            x0=72 + x_offset,
                            y0=120,
                            x1=260 + x_offset,
                            y1=134,
                        ),
                        font_name=font_name,
                        font_size=10.5,
                        color_hex="#111111",
                    ),
                    TemplateTextBox(
                        id="p1_t2",
                        page_number=1,
                        text="Skills",
                        bbox=BoundingBox(
                            x0=72 + x_offset,
                            y0=156,
                            x1=112 + x_offset,
                            y1=170,
                        ),
                        font_name=font_name,
                        font_size=11.0,
                        color_hex="#111111",
                    ),
                ],
            )
        ],
    )

