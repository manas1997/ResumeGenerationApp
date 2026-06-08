from dataclasses import dataclass

from app.ai.gateway import AIProvider
from app.schemas.ai import BulletRewrite, BulletRewriteResponse
from app.schemas.job_description import ParsedJobDescription
from app.schemas.resume import ParsedResume, ResumeClaim, TailoredBullet, TailoredResume, TailoredSection
from app.schemas.scorecard import Scorecard
from app.schemas.tailoring import ChangeExplanation, TailoringPreferences
from app.services.ai_rewrite_validator import validate_ai_rewrites
from app.services.text_utils import clean_text, jaccard_similarity, stable_unique


_BULLET_REWRITE_SYSTEM_PROMPT = """
You rewrite resume bullets for ATS and recruiter readability.

Rules:
- Use only facts from allowed_claims.
- Do not invent employers, titles, dates, metrics, skills, tools, certifications, or projects.
- Do not add unsupported JD keywords.
- Every rewrite must keep the original source_claim_id.
- Every rewrite must preserve factual meaning.
- If a claim cannot be improved safely, return the original text as rewritten_text.
- Return structured JSON only.
"""


@dataclass(frozen=True)
class TailoringResult:
    resume: TailoredResume
    comparison: list[ChangeExplanation]


def tailor_resume(
    resume: ParsedResume,
    jd: ParsedJobDescription,
    preferences: TailoringPreferences,
    scorecard: Scorecard,
    ai_provider: AIProvider | None = None,
) -> TailoringResult:
    jd_keywords = stable_unique(jd.required_skills + jd.preferred_skills + jd.technologies)
    supported_keywords = [keyword for keyword in jd_keywords if keyword in scorecard.matched_keywords]
    ranked_claims = _rank_claims(resume.claims, jd)

    summary = _build_summary(resume, ranked_claims, supported_keywords, preferences)
    skills = _rank_skills(resume.skills, supported_keywords, preferences.skills_emphasis)
    sections, comparison, ai_warnings = _build_sections(
        ranked_claims,
        supported_keywords,
        jd,
        preferences,
        ai_provider,
    )
    warnings = _validation_warnings(scorecard) + ai_warnings

    return TailoringResult(
        resume=TailoredResume(
            summary=summary,
            skills=skills,
            sections=sections,
            validation_warnings=warnings,
        ),
        comparison=comparison,
    )


def _rank_claims(claims: list[ResumeClaim], jd: ParsedJobDescription) -> list[ResumeClaim]:
    requirements_text = "\n".join(requirement.text for requirement in jd.requirements)

    def relevance(claim: ResumeClaim) -> tuple[float, int]:
        term_overlap = len(set(claim.normalized_terms) & set(jd.technologies + jd.required_skills))
        semantic = jaccard_similarity(claim.text, requirements_text)
        type_weight = 2 if claim.claim_type in {"experience", "project", "achievement"} else 1
        return (term_overlap * 10 + semantic * 10 + type_weight, -claim.source_span.start)

    return sorted(claims, key=relevance, reverse=True)


def _build_summary(
    resume: ParsedResume,
    ranked_claims: list[ResumeClaim],
    supported_keywords: list[str],
    preferences: TailoringPreferences,
) -> list[TailoredBullet]:
    existing_summary = [claim for claim in resume.claims if claim.claim_type == "summary"]
    source = existing_summary[:2] or [
        claim for claim in ranked_claims if claim.claim_type in {"experience", "project", "achievement"}
    ][:2]
    bullets: list[TailoredBullet] = []
    for claim in source:
        keywords = _keywords_for_claim(claim, supported_keywords)
        text = _polish_bullet(claim.text)
        if preferences.target_role and keywords:
            text = f"{text} Relevant focus: {', '.join(keywords[:4])}."
        bullets.append(TailoredBullet(text=text, source_claim_ids=[claim.id], jd_keywords=keywords))
    return bullets[:3]


def _rank_skills(
    resume_skills: list[str],
    supported_keywords: list[str],
    emphasis: list[str],
) -> list[str]:
    emphasis_normalized = stable_unique(emphasis)
    ordered = []
    ordered.extend(skill for skill in emphasis_normalized if skill in resume_skills)
    ordered.extend(skill for skill in supported_keywords if skill in resume_skills and skill not in ordered)
    ordered.extend(skill for skill in resume_skills if skill not in ordered)
    return ordered[:32]


