import re

from app.schemas.job_description import JobRequirement, ParsedJobDescription
from app.services.taxonomy import ACTION_VERBS
from app.services.text_utils import clean_text, extract_terms, stable_unique


REQUIRED_MARKERS = ("required", "must", "need", "minimum", "proficient", "strong")
PREFERRED_MARKERS = ("preferred", "nice to have", "bonus", "plus", "familiarity")
SENIORITY_TERMS = ("senior", "staff", "principal", "lead", "manager", "director", "junior", "entry")


def parse_job_description(raw_text: str) -> ParsedJobDescription:
    cleaned = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [clean_text(line) for line in cleaned.splitlines() if clean_text(line)]
    all_terms = extract_terms(cleaned)
    required = _extract_marked_terms(lines, REQUIRED_MARKERS)
    preferred = _extract_marked_terms(lines, PREFERRED_MARKERS)
    technologies = stable_unique(all_terms)
    years = _extract_years(cleaned)
    role_expectations = _extract_expectations(lines)
    domain_keywords = _extract_domain_keywords(cleaned, technologies)
    action_verbs = sorted({verb for verb in ACTION_VERBS if re.search(rf"\b{verb}\b", cleaned, re.I)})
    seniority_signals = sorted({term for term in SENIORITY_TERMS if re.search(rf"\b{term}\b", cleaned, re.I)})

    requirements = _build_requirements(
        required_skills=required,
        preferred_skills=preferred,
        technologies=technologies,
        role_expectations=role_expectations,
        domain_keywords=domain_keywords,
        action_verbs=action_verbs,
        seniority_signals=seniority_signals,
    )

    return ParsedJobDescription(
        raw_text=raw_text,
        required_skills=required,
        preferred_skills=preferred,
        technologies=technologies,
        years_of_experience=years,
        role_expectations=role_expectations,
        domain_keywords=domain_keywords,
        action_verbs=action_verbs,
        seniority_signals=seniority_signals,
        requirements=requirements,
    )


def _extract_marked_terms(lines: list[str], markers: tuple[str, ...]) -> list[str]:
    terms: list[str] = []
    for line in lines:
        if any(marker in line.lower() for marker in markers):
            terms.extend(extract_terms(line))
    return stable_unique(terms)


def _extract_years(text: str) -> int | None:
    matches = re.findall(r"(\d+)\+?\s*(?:years|yrs)", text, flags=re.IGNORECASE)
    if not matches:
        return None
    return max(int(match) for match in matches)


def _extract_expectations(lines: list[str]) -> list[str]:
    expectation_markers = ("responsible", "build", "design", "develop", "lead", "own", "deliver")
    expectations: list[str] = []
    for line in lines:
        lowered = line.lower()
        if any(marker in lowered for marker in expectation_markers) and len(line) > 32:
            expectations.append(line)
    return expectations[:12]


def _extract_domain_keywords(text: str, technologies: list[str]) -> list[str]:
    tokens = re.findall(r"\b[a-zA-Z][a-zA-Z-]{4,}\b", text.lower())
    stop_words = {
        "experience",
        "required",
        "preferred",
        "skills",
        "working",
        "years",
        "teams",
        "using",
        "strong",
        "knowledge",
        "ability",
        "responsibilities",
    }
    keywords = [
        token
        for token in tokens
        if token not in stop_words and token not in technologies and not token.endswith("ing")
    ]
    return stable_unique(keywords)[:20]


def _build_requirements(
    required_skills: list[str],
    preferred_skills: list[str],
    technologies: list[str],
    role_expectations: list[str],
    domain_keywords: list[str],
    action_verbs: list[str],
    seniority_signals: list[str],
) -> list[JobRequirement]:
    requirements: list[JobRequirement] = []

    def add(requirement_type, text, normalized_value, priority, confidence=0.75):
        requirements.append(
            JobRequirement(
                id=f"req_{len(requirements) + 1:04d}",
                requirement_type=requirement_type,
                text=text,
                normalized_value=normalized_value,
                priority=priority,
                confidence=confidence,
            )
        )

    for skill in required_skills:
        add("required_skill", skill, skill, 5, 0.85)
    for skill in preferred_skills:
        add("preferred_skill", skill, skill, 3, 0.75)
    for technology in technologies:
        if technology not in required_skills and technology not in preferred_skills:
            add("technology", technology, technology, 2, 0.7)
    for expectation in role_expectations:
        add("responsibility", expectation, expectation.lower(), 3, 0.65)
    for keyword in domain_keywords:
        add("domain_keyword", keyword, keyword, 1, 0.55)
    for verb in action_verbs:
        add("action_verb", verb, verb, 1, 0.55)
    for signal in seniority_signals:
        add("seniority_signal", signal, signal, 2, 0.65)

    return requirements

