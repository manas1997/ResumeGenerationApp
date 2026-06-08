from pydantic import BaseModel, Field


class BulletRewrite(BaseModel):
    source_claim_id: str
    original_text: str
    rewritten_text: str
    jd_keywords: list[str] = Field(default_factory=list)
    change_reason: str
    recruiter_benefit: str
    ats_benefit: str


class BulletRewriteResponse(BaseModel):
    rewrites: list[BulletRewrite] = Field(default_factory=list)

