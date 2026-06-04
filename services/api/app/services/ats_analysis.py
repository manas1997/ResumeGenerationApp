from statistics import mean

from app.schemas.ats import (
    AtsAnalysisDashboard,
    AtsCompatibilityCheck,
    ExperienceGapItem,
    KeywordAnalysis,
    SkillGapItem,
    SkillImprovementReport,
)
from app.schemas.job_description import ParsedJobDescription
from app.schemas.resume import ParsedResume, ResumeClaim
from app.schemas.scorecard import Scorecard
from app.services.text_utils import jaccard_similarity, stable_unique


LEADERSHIP_TERMS = {
    "lead",
    "led",
    "mentor",
    "mentored",
    "own",
    "owned",
    "stakeholder",
    "roadmap",
    "strategy",
    "cross-functional",
    "manager",
}


def build_ats_analysis(
    resume: ParsedResume,
    jd: ParsedJobDescription,
    scorecard: Scorecard,
) -> AtsAnalysisDashboard:
    jd_keywords = stable_unique(jd.required_skills + jd.preferred_skills + jd.technologies)
    keyword_analysis = _keyword_analysis(resume, jd_keywords)
    skill_items = [_classify_skill(skill, resume) for skill in jd_keywords]
    experience_gaps = _experience_gaps(resume, jd)
    technical_skill_match = _technical_skill_match(skill_items)
    experience_match = _experience_match(experience_gaps)
    leadership_match = _leadership_match(resume, jd)
    domain_match = _domain_match(resume, jd)
    compatibility_checks = _compatibility_checks(resume, scorecard)

    missing_skills = [item for item in skill_items if item.level == "missing"]
    weak_skills = [item for item in skill_items if item.level == "weak"]
    strong_skills = [item for item in skill_items if item.level == "strong"]

    strengths = _strengths(strong_skills, resume)
    gaps = _gaps(missing_skills, weak_skills, experience_gaps)
    recommendations = _recommendations(missing_skills, weak_skills, experience_gaps)

    return AtsAnalysisDashboard(
        ats_compatibility_score=scorecard.ats_compatibility_score,
        keyword_match_score=scorecard.keyword_match_score,
        technical_skill_match=round(technical_skill_match, 2),
        experience_match=round(experience_match, 2),
        leadership_match=round(leadership_match, 2),
        domain_match=round(domain_match, 2),
        keyword_analysis=keyword_analysis,
        missing_skills=missing_skills,
        weakly_demonstrated_skills=weak_skills,
        strongly_demonstrated_skills=strong_skills,
        experience_gaps=experience_gaps,
        compatibility_checks=compatibility_checks,
        strengths=strengths,
        gaps=gaps,
        recommendations=recommendations,
        skill_improvement_report=_skill_improvement_report(
            missing_skills,
            weak_skills,
            experience_gaps,
            jd,
        ),
    )


def _keyword_analysis(resume: ParsedResume, jd_keywords: list[str]) -> KeywordAnalysis:
    resume_keywords = stable_unique(resume.skills)
    resume_text = resume.raw_text.lower()
    matched = [keyword for keyword in jd_keywords if keyword in resume_keywords or keyword in resume_text]
    missing = [keyword for keyword in jd_keywords if keyword not in matched]
    coverage = (len(matched) / len(jd_keywords) * 100) if jd_keywords else 100.0
    return KeywordAnalysis(
        jd_keywords=jd_keywords,
        resume_keywords=resume_keywords,
        matched_keywords=matched,
        missing_keywords=missing,
        coverage_percentage=round(coverage, 2),
    )


