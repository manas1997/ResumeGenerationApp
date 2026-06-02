import re

from app.schemas.resume import ParsedResume, ResumeClaim, ResumeSection, SourceSpan
from app.services.taxonomy import SECTION_ALIASES
from app.services.text_utils import clean_text, extract_terms, stable_unique


BULLET_RE = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+(?P<text>.+)$")


def parse_resume_text(raw_text: str) -> ParsedResume:
    normalized_text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    sections = _extract_sections(normalized_text)
    skills = stable_unique(_extract_skills(normalized_text, sections))
    claims = _extract_claims(normalized_text, sections, skills)
    return ParsedResume(
        raw_text=raw_text,
        sections=sections,
        skills=skills,
        claims=claims,
    )


def _extract_sections(text: str) -> list[ResumeSection]:
    headings: list[tuple[int, int, str, str]] = []
    for match in re.finditer(r"(?im)^\s*([A-Z][A-Z /&-]{2,}|[A-Z][a-zA-Z /&-]{2,})\s*$", text):
        heading = clean_text(match.group(1)).lower()
        normalized = SECTION_ALIASES.get(heading)
        if normalized:
            headings.append((match.start(), match.end(), match.group(1).strip(), normalized))

    if not headings:
        return [
            ResumeSection(
                name="Resume",
                normalized_name="resume",
                content=text.strip(),
                source_span=SourceSpan(start=0, end=len(text)),
            )
        ]

    sections: list[ResumeSection] = []
    for index, (heading_start, heading_end, heading, normalized) in enumerate(headings):
        next_start = headings[index + 1][0] if index + 1 < len(headings) else len(text)
        content = text[heading_end:next_start].strip()
        sections.append(
            ResumeSection(
                name=heading,
                normalized_name=normalized,
                content=content,
                source_span=SourceSpan(start=heading_start, end=next_start),
            )
        )
    return sections


def _extract_skills(text: str, sections: list[ResumeSection]) -> list[str]:
    skills = extract_terms(text)
    skill_sections = [section for section in sections if section.normalized_name == "skills"]
    for section in skill_sections:
        fragments = re.split(r"[,|;•\n]", section.content)
        skills.extend(fragment.strip() for fragment in fragments if len(fragment.strip()) > 1)
    return skills


def _extract_claims(
    text: str,
    sections: list[ResumeSection],
    skills: list[str],
) -> list[ResumeClaim]:
    claims: list[ResumeClaim] = []

    for skill in skills:
        match = re.search(re.escape(skill), text, flags=re.IGNORECASE)
        if not match:
            continue
        claims.append(
            ResumeClaim(
                id=f"claim_{len(claims) + 1:04d}",
                claim_type="skill",
                text=skill,
                normalized_terms=[skill],
                source_section="skills",
                source_span=SourceSpan(start=match.start(), end=match.end()),
                confidence=0.9,
            )
        )

    for section in sections:
        section_type = _section_to_claim_type(section.normalized_name)
        lines = [line.strip() for line in section.content.splitlines() if line.strip()]
        for line in lines:
            bullet = BULLET_RE.match(line)
            claim_text = bullet.group("text") if bullet else line
            if len(claim_text) < 24 and section_type not in {"education", "certification"}:
                continue
            start = text.find(claim_text, section.source_span.start, section.source_span.end)
            if start < 0:
                start = section.source_span.start
            claims.append(
                ResumeClaim(
                    id=f"claim_{len(claims) + 1:04d}",
                    claim_type=section_type,
                    text=clean_text(claim_text),
                    normalized_terms=extract_terms(claim_text),
                    source_section=section.normalized_name,
                    source_span=SourceSpan(start=start, end=start + len(claim_text)),
                    confidence=0.8 if bullet else 0.65,
                )
            )
    return claims


def _section_to_claim_type(section_name: str):
    mapping = {
        "summary": "summary",
        "skills": "skill",
        "experience": "experience",
        "projects": "project",
        "education": "education",
        "certifications": "certification",
        "achievements": "achievement",
    }
    return mapping.get(section_name, "experience")

