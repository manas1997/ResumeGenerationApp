# Resume Generation App

Production-grade resume tailoring platform for generating ATS-friendly, recruiter-readable resumes from a source resume and a job description.

## Core Principle

The application must never invent user experience, projects, employers, skills, certifications, dates, metrics, or achievements. Every tailored resume claim is grounded in source resume evidence and traceable through `source_claim_ids`.

## Modules

- `apps/web`: Next.js frontend.
- `services/api`: FastAPI backend and resume intelligence engine.
- `packages/schemas`: Shared JSON schemas and cross-service contracts.
- `infra`: Docker, deployment, and infrastructure assets.
- `docs`: Product, architecture, and implementation documentation.

## Local Development

```bash
docker compose -f infra/docker/docker-compose.yml up --build
```

API:

```bash
cd services/api
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
export RESUME_APP_OPENAI_API_KEY="your-api-key"
uvicorn app.main:app --reload
```

AI rewriting is optional at runtime. Without `RESUME_APP_OPENAI_API_KEY`, the API uses the deterministic tailoring fallback. With the key set, the backend calls OpenAI through the AI gateway and validates every model rewrite before accepting it.

Web:

```bash
cd apps/web
npm install
npm run dev
```