def _classify_skill(skill: str, resume: ParsedResume) -> SkillGapItem:
    evidence_claims = [
        claim
        for claim in resume.claims
        if skill in claim.normalized_terms or skill in claim.text.lower()
    ]
    applied_claims = [
        claim
        for claim in evidence_claims
        if claim.claim_type in {"experience", "project", "achievement"}
    ]

    if applied_claims:
        return SkillGapItem(
            skill=skill,
            level="strong",
            evidence_claim_ids=[claim.id for claim in applied_claims[:3]],
            explanation=f"The resume demonstrates {skill} through applied work evidence.",
        )
    if evidence_claims:
        return SkillGapItem(
            skill=skill,
            level="weak",
            evidence_claim_ids=[claim.id for claim in evidence_claims[:3]],
            explanation=(
                f"The Job Description places emphasis on {skill}, but evidence of this skill "
                "is limited in the resume."
            ),
        )
    return SkillGapItem(
        skill=skill,
        level="missing",
        evidence_claim_ids=[],
        explanation=f"The resume does not currently demonstrate experience with {skill}.",
    )


def _experience_gaps(resume: ParsedResume, jd: ParsedJobDescription) -> list[ExperienceGapItem]:
    evidence_claims = [claim for claim in resume.claims if claim.claim_type != "skill"]
    gaps: list[ExperienceGapItem] = []

    for expectation in jd.role_expectations[:10]:
        best_claim, best_score = _best_claim_match(expectation, evidence_claims)
        if best_score >= 0.22:
            level = "strong"
            explanation = "The resume includes relevant experience aligned to this responsibility."
        elif best_score >= 0.1:
            level = "weak"
            explanation = (
                "The Job Description emphasizes this responsibility, but evidence is limited "
                "in the resume."
            )
        else:
            level = "missing"
            explanation = (
                "The resume does not currently demonstrate this responsibility from the Job "
                "Description."
            )

        if level != "strong":
            gaps.append(
                ExperienceGapItem(
                    responsibility=expectation,
                    evidence_strength=level,
                    best_matching_claim_id=best_claim.id if best_claim else None,
                    explanation=explanation,
                )
            )
    return gaps


def _technical_skill_match(skill_items: list[SkillGapItem]) -> float:
    if not skill_items:
        return 100.0
    weights = {"strong": 1.0, "weak": 0.5, "missing": 0.0}
    return mean(weights[item.level] for item in skill_items) * 100


def _experience_match(experience_gaps: list[ExperienceGapItem]) -> float:
    if not experience_gaps:
        return 100.0
    weights = {"strong": 1.0, "weak": 0.5, "missing": 0.0}
    return mean(weights[item.evidence_strength] for item in experience_gaps) * 100


def _leadership_match(resume: ParsedResume, jd: ParsedJobDescription) -> float:
    jd_text = " ".join(jd.seniority_signals + jd.role_expectations).lower()
    if not any(term in jd_text for term in LEADERSHIP_TERMS):
        return 100.0
    resume_text = resume.raw_text.lower()
    matched_terms = [term for term in LEADERSHIP_TERMS if term in resume_text]
    return min(len(matched_terms) / 3 * 100, 100)


def _domain_match(resume: ParsedResume, jd: ParsedJobDescription) -> float:
    if not jd.domain_keywords:
        return 100.0
    resume_text = resume.raw_text.lower()
    matched = [keyword for keyword in jd.domain_keywords if keyword in resume_text]
    return len(matched) / len(jd.domain_keywords) * 100


def _compatibility_checks(
    resume: ParsedResume,
    scorecard: Scorecard,
) -> list[AtsCompatibilityCheck]:
    section_names = {section.normalized_name for section in resume.sections}
    checks = [
        AtsCompatibilityCheck(
            name="Formatting validation",
            status="warning" if "|" in resume.raw_text or "\t" in resume.raw_text else "pass",
            detail="Avoid tables, columns, tabs, icons, and text boxes for ATS parsing.",
        ),
        AtsCompatibilityCheck(
            name="Section validation",
            status="pass" if {"skills", "experience", "education"} <= section_names else "warning",
            detail="Resume should include standard Skills, Experience, and Education sections.",
        ),
        AtsCompatibilityCheck(
            name="Readability validation",
            status="pass" if scorecard.recruiter_readability_score >= 80 else "warning",
            detail="Bullets should be concise, evidence-backed, and easy to scan.",
        ),
        AtsCompatibilityCheck(
            name="ATS parsing validation",
            status="pass" if scorecard.ats_compatibility_score >= 85 else "warning",
            detail="Text extraction and section parsing confidence should remain high.",
        ),
    ]
    return checks


