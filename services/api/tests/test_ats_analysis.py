from app.services.ats_analysis import build_ats_analysis
from app.services.jd_parser import parse_job_description
from app.services.resume_parser import parse_resume_text
from app.services.scoring import compute_scorecard


def test_ats_analysis_separates_missing_weak_and_strong_skills() -> None:
    resume = parse_resume_text(
        """
SKILLS
Python, FastAPI, Kafka

EXPERIENCE
- Built production APIs with Python and FastAPI for customer workflows.
"""
    )
    jd = parse_job_description(
        """
Required: Python, FastAPI, Kafka, Kubernetes.
Responsible for building event-driven services.
"""
    )
    scorecard = compute_scorecard(resume, jd)

    analysis = build_ats_analysis(resume, jd, scorecard)

    assert any(item.skill == "python" for item in analysis.strongly_demonstrated_skills)
    assert any(item.skill == "kafka" for item in analysis.weakly_demonstrated_skills)
    assert any(item.skill == "kubernetes" for item in analysis.missing_skills)


def test_skill_improvement_report_uses_safe_evidence_based_language() -> None:
    resume = parse_resume_text("SKILLS\nPython\nEXPERIENCE\n- Built backend APIs with Python.")
    jd = parse_job_description("Required: Kubernetes and Kafka.")
    scorecard = compute_scorecard(resume, jd)

    analysis = build_ats_analysis(resume, jd, scorecard)
    combined_text = " ".join(
        [item.explanation for item in analysis.missing_skills]
        + analysis.gaps
        + analysis.skill_improvement_report.technical_skills_to_learn
    ).lower()

    assert "you do not know" not in combined_text
    assert "resume does not currently demonstrate" in combined_text

