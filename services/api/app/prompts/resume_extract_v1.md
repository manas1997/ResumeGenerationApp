# resume_extract_v1

Extract structured resume data from the source resume.

Rules:

- Preserve source wording for factual claims.
- Extract atomic claims with source spans whenever available.
- Do not infer missing employers, dates, metrics, skills, projects, or credentials.
- Return only schema-valid JSON.

