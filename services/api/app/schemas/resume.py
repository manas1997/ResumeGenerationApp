from typing import Literal

from pydantic import BaseModel, Field


ClaimType = Literal[
    "summary",
    "skill",
    "experience",
    "project",
    "education",
    "certification",
    "achievement",
]


class SourceSpan(BaseModel):
    start: int = Field(ge=0)
    end: int = Field(ge=0)


class ResumeSection(BaseModel):
    name: str
    normalized_name: str
    content: str
    source_span: SourceSpan


class ResumeClaim(BaseModel):
    id: str
    claim_type: ClaimType
    text: str
    normalized_terms: list[str] = Field(default_factory=list)
    source_section: str
    source_span: SourceSpan
    confidence: float = Field(default=0.75, ge=0, le=1)


class ParsedResume(BaseModel):
    raw_text: str
    sections: list[ResumeSection] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    claims: list[ResumeClaim] = Field(default_factory=list)


class TailoredBullet(BaseModel):
    text: str
    source_claim_ids: list[str]
    jd_keywords: list[str] = Field(default_factory=list)


class TailoredSection(BaseModel):
    name: str
    items: list[TailoredBullet]


class TailoredResume(BaseModel):
    summary: list[TailoredBullet] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    sections: list[TailoredSection] = Field(default_factory=list)
    validation_warnings: list[str] = Field(default_factory=list)

