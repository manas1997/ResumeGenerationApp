from pydantic import BaseModel, Field

from app.schemas.job_description import ParsedJobDescription
from app.schemas.resume import ParsedResume, TailoredResume
from app.schemas.scorecard import Scorecard


class SourceResumeInput(BaseModel):
    raw_text: str


class JobDescriptionInput(BaseModel):
    raw_text: str


class TailoringPreferences(BaseModel):
    target_role: str | None = None
    seniority: str | None = None
    years_of_experience: int | None = Field(default=None, ge=0, le=60)
    skills_emphasis: list[str] = Field(default_factory=list)
    tone: str = "professional"


class ChangeExplanation(BaseModel):
    original_text: str
    tailored_text: str
    source_claim_ids: list[str]
    jd_keywords: list[str]
    reason: str
    recruiter_benefit: str
    ats_benefit: str


class TailoringRequest(BaseModel):
    source_resume: SourceResumeInput
    job_description: JobDescriptionInput
    preferences: TailoringPreferences = Field(default_factory=TailoringPreferences)


class TailoringResponse(BaseModel):
    run_id: str
    parsed_resume: ParsedResume
    parsed_job_description: ParsedJobDescription
    tailored_resume: TailoredResume
    scorecard: Scorecard
    comparison: list[ChangeExplanation]

