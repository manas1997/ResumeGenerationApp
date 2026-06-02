# bullet_rewrite_grounded_v1

Rewrite resume bullets using only allowed source claims.

Rules:

- Every output bullet must include `source_claim_ids`.
- Do not add unsupported skills, tools, employers, dates, projects, numbers, certifications, or achievements.
- If a JD keyword is unsupported, do not insert it.
- Improve action verbs and clarity while preserving factual meaning.
- Return only schema-valid JSON.

