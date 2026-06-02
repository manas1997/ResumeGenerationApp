# Product Requirements Document

## Product

Resume Generation App helps users create tailored, ATS-compatible resumes from a master resume and a job description while preserving factual integrity.

## Users

- Job seekers tailoring resumes for specific roles.
- Career coaches producing resume variants for clients.
- Internal mobility candidates adapting profiles to internal openings.

## Inputs

- Source resume: PDF, DOCX, or TXT.
- Job description text.
- Optional preferences: target role, seniority, years of experience, skills emphasis, tone.

## Outputs

- Parsed source resume JSON.
- Parsed job description JSON.
- Tailored resume JSON.
- ATS and recruiter scorecard.
- Original vs tailored comparison.
- DOCX and PDF exports.

## Non-Negotiable Constraints

- Do not invent facts.
- Do not add unsupported skills, projects, certifications, dates, employers, metrics, or achievements.
- Every generated claim must reference source evidence.
- Unsupported JD keywords are recommendations or gaps, not inserted content.
- Estimate compatibility confidence; never claim guaranteed ATS pass rates.

## MVP Scope

- Resume upload and parsing.
- JD parsing.
- Claim extraction and grounding.
- Relevance scoring.
- Tailored resume generation.
- PDF export.
- Scorecard and explanations.
- Version history.

## Out Of Scope For MVP

- Browser extension.
- Auto-apply workflows.
- Cover letter generation.
- Multi-language resume generation.
- Payment plans.
- Team administration.

## Success Metrics

- Source-grounding validation pass rate.
- Keyword coverage lift.
- User accepted rewrite percentage.
- Export success rate.
- Tailoring run latency.
- Cost per tailoring run.

