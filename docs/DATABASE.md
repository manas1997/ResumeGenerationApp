# Database Schema

Initial production schema targets PostgreSQL. IDs are UUIDs unless noted.

```sql
create table users (
  id uuid primary key,
  email text not null unique,
  auth_provider text not null,
  created_at timestamptz not null default now()
);

create table source_documents (
  id uuid primary key,
  user_id uuid not null references users(id),
  file_url text not null,
  file_type text not null,
  checksum text not null,
  status text not null,
  created_at timestamptz not null default now()
);

create table resumes (
  id uuid primary key,
  user_id uuid not null references users(id),
  title text not null,
  active_version_id uuid,
  created_at timestamptz not null default now()
);

create table resume_versions (
  id uuid primary key,
  resume_id uuid not null references resumes(id),
  source_document_id uuid references source_documents(id),
  structured_json jsonb not null,
  created_at timestamptz not null default now()
);

create table resume_claims (
  id uuid primary key,
  resume_version_id uuid not null references resume_versions(id),
  claim_type text not null,
  text text not null,
  normalized_terms jsonb not null default '[]',
  source_section text not null,
  source_span jsonb not null,
  confidence numeric(4, 3) not null,
  created_at timestamptz not null default now()
);

create table job_descriptions (
  id uuid primary key,
  user_id uuid not null references users(id),
  title text,
  company text,
  raw_text text not null,
  parsed_json jsonb not null,
  created_at timestamptz not null default now()
);

create table tailoring_runs (
  id uuid primary key,
  user_id uuid not null references users(id),
  resume_version_id uuid not null references resume_versions(id),
  job_description_id uuid not null references job_descriptions(id),
  preferences_json jsonb not null default '{}',
  status text not null,
  created_at timestamptz not null default now(),
  completed_at timestamptz
);

create table generated_resumes (
  id uuid primary key,
  tailoring_run_id uuid not null references tailoring_runs(id),
  tailored_json jsonb not null,
  docx_url text,
  pdf_url text,
  template_id text not null,
  created_at timestamptz not null default now()
);

create table scorecards (
  id uuid primary key,
  tailoring_run_id uuid not null references tailoring_runs(id),
  keyword_match_score numeric(5, 2) not null,
  semantic_alignment_score numeric(5, 2) not null,
  ats_compatibility_score numeric(5, 2) not null,
  recruiter_readability_score numeric(5, 2) not null,
  missing_keywords_json jsonb not null default '[]',
  created_at timestamptz not null default now()
);

create table change_logs (
  id uuid primary key,
  tailoring_run_id uuid not null references tailoring_runs(id),
  original_text text not null,
  tailored_text text not null,
  source_claim_ids jsonb not null,
  jd_keywords jsonb not null default '[]',
  reason text not null,
  created_at timestamptz not null default now()
);

create table ai_runs (
  id uuid primary key,
  tailoring_run_id uuid references tailoring_runs(id),
  prompt_name text not null,
  model text not null,
  input_hash text not null,
  output_json jsonb,
  latency_ms integer,
  cost_estimate numeric(10, 6),
  created_at timestamptz not null default now()
);
```

Recommended indexes:

```sql
create index idx_resume_claims_resume_version on resume_claims(resume_version_id);
create index idx_tailoring_runs_user on tailoring_runs(user_id, created_at desc);
create index idx_generated_resumes_run on generated_resumes(tailoring_run_id);
create index idx_job_descriptions_user on job_descriptions(user_id, created_at desc);
```

