import re

from app.schemas.ai import BulletRewrite, BulletRewriteResponse
from app.schemas.resume import ResumeClaim


NUMBER_RE = re.compile(r"\d+(?:[.,]\d+)?%?")


def validate_ai_rewrites(
    response: BulletRewriteResponse,
    allowed_claims: list[ResumeClaim],
    supported_keywords: list[str],
    jd_keywords: list[str],
) -> tuple[dict[str, BulletRewrite], list[str]]:
    claims_by_id = {claim.id: claim for claim in allowed_claims}
    supported = set(supported_keywords)
    unsupported_keywords = [keyword for keyword in jd_keywords if keyword not in supported]
    accepted: dict[str, BulletRewrite] = {}
    warnings: list[str] = []

    for rewrite in response.rewrites:
        claim = claims_by_id.get(rewrite.source_claim_id)
        if claim is None:
            warnings.append(f"Rejected AI rewrite for unknown claim {rewrite.source_claim_id}.")
            continue
        if rewrite.original_text.strip() != claim.text.strip():
            warnings.append(f"Rejected AI rewrite for original text mismatch on {claim.id}.")
            continue
        if not rewrite.rewritten_text.strip():
            warnings.append(f"Rejected empty AI rewrite for {claim.id}.")
            continue
        if _contains_unsupported_keyword(rewrite.rewritten_text, unsupported_keywords):
            warnings.append(f"Rejected AI rewrite with unsupported JD keyword for {claim.id}.")
            continue
        if not _numbers_are_supported(claim.text, rewrite.rewritten_text):
            warnings.append(f"Rejected AI rewrite with unsupported numeric claim for {claim.id}.")
            continue
        accepted[claim.id] = rewrite

    return accepted, warnings


def _contains_unsupported_keyword(text: str, unsupported_keywords: list[str]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in unsupported_keywords)


def _numbers_are_supported(original_text: str, rewritten_text: str) -> bool:
    original_numbers = set(NUMBER_RE.findall(original_text))
    rewritten_numbers = set(NUMBER_RE.findall(rewritten_text))
    return rewritten_numbers <= original_numbers