def _strengths(strong_skills: list[SkillGapItem], resume: ParsedResume) -> list[str]:
    strengths = [f"Strong evidence for {item.skill}." for item in strong_skills[:6]]
    if any(claim.claim_type == "achievement" for claim in resume.claims):
        strengths.append("Resume includes achievement-oriented evidence.")
    return strengths


def _gaps(
    missing_skills: list[SkillGapItem],
    weak_skills: list[SkillGapItem],
    experience_gaps: list[ExperienceGapItem],
) -> list[str]:
    gaps = [item.explanation for item in missing_skills[:5]]
    gaps.extend(item.explanation for item in weak_skills[:3])
    gaps.extend(item.explanation for item in experience_gaps[:3])
    return gaps[:10]


def _recommendations(
    missing_skills: list[SkillGapItem],
    weak_skills: list[SkillGapItem],
    experience_gaps: list[ExperienceGapItem],
) -> list[str]:
    recommendations: list[str] = []
    if weak_skills:
        recommendations.append("Add stronger evidence for weakly demonstrated skills when truthful.")
    if missing_skills:
        recommendations.append("Do not insert missing skills into the resume without real evidence.")
    if experience_gaps:
        recommendations.append("Build or document experience in the JD responsibility areas.")
    return recommendations


def _skill_improvement_report(
    missing_skills: list[SkillGapItem],
    weak_skills: list[SkillGapItem],
    experience_gaps: list[ExperienceGapItem],
    jd: ParsedJobDescription,
) -> SkillImprovementReport:
    technical_skills = [item.skill for item in missing_skills[:8]]
    experience_areas = [
        gap.responsibility
        for gap in experience_gaps
        if gap.evidence_strength in {"missing", "weak"}
    ][:6]

    return SkillImprovementReport(
        technical_skills_to_learn=technical_skills,
        experience_areas_to_build=experience_areas,
        suggested_projects=_suggested_projects(technical_skills, experience_areas),
        certification_suggestions=_certification_suggestions(jd, technical_skills),
        interview_preparation_areas=_interview_areas(jd, missing_skills, weak_skills),
    )


def _suggested_projects(skills: list[str], experience_areas: list[str]) -> list[str]:
    projects: list[str] = []
    if any("kafka" in skill for skill in skills):
        projects.append("Build an event-driven order processing system.")
    if any("kubernetes" in skill for skill in skills):
        projects.append("Deploy a production-style service on Kubernetes with health checks.")
    if any("aws" in skill for skill in skills):
        projects.append("Build and deploy a cloud-native API with managed storage and monitoring.")
    if experience_areas:
        projects.append("Build a distributed job scheduler with retries, ownership metrics, and observability.")
    return projects[:5]


def _certification_suggestions(jd: ParsedJobDescription, skills: list[str]) -> list[str]:
    text = " ".join(jd.technologies + skills).lower()
    suggestions: list[str] = []
    if "aws" in text:
        suggestions.append("Relevant AWS cloud certification.")
    if "azure" in text:
        suggestions.append("Relevant Azure cloud certification.")
    if "gcp" in text or "google cloud" in text:
        suggestions.append("Relevant Google Cloud certification.")
    if "kubernetes" in text:
        suggestions.append("Relevant Kubernetes certification.")
    return suggestions or ["Relevant cloud or technology certification aligned to the target role."]


def _interview_areas(
    jd: ParsedJobDescription,
    missing_skills: list[SkillGapItem],
    weak_skills: list[SkillGapItem],
) -> list[str]:
    areas = ["System Design", "Distributed Systems", "Concurrency"]
    if jd.domain_keywords:
        areas.append("Domain-specific concepts")
    if missing_skills or weak_skills:
        areas.append("Technical depth for JD-emphasized skills")
    return areas


def _best_claim_match(
    text: str,
    claims: list[ResumeClaim],
) -> tuple[ResumeClaim | None, float]:
    if not claims:
        return None, 0.0
    scored = [(claim, jaccard_similarity(text, claim.text)) for claim in claims]
    return max(scored, key=lambda item: item[1])

