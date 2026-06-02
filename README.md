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
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Web:

```bash
cd apps/web
npm install
npm run dev
```

