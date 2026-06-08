from typing import Any

from pydantic import BaseModel

from app.schemas.ai import BulletRewrite, BulletRewriteResponse
from app.schemas.tailoring import TailoringPreferences
from app.services.jd_parser import parse_job_description
from app.services.resume_parser import parse_resume_text
from app.services.scoring import compute_scorecard
from app.services.tailoring_engine import tailor_resume


class FakeRewriteProvider:
    def __init__(self, *, inject_unsupported_keyword: bool = False) -> None:
        self.inject_unsupported_keyword = inject_unsupported_keyword

    def structured_completion(
        self,
        *,
        prompt_name: str,
        system_prompt: str,
        user_payload: dict[str, Any],
        schema: type[BaseModel],
    ) -> BaseModel:
        claim = user_payload["allowed_claims"][0]
        rewritten = "Built reliable Python APIs for customer workflows."
        if self.inject_unsupported_keyword:
            rewritten = "Built reliable Python APIs using Kubernetes for customer workflows."

        return BulletRewriteResponse(
            rewrites=[
                BulletRewrite(
                    source_claim_id=claim["source_claim_id"],
                    original_text=claim["original_text"],
                    rewritten_text=rewritten,
                    jd_keywords=["python"],
                    change_reason="Aligned wording to the JD while preserving source facts.",
                    recruiter_benefit="Makes the API experience clearer.",
                    ats_benefit="Surfaces supported Python keyword evidence.",
                )
            ]
        )


def test_ai_rewrite_is_used_when_valid() -> None:
    resume = parse_resume_text(
        """
SKILLS
Python

EXPERIENCE
- Built backend API services with Python for internal customer workflow automation.
"""
    )
    jd = parse_job_description("Required: Python. Build reliable backend APIs.")
    scorecard = compute_scorecard(resume, jd)

    result = tailor_resume(
        resume,
        jd,
        TailoringPreferences(),
        scorecard,
        ai_provider=FakeRewriteProvider(),
    )
    generated = " ".join(
        item.text for section in result.resume.sections for item in section.items
    )

    assert "Built reliable Python APIs for customer workflows." in generated


def test_ai_rewrite_with_unsupported_keyword_is_rejected() -> None:
    resume = parse_resume_text(
        """
SKILLS
Python

EXPERIENCE
- Built backend API services with Python for internal customer workflow automation.
"""
    )
    jd = parse_job_description("Required: Python and Kubernetes. Build reliable backend APIs.")
    scorecard = compute_scorecard(resume, jd)

    result = tailor_resume(
        resume,
        jd,
        TailoringPreferences(),
        scorecard,
        ai_provider=FakeRewriteProvider(inject_unsupported_keyword=True),
    )
    generated = " ".join(
        item.text for section in result.resume.sections for item in section.items
    )

    assert "Kubernetes" not in generated
    assert any("Rejected AI rewrite" in warning for warning in result.resume.validation_warnings)

