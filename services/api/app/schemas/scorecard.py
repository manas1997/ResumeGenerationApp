from typing import Literal

from pydantic import BaseModel, Field


KeywordSupport = Literal["supported", "unsupported", "ambiguous"]


class MissingKeyword(BaseModel):
    keyword: str
    support_status: KeywordSupport
    reason: str


class Scorecard(BaseModel):
    keyword_match_score: float = Field(ge=0, le=100)
    semantic_alignment_score: float = Field(ge=0, le=100)
    ats_compatibility_score: float = Field(ge=0, le=100)
    recruiter_readability_score: float = Field(ge=0, le=100)
    compatibility_confidence: str
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[MissingKeyword] = Field(default_factory=list)
    improvement_recommendations: list[str] = Field(default_factory=list)

