from app.services.jd_parser import parse_job_description
from app.services.resume_parser import parse_resume_text
from app.services.scoring import compute_scorecard
from app.services.tailoring_engine import tailor_resume
from app.schemas.tailoring import TailoringPreferences


def test_tailoring_does_not_insert_unsupported_keyword() -> None:
    resume = parse_resume_text(
        """
SUMMARY
Backend engineer building APIs and distributed systems.

SKILLS
Python, FastAPI, PostgreSQL, Redis

EXPERIENCE
- Built FastAPI services backed by PostgreSQL and Redis for high-volume workflows.
"""
    )
    jd = parse_job_description(
        """
Required: Python, FastAPI, Kubernetes.
Preferred: PostgreSQL.
Build reliable backend services.
"""
    )

    scorecard = compute_scorecard(resume, jd)
    result = tailor_resume(resume, jd, TailoringPreferences(), scorecard)
    generated_text = " ".join(
        bullet.text for section in result.resume.sections for bullet in section.items
    ).lower()

    assert "kubernetes" not in generated_text
    assert any(missing.keyword == "kubernetes" for missing in scorecard.missing_keywords)


def test_scorecard_tracks_matched_keywords() -> None:
    resume = parse_resume_text("SKILLS\nPython, FastAPI\nEXPERIENCE\n- Built APIs with Python.")
    jd = parse_job_description("Required: Python and FastAPI.")
    scorecard = compute_scorecard(resume, jd)

    assert "python" in scorecard.matched_keywords
    assert "fastapi" in scorecard.matched_keywords
    assert scorecard.keyword_match_score == 100

