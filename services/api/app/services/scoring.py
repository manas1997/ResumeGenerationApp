from statistics import mean

from app.schemas.job_description import ParsedJobDescription
from app.schemas.resume import ParsedResume
from app.schemas.scorecard import MissingKeyword, Scorecard
from app.services.text_utils import jaccard_similarity, stable_unique


def compute_scorecard(resume: ParsedResume, jd: ParsedJobDescription) -> Scorecard:
    resume_terms = set(resume.skills)
    resume_text = resume.raw_text.lower()
    jd_terms = stable_unique(jd.required_skills + jd.preferred_skills + jd.technologies)

    matched = sorted(term for term in jd_terms if term in resume_terms or term in resume_text)
    missing = [term for term in jd_terms if term not in matched]

    keyword_score = _weighted_keyword_score(resume, jd)
    semantic_score = _semantic_score(resume, jd)
    ats_score = _ats_score(resume)
    readability_score = _readability_score(resume)

    recommendations: list[str] = []
    if missing:
        recommendations.append("Review unsupported JD keywords before adding them to the resume.")
    if keyword_score < 70:
        recommendations.append("Prioritize supported skills and experiences that map directly to the JD.")
    if ats_score < 85:
        recommendations.append("Use standard headings, simple bullets, and single-column formatting.")
    if readability_score < 80:
        recommendations.append("Prefer concise bullets with clear action verbs and evidence-backed outcomes.")

    return Scorecard(
        keyword_match_score=round(keyword_score, 2),
        semantic_alignment_score=round(semantic_score, 2),
        ats_compatibility_score=round(ats_score, 2),
        recruiter_readability_score=round(readability_score, 2),
        compatibility_confidence=_confidence(keyword_score, semantic_score, ats_score, readability_score),
        matched_keywords=matched,
        missing_keywords=[
            MissingKeyword(
                keyword=keyword,
                support_status="unsupported",
                reason="The keyword appears in the JD but was not detected in source resume evidence.",
            )
            for keyword in missing
        ],
        improvement_recommendations=recommendations,
    )


def _weighted_keyword_score(resume: ParsedResume, jd: ParsedJobDescription) -> float:
    required = jd.required_skills or jd.technologies
    preferred = jd.preferred_skills
    resume_terms = set(resume.skills)
    resume_text = resume.raw_text.lower()

    def covered(term: str) -> bool:
        return term in resume_terms or term in resume_text

    required_total = len(required) * 2
    preferred_total = len(preferred)
    total = required_total + preferred_total
    if total == 0:
        return 75.0

    score = sum(2 for term in required if covered(term)) + sum(1 for term in preferred if covered(term))
    return (score / total) * 100


def _semantic_score(resume: ParsedResume, jd: ParsedJobDescription) -> float:
    if not resume.claims or not jd.requirements:
        return 0.0

    per_requirement: list[float] = []
    for requirement in jd.requirements[:30]:
        best = max(
            jaccard_similarity(requirement.text, claim.text)
            for claim in resume.claims
            if claim.claim_type != "skill"
        ) if resume.claims else 0.0
        per_requirement.append(best)

    return min(mean(per_requirement) * 250, 100) if per_requirement else 0.0


def _ats_score(resume: ParsedResume) -> float:
    section_names = {section.normalized_name for section in resume.sections}
    expected_sections = {"skills", "experience", "education"}
    section_score = len(section_names & expected_sections) / len(expected_sections) * 45
    bullet_score = 20 if any("-" in claim.text or claim.claim_type == "experience" for claim in resume.claims) else 10
    table_penalty = 10 if "|" in resume.raw_text or "\t" in resume.raw_text else 0
    parseability_score = 35 if resume.claims else 10
    return max(0, min(section_score + bullet_score + parseability_score - table_penalty, 100))


def _readability_score(resume: ParsedResume) -> float:
    non_skill_claims = [claim for claim in resume.claims if claim.claim_type != "skill"]
    if not non_skill_claims:
        return 50.0

    concise = [claim for claim in non_skill_claims if 45 <= len(claim.text) <= 220]
    metric_backed = [claim for claim in non_skill_claims if any(char.isdigit() for char in claim.text)]
    concise_score = len(concise) / len(non_skill_claims) * 65
    metric_score = min(len(metric_backed) / max(len(non_skill_claims), 1) * 35, 35)
    return min(concise_score + metric_score, 100)


def _confidence(*scores: float) -> str:
    average = mean(scores)
    if average >= 85:
        return "high"
    if average >= 65:
        return "medium"
    return "low"

