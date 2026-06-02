import re

from app.services.taxonomy import SKILL_ALIASES


WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+#./-]*")


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def normalize_term(value: str) -> str:
    normalized = clean_text(value).lower()
    normalized = normalized.strip(".,;:()[]{}")
    return SKILL_ALIASES.get(normalized, normalized)


def extract_terms(text: str) -> list[str]:
    haystack = f" {text.lower()} "
    terms: set[str] = set()
    for alias, canonical in SKILL_ALIASES.items():
        pattern = rf"(?<![a-zA-Z0-9]){re.escape(alias)}(?![a-zA-Z0-9])"
        if re.search(pattern, haystack):
            terms.add(canonical)
    return sorted(terms)


def tokenize(text: str) -> set[str]:
    stop_words = {
        "and",
        "or",
        "the",
        "a",
        "an",
        "to",
        "of",
        "for",
        "in",
        "with",
        "on",
        "by",
        "as",
        "is",
        "are",
        "be",
        "will",
        "you",
        "we",
    }
    return {word.lower() for word in WORD_RE.findall(text) if word.lower() not in stop_words}


def jaccard_similarity(left: str, right: str) -> float:
    left_tokens = tokenize(left)
    right_tokens = tokenize(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def stable_unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = normalize_term(value)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result