def _build_sections(
    ranked_claims: list[ResumeClaim],
    supported_keywords: list[str],
    jd: ParsedJobDescription,
    preferences: TailoringPreferences,
    ai_provider: AIProvider | None,
) -> tuple[list[TailoredSection], list[ChangeExplanation], list[str]]:
    grouped: dict[str, list[TailoredBullet]] = {
        "Experience": [],
        "Projects": [],
        "Education": [],
        "Certifications": [],
        "Achievements": [],
    }
    comparison: list[ChangeExplanation] = []
    selected_claims = _select_section_claims(ranked_claims)
    jd_keywords = stable_unique(jd.required_skills + jd.preferred_skills + jd.technologies)
    ai_rewrites, ai_warnings = _rewrite_claims_with_ai(
        selected_claims,
        supported_keywords,
        jd_keywords,
        jd,
        preferences,
        ai_provider,
    )

    for claim in selected_claims:
        section_name = _section_name(claim.claim_type)
        keywords = _keywords_for_claim(claim, supported_keywords)
        rewrite = ai_rewrites.get(claim.id)
        tailored_text = rewrite.rewritten_text if rewrite else _polish_bullet(claim.text)
        grouped[section_name].append(
            TailoredBullet(
                text=tailored_text,
                source_claim_ids=[claim.id],
                jd_keywords=rewrite.jd_keywords if rewrite else keywords,
            )
        )
        comparison.append(
            ChangeExplanation(
                original_text=claim.text,
                tailored_text=tailored_text,
                source_claim_ids=[claim.id],
                jd_keywords=rewrite.jd_keywords if rewrite else keywords,
                reason=(
                    rewrite.change_reason
                    if rewrite
                    else "Prioritized and polished because the source claim overlaps with JD language."
                ),
                recruiter_benefit=(
                    rewrite.recruiter_benefit
                    if rewrite
                    else "Makes the most relevant evidence easier to scan."
                ),
                ats_benefit=(
                    rewrite.ats_benefit
                    if rewrite
                    else "Surfaces supported JD keywords without adding unsupported claims."
                ),
            )
        )

    return (
        [TailoredSection(name=name, items=items) for name, items in grouped.items() if items],
        comparison,
        ai_warnings,
    )


def _select_section_claims(ranked_claims: list[ResumeClaim]) -> list[ResumeClaim]:
    counts: dict[str, int] = {}
    selected: list[ResumeClaim] = []
    for claim in ranked_claims:
        if claim.claim_type in {"skill", "summary"}:
            continue
        section_name = _section_name(claim.claim_type)
        if counts.get(section_name, 0) >= _section_limit(section_name):
            continue
        selected.append(claim)
        counts[section_name] = counts.get(section_name, 0) + 1
    return selected


def _rewrite_claims_with_ai(
    selected_claims: list[ResumeClaim],
    supported_keywords: list[str],
    jd_keywords: list[str],
    jd: ParsedJobDescription,
    preferences: TailoringPreferences,
    ai_provider: AIProvider | None,
) -> tuple[dict[str, BulletRewrite], list[str]]:
    if ai_provider is None or not selected_claims:
        return {}, []

    payload = {
        "allowed_claims": [
            {
                "source_claim_id": claim.id,
                "claim_type": claim.claim_type,
                "original_text": claim.text,
                "supported_terms": claim.normalized_terms,
            }
            for claim in selected_claims
        ],
        "supported_jd_keywords": supported_keywords,
        "candidate_jd_keywords": jd_keywords,
        "role_expectations": jd.role_expectations,
        "target_role": preferences.target_role,
        "seniority": preferences.seniority,
        "requirements": [
            "Rewrite only when the result is clearer or better aligned.",
            "Keep every rewrite truthful and grounded in allowed_claims.",
            "Return one item per allowed claim.",
        ],
    }

    try:
        response = ai_provider.structured_completion(
            prompt_name="bullet_rewrite_grounded_v1",
            system_prompt=_BULLET_REWRITE_SYSTEM_PROMPT,
            user_payload=payload,
            schema=BulletRewriteResponse,
        )
    except Exception as exc:
        return {}, [f"AI rewriting unavailable; deterministic fallback used ({exc.__class__.__name__})."]

    rewrites, warnings = validate_ai_rewrites(
        response=response,  # type: ignore[arg-type]
        allowed_claims=selected_claims,
        supported_keywords=supported_keywords,
        jd_keywords=jd_keywords,
    )
    return rewrites, warnings


def _polish_bullet(text: str) -> str:
    cleaned = clean_text(text).rstrip(".")
    if not cleaned:
        return cleaned
    first_word = cleaned.split(" ", 1)[0].lower()
    if first_word in {"responsible", "worked", "helped"}:
        cleaned = cleaned[0].upper() + cleaned[1:]
    else:
        cleaned = cleaned[0].upper() + cleaned[1:]
    return f"{cleaned}."


def _keywords_for_claim(claim: ResumeClaim, supported_keywords: list[str]) -> list[str]:
    claim_text = claim.text.lower()
    return [keyword for keyword in supported_keywords if keyword in claim.normalized_terms or keyword in claim_text]


def _section_name(claim_type: str) -> str:
    mapping = {
        "experience": "Experience",
        "project": "Projects",
        "education": "Education",
        "certification": "Certifications",
        "achievement": "Achievements",
    }
    return mapping.get(claim_type, "Experience")


def _section_limit(section_name: str) -> int:
    return {
        "Experience": 10,
        "Projects": 5,
        "Education": 4,
        "Certifications": 6,
        "Achievements": 6,
    }.get(section_name, 6)


def _validation_warnings(scorecard: Scorecard) -> list[str]:
    return [
        f"Unsupported JD keyword not inserted: {missing.keyword}"
        for missing in scorecard.missing_keywords
        if missing.support_status == "unsupported"
    ]
