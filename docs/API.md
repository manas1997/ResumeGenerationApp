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
  "comparison": []
}
```

