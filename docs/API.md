# API Contracts

## Create Tailoring Run

`POST /api/v1/tailoring-runs`

```json
{
  "source_resume": {
    "raw_text": "string"
  },
  "job_description": {
    "raw_text": "string"
  },
  "preferences": {
    "target_role": "Senior Backend Engineer",
    "seniority": "senior",
    "years_of_experience": 8,
    "skills_emphasis": ["Python", "FastAPI", "AWS"]
  }
}
```

## Response

```json
{
  "run_id": "uuid",
  "tailored_resume": {},
  "scorecard": {},
  "ats_analysis": {
    "ats_compatibility_score": 88,
    "keyword_match_score": 76,
    "technical_skill_match": 72,
    "experience_match": 68,
    "leadership_match": 80,
    "domain_match": 70,
    "strengths": [],
    "gaps": [],
    "recommendations": [],
    "skill_improvement_report": {}
  },
  "output_assets": {
    "tailored_resume_pdf_url": null,
    "original_resume_pdf_url": null,
    "ats_report_pdf_url": null,
    "tailored_page_count": null,
    "original_page_count": null
  },
  "comparison": []
}
```

## Template-Preserved PDF Export

Production PDF export must use the source PDF as the visual template.

`POST /api/v1/generated-resumes/{id}/export/pdf`

Planned request shape:

```json
{
  "source_document_id": "uuid",
  "replacement_strategy": "text_only",
  "template_fidelity_threshold": 99
}
```

Planned response shape:

```json
{
  "pdf_url": "signed-url",
  "template_fidelity": {
    "overall_score": 99.4,
    "font_score": 100,
    "margin_score": 100,
    "spacing_score": 99,
    "position_score": 99,
    "page_structure_score": 99,
    "passed": true,
    "threshold": 99,
    "violations": []
  }
}
```

If fidelity is below threshold, the API must return a validation failure and recommendations for text compression. It must not return a redesigned PDF.

## ATS Analysis Dashboard

Returned as part of `TailoringResponse.ats_analysis`.

The dashboard separates:

- Missing skills.
- Weakly demonstrated skills.
- Strongly demonstrated skills.
- Experience gaps.
- Compatibility checks.
- Strengths.
- Gaps.
- Recommendations.
- Skill improvement recommendations.

Skill improvement recommendations must never claim the user does not know a skill. They must speak only about evidence currently demonstrated in the resume.
