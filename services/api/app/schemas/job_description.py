from typing import Literal

from pydantic import BaseModel, Field


RequirementType = Literal[
    "required_skill",
    "preferred_skill",
    "technology",
    "responsibility",
    "domain_keyword",
    "action_verb",
    "seniority_signal",
]


class JobRequirement(BaseModel):
    id: str
    requirement_type: RequirementType
    text: str
    normalized_value: str
    priority: int = Field(default=1, ge=1, le=5)
    confidence: float = Field(default=0.7, ge=0, le=1)


class ParsedJobDescription(BaseModel):
    raw_text: str
    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    years_of_experience: int | None = None
    role_expectations: list[str] = Field(default_factory=list)
    domain_keywords: list[str] = Field(default_factory=list)
    action_verbs: list[str] = Field(default_factory=list)
    seniority_signals: list[str] = Field(default_factory=list)
    requirements: list[JobRequirement] = Field(default_factory=list)

