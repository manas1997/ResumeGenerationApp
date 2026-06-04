from pydantic import BaseModel, Field


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class TemplateTextBox(BaseModel):
    id: str
    page_number: int = Field(ge=1)
    text: str
    bbox: BoundingBox
    font_name: str
    font_size: float
    color_hex: str
    writing_mode: str = "horizontal"


class TemplatePage(BaseModel):
    page_number: int = Field(ge=1)
    width: float
    height: float
    text_boxes: list[TemplateTextBox] = Field(default_factory=list)


class TemplateSnapshot(BaseModel):
    source_checksum: str
    pages: list[TemplatePage]


class TemplateReplacement(BaseModel):
    target_box_id: str
    original_text: str
    replacement_text: str
    source_claim_ids: list[str] = Field(default_factory=list)


class TemplateFidelityReport(BaseModel):
    overall_score: float = Field(ge=0, le=100)
    font_score: float = Field(ge=0, le=100)
    margin_score: float = Field(ge=0, le=100)
    spacing_score: float = Field(ge=0, le=100)
    position_score: float = Field(ge=0, le=100)
    page_structure_score: float = Field(ge=0, le=100)
    passed: bool
    threshold: float = 99.0
    violations: list[str] = Field(default_factory=list)

