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
- Template fidelity report for generated PDFs.
- In-browser PDF preview with page count, zoom, side-by-side comparison, and modified-section highlighting.
- Downloadable tailored resume PDF, original resume PDF, and ATS analysis report PDF.
- Version history with timestamp and associated Job Description.
- ATS dashboard and skill improvement report.

## Non-Negotiable Constraints

- Do not invent facts.
- Do not add unsupported skills, projects, certifications, dates, employers, metrics, or achievements.
- Every generated claim must reference source evidence.
- Unsupported JD keywords are recommendations or gaps, not inserted content.
- Estimate compatibility confidence; never claim guaranteed ATS pass rates.
- The source resume PDF is the master visual template.
- Production PDF output must preserve the original layout, styling, fonts, font sizes, spacing, margins, colors, alignment, headers, section order, and page design.
- The only visible differences between source PDF and generated PDF should be text content changes.
- Template preservation must not be violated to satisfy page limits.

## Template Preservation Requirements

The application is not allowed to redesign the resume, change formatting, change section styling, change typography, alter colors, adjust spacing, introduce new layouts, or change visual hierarchy.

Allowed modifications:

- Rewrite bullet points.
- Reorder bullets within an existing section.
- Replace text with ATS-optimized text.
- Add or remove existing supported keywords.
- Shorten content.
- Expand content only when it still fits inside the existing text regions.
- Remove less relevant content when page constraints require compression.

The system must calculate a template fidelity score before returning the generated PDF. Output is blocked unless fidelity is at least 99%.

Template fidelity validation checks:

- Font families.
- Font sizes.
- Margins.
- Section positions.
- Text-box positions.
- Spacing.
- Page count.
- Page dimensions.
- Colors.
- Alignment-sensitive visual structure.

## MVP Scope

- Resume upload and parsing.
- JD parsing.
- Claim extraction and grounding.
- Relevance scoring.
- Tailored resume generation.
- PDF export.
- Template-preserving PDF text replacement.
- Template fidelity scoring.
- Resume preview and download workflow.
- ATS analysis dashboard.
- Skill improvement recommendations that do not modify resume content.
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
- Template fidelity pass rate.
- Keyword coverage lift.
- User accepted rewrite percentage.
- Export success rate.
- Tailoring run latency.
- Cost per tailoring run.

## Preview And Download Requirements

After tailoring, the UI must display an in-browser PDF preview, page count, zoom controls, side-by-side original vs tailored comparison, and modified-section highlights.

Download options:

- Tailored Resume PDF.
- Original Resume PDF.
- ATS Analysis Report PDF.

Version history must retain previous resume generations, allow reopening older versions, and show the generation timestamp plus associated Job Description preview.

## ATS Analysis Engine

The ATS engine must perform:

- Keyword matching across JD and resume.
- Keyword coverage percentage.
- Skill gap analysis split into missing, weakly demonstrated, and strongly demonstrated skills.
- Experience gap analysis for JD responsibilities not evident in the resume.
- Formatting, section, readability, and ATS parsing validation.

Dashboard scores:

- ATS Compatibility Score.
- Keyword Match Score.
- Technical Skill Match.
- Experience Match.
- Leadership Match.
- Domain Match.

## Skill Improvement Recommendations

The Skill Improvement Recommendations section must not alter the resume. It provides future-growth guidance only:

- Technical Skills to Learn.
- Experience Areas to Build.
- Suggested Projects.
- Certification Suggestions.
- Interview Preparation Areas.

Safety rule: never say "You do not know X." Use wording like "The resume does not currently demonstrate experience with X" or "The Job Description places significant emphasis on X, but evidence of this skill is limited in the resume."
