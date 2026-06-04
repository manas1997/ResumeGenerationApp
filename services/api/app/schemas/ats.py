from typing import Literal

from pydantic import BaseModel, Field


SkillEvidenceLevel = Literal["missing", "weak", "strong"]
CheckStatus = Literal["pass", "warning", "fail"]


class KeywordAnalysis(BaseModel):
    jd_keywords: list[str] = Field(default_factory=list)
    resume_keywords: list[str] = Field(default_factory=list)
    matched_keywords: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    coverage_percentage: float = Field(ge=0, le=100)


class SkillGapItem(BaseModel):
    skill: str
    level: SkillEvidenceLevel
    evidence_claim_ids: list[str] = Field(default_factory=list)
    explanation: str


class ExperienceGapItem(BaseModel):
    responsibility: str
    evidence_strength: SkillEvidenceLevel
    best_matching_claim_id: str | None = None
    explanation: str


class AtsCompatibilityCheck(BaseModel):
    name: str
    status: CheckStatus
    detail: str


class SkillImprovementReport(BaseModel):
    technical_skills_to_learn: list[str] = Field(default_factory=list)
    experience_areas_to_build: list[str] = Field(default_factory=list)
    suggested_projects: list[str] = Field(default_factory=list)
    certification_suggestions: list[str] = Field(default_factory=list)
    interview_preparation_areas: list[str] = Field(default_factory=list)
    safety_note: str = (
        "Recommendations are based on what the resume currently demonstrates, "
        "not on assumptions about the user's actual knowledge."
    )


class AtsAnalysisDashboard(BaseModel):
    ats_compatibility_score: float = Field(ge=0, le=100)
    keyword_match_score: float = Field(ge=0, le=100)
    technical_skill_match: float = Field(ge=0, le=100)
    experience_match: float = Field(ge=0, le=100)
    leadership_match: float = Field(ge=0, le=100)
    domain_match: float = Field(ge=0, le=100)
    keyword_analysis: KeywordAnalysis
    missing_skills: list[SkillGapItem] = Field(default_factory=list)
    weakly_demonstrated_skills: list[SkillGapItem] = Field(default_factory=list)
    strongly_demonstrated_skills: list[SkillGapItem] = Field(default_factory=list)
    experience_gaps: list[ExperienceGapItem] = Field(default_factory=list)
    compatibility_checks: list[AtsCompatibilityCheck] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    skill_improvement_report: SkillImprovementReport

