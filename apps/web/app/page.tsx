"use client";

import {
  AlertTriangle,
  Columns2,
  Download,
  FileText,
  RotateCcw,
  Wand2,
  ZoomIn,
  ZoomOut
} from "lucide-react";
import { FormEvent, useEffect, useMemo, useState } from "react";

import { ScoreMeter } from "@/components/ScoreMeter";
import { createTailoringRun } from "@/lib/api";
import type { TailoringResponse } from "@/types/tailoring";

type VersionHistoryItem = {
  runId: string;
  createdAt: string;
  jobDescriptionPreview: string;
  result: TailoringResponse;
};

export default function Home() {
  const [resumeText, setResumeText] = useState("");
  const [jdText, setJdText] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [seniority, setSeniority] = useState("");
  const [years, setYears] = useState("");
  const [skills, setSkills] = useState("");
  const [result, setResult] = useState<TailoringResponse | null>(null);
  const [versionHistory, setVersionHistory] = useState<VersionHistoryItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const stored = window.localStorage.getItem("resume-generation-versions");
    if (stored) {
      setVersionHistory(JSON.parse(stored));
    }
  }, []);

  const canSubmit = useMemo(() => resumeText.trim().length > 0 && jdText.trim().length > 0, [
    resumeText,
    jdText
  ]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!canSubmit) return;

    setError(null);
    setIsLoading(true);

    try {
      const response = await createTailoringRun({
        source_resume: { raw_text: resumeText },
        job_description: { raw_text: jdText },
        preferences: {
          target_role: targetRole || undefined,
          seniority: seniority || undefined,
          years_of_experience: years ? Number(years) : undefined,
          skills_emphasis: skills
            .split(",")
            .map((skill) => skill.trim())
            .filter(Boolean),
          tone: "professional"
        }
      });
      setResult(response);
      const nextHistory = [
        {
          runId: response.run_id,
          createdAt: new Date().toISOString(),
          jobDescriptionPreview: jdText.trim().slice(0, 120),
          result: response
        },
        ...versionHistory
      ].slice(0, 10);
      setVersionHistory(nextHistory);
      window.localStorage.setItem("resume-generation-versions", JSON.stringify(nextHistory));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to generate resume.");
    } finally {
      setIsLoading(false);
    }
  }

  function reset() {
    setResult(null);
    setError(null);
  }

  return (
    <main className="min-h-screen">
      <header className="border-b border-line bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4">
          <div className="flex items-center gap-3">
            <div className="grid h-9 w-9 place-items-center rounded border border-line bg-paper">
              <FileText aria-hidden className="h-5 w-5 text-pine" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-ink">Resume Generation App</h1>
              <p className="text-sm text-neutral-600">Grounded ATS tailoring workspace</p>
            </div>
          </div>
          <button
            type="button"
            onClick={reset}
            className="focus-ring inline-flex h-10 items-center gap-2 rounded border border-line bg-white px-3 text-sm font-medium text-ink hover:bg-paper"
          >
            <RotateCcw aria-hidden className="h-4 w-4" />
            Reset
          </button>
        </div>
      </header>

      <form onSubmit={onSubmit} className="mx-auto grid max-w-7xl gap-5 px-5 py-5 lg:grid-cols-[1.05fr_0.95fr]">
        <section className="grid gap-4">
          <div className="rounded border border-line bg-white p-4">
            <label className="mb-2 block text-sm font-semibold text-ink" htmlFor="resume">
              Source Resume
            </label>
            <textarea
              id="resume"
              value={resumeText}
              onChange={(event) => setResumeText(event.target.value)}
              className="focus-ring min-h-72 w-full rounded border border-line bg-paper p-3 text-sm leading-6 text-ink"
              placeholder="Paste the master resume text here."
            />
          </div>

          <div className="rounded border border-line bg-white p-4">
            <label className="mb-2 block text-sm font-semibold text-ink" htmlFor="jd">
              Job Description
            </label>
            <textarea
              id="jd"
              value={jdText}
              onChange={(event) => setJdText(event.target.value)}
              className="focus-ring min-h-72 w-full rounded border border-line bg-paper p-3 text-sm leading-6 text-ink"
              placeholder="Paste the job description text here."
            />
          </div>

          <div className="grid gap-3 rounded border border-line bg-white p-4 md:grid-cols-2">
            <label className="grid gap-2 text-sm font-medium text-ink">
              Target Role
              <input
                value={targetRole}
                onChange={(event) => setTargetRole(event.target.value)}
                className="focus-ring h-10 rounded border border-line bg-paper px-3 text-sm"
                placeholder="Senior Backend Engineer"
              />
            </label>
            <label className="grid gap-2 text-sm font-medium text-ink">
              Seniority
              <input
                value={seniority}
                onChange={(event) => setSeniority(event.target.value)}
                className="focus-ring h-10 rounded border border-line bg-paper px-3 text-sm"
                placeholder="Senior"
              />
            </label>
            <label className="grid gap-2 text-sm font-medium text-ink">
              Years
              <input
                value={years}
                onChange={(event) => setYears(event.target.value)}
                className="focus-ring h-10 rounded border border-line bg-paper px-3 text-sm"
                inputMode="numeric"
                placeholder="8"
              />
            </label>
            <label className="grid gap-2 text-sm font-medium text-ink">
              Skills Emphasis
              <input
                value={skills}
                onChange={(event) => setSkills(event.target.value)}
                className="focus-ring h-10 rounded border border-line bg-paper px-3 text-sm"
                placeholder="Python, FastAPI, AWS"
              />
            </label>
          </div>

          <button
            type="submit"
            disabled={!canSubmit || isLoading}
            className="focus-ring inline-flex h-11 items-center justify-center gap-2 rounded bg-pine px-4 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-neutral-400"
          >
            <Wand2 aria-hidden className="h-4 w-4" />
            {isLoading ? "Generating" : "Generate Tailored Resume"}
          </button>

          {error ? (
            <div className="flex items-start gap-2 rounded border border-coral bg-white p-3 text-sm text-coral">
              <AlertTriangle aria-hidden className="mt-0.5 h-4 w-4 shrink-0" />
              {error}
            </div>
          ) : null}
        </section>

        <section className="grid content-start gap-4">
          {result ? (
            <ResultPanel
              result={result}
              versionHistory={versionHistory}
              onOpenVersion={(item) => setResult(item.result)}
            />
          ) : (
            <EmptyPanel versionHistory={versionHistory} onOpenVersion={(item) => setResult(item.result)} />
          )}
        </section>
      </form>
    </main>
  );
}

function EmptyPanel({
  versionHistory,
  onOpenVersion
}: {
  versionHistory: VersionHistoryItem[];
  onOpenVersion: (item: VersionHistoryItem) => void;
}) {
  return (
    <>
      <div className="rounded border border-dashed border-line bg-white p-6">
        <h2 className="text-lg font-semibold text-ink">Tailored output</h2>
        <p className="mt-2 text-sm leading-6 text-neutral-600">
          Results will appear here after generation.
        </p>
      </div>
      <VersionHistoryPanel versionHistory={versionHistory} onOpenVersion={onOpenVersion} />
    </>
  );
}

function ResultPanel({
  result,
  versionHistory,
  onOpenVersion
}: {
  result: TailoringResponse;
  versionHistory: VersionHistoryItem[];
  onOpenVersion: (item: VersionHistoryItem) => void;
}) {
  const scorecard = result.scorecard;
  const resume = result.tailored_resume;

  return (
    <>
      <PdfPreviewPanel result={result} />
      <DownloadPanel result={result} />
      <AtsDashboard result={result} />

      <div className="rounded border border-line bg-white p-4">
        <div className="mb-4 flex items-start justify-between gap-3">
          <div>
            <h2 className="text-lg font-semibold text-ink">Scorecard</h2>
            <p className="text-sm capitalize text-neutral-600">
              Confidence: {scorecard.compatibility_confidence}
            </p>
          </div>
          <span className="rounded border border-line px-2 py-1 text-xs font-medium text-ink">
            {scorecard.matched_keywords.length} matched
          </span>
        </div>
        <div className="grid gap-4">
          <ScoreMeter label="Keyword Match" value={scorecard.keyword_match_score} />
          <ScoreMeter label="ATS Compatibility" value={scorecard.ats_compatibility_score} />
          <ScoreMeter label="Technical Skill Match" value={scorecard.technical_skill_match_score} />
          <ScoreMeter label="Experience Match" value={scorecard.experience_match_score} />
          <ScoreMeter label="Leadership Match" value={scorecard.leadership_match_score} />
          <ScoreMeter label="Domain Match" value={scorecard.domain_match_score} />
          <ScoreMeter label="Semantic Alignment" value={scorecard.semantic_alignment_score} />
          <ScoreMeter label="Recruiter Readability" value={scorecard.recruiter_readability_score} />
        </div>
      </div>

      <div className="rounded border border-line bg-white p-4">
        <h2 className="mb-3 text-lg font-semibold text-ink">Tailored Resume</h2>
        <ResumePreview resume={resume} />
      </div>

      <SkillImprovementPanel result={result} />

      <div className="rounded border border-line bg-white p-4">
        <h2 className="mb-3 text-lg font-semibold text-ink">Change Log</h2>
        <div className="grid gap-3">
          {result.comparison.slice(0, 8).map((change, index) => (
            <div key={`${change.source_claim_ids.join("-")}-${index}`} className="border-t border-line pt-3 first:border-t-0 first:pt-0">
              <p className="text-sm font-medium text-ink">{change.tailored_text}</p>
              <p className="mt-1 text-xs leading-5 text-neutral-600">{change.reason}</p>
              {change.jd_keywords.length ? (
                <p className="mt-1 text-xs text-cobalt">Mapped: {change.jd_keywords.join(", ")}</p>
              ) : null}
            </div>
          ))}
        </div>
      </div>
      <VersionHistoryPanel versionHistory={versionHistory} onOpenVersion={onOpenVersion} />
    </>
  );
}

function PdfPreviewPanel({ result }: { result: TailoringResponse }) {
  const [zoom, setZoom] = useState(100);
  const [compare, setCompare] = useState(true);
  const assets = result.output_assets;
  const tailoredUrl = assets.tailored_resume_pdf_url;
  const originalUrl = assets.original_resume_pdf_url;
  const hasPdfPreview = Boolean(tailoredUrl);

  return (
    <div className="rounded border border-line bg-white p-4">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-ink">Resume Preview</h2>
          <p className="text-sm text-neutral-600">
            Pages: {assets.tailored_page_count ?? "Pending PDF export"}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setZoom((value) => Math.max(70, value - 10))}
            className="focus-ring grid h-9 w-9 place-items-center rounded border border-line bg-white"
            aria-label="Zoom out"
          >
            <ZoomOut aria-hidden className="h-4 w-4" />
          </button>
          <span className="w-14 text-center text-sm tabular-nums">{zoom}%</span>
          <button
            type="button"
            onClick={() => setZoom((value) => Math.min(160, value + 10))}
            className="focus-ring grid h-9 w-9 place-items-center rounded border border-line bg-white"
            aria-label="Zoom in"
          >
            <ZoomIn aria-hidden className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={() => setCompare((value) => !value)}
            className="focus-ring inline-flex h-9 items-center gap-2 rounded border border-line bg-white px-3 text-sm"
          >
            <Columns2 aria-hidden className="h-4 w-4" />
            Compare
          </button>
        </div>
      </div>

      {hasPdfPreview ? (
        <div className={compare && originalUrl ? "grid gap-3 md:grid-cols-2" : "grid gap-3"}>
          {compare && originalUrl ? (
            <PdfFrame title="Original Resume" url={originalUrl} zoom={zoom} />
          ) : null}
          <PdfFrame title="Tailored Resume" url={tailoredUrl ?? ""} zoom={zoom} />
        </div>
      ) : (
        <div className="rounded border border-dashed border-line bg-paper p-4 text-sm leading-6 text-neutral-700">
          PDF preview will render after the template-preserving export endpoint returns PDF URLs.
          Modified sections are listed below in the change summary.
        </div>
      )}
    </div>
  );
}

function PdfFrame({ title, url, zoom }: { title: string; url: string; zoom: number }) {
  return (
    <div className="overflow-hidden rounded border border-line">
      <div className="border-b border-line bg-paper px-3 py-2 text-sm font-medium text-ink">{title}</div>
      <iframe
        title={title}
        src={`${url}#zoom=${zoom}`}
        className="h-[520px] w-full bg-white"
      />
    </div>
  );
}

function DownloadPanel({ result }: { result: TailoringResponse }) {
  const links = [
    ["Tailored Resume PDF", result.output_assets.tailored_resume_pdf_url],
    ["Original Resume PDF", result.output_assets.original_resume_pdf_url],
    ["ATS Analysis Report PDF", result.output_assets.ats_report_pdf_url]
  ] as const;

  return (
    <div className="rounded border border-line bg-white p-4">
      <h2 className="mb-3 text-lg font-semibold text-ink">Downloads</h2>
      <div className="grid gap-2 md:grid-cols-3">
        {links.map(([label, href]) =>
          href ? (
            <a
              key={label}
              href={href}
              download
              className="focus-ring inline-flex h-10 items-center justify-center gap-2 rounded border border-line bg-paper px-3 text-sm font-medium text-ink"
            >
              <Download aria-hidden className="h-4 w-4" />
              {label}
            </a>
          ) : (
            <button
              key={label}
              type="button"
              disabled
              className="inline-flex h-10 cursor-not-allowed items-center justify-center gap-2 rounded border border-line bg-neutral-100 px-3 text-sm font-medium text-neutral-500"
            >
              <Download aria-hidden className="h-4 w-4" />
              {label}
            </button>
          )
        )}
      </div>
    </div>
  );
}

function AtsDashboard({ result }: { result: TailoringResponse }) {
  const analysis = result.ats_analysis;

  return (
    <div className="rounded border border-line bg-white p-4">
      <h2 className="mb-3 text-lg font-semibold text-ink">ATS Analysis Dashboard</h2>
      <div className="grid gap-4">
        <ScoreMeter label="ATS Compatibility" value={analysis.ats_compatibility_score} />
        <ScoreMeter label="Keyword Match" value={analysis.keyword_match_score} />
        <ScoreMeter label="Technical Skill Match" value={analysis.technical_skill_match} />
        <ScoreMeter label="Experience Match" value={analysis.experience_match} />
        <ScoreMeter label="Leadership Match" value={analysis.leadership_match} />
        <ScoreMeter label="Domain Match" value={analysis.domain_match} />
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <SummaryList title="Strengths" items={analysis.strengths} />
        <SummaryList title="Gaps" items={analysis.gaps} />
        <SummaryList title="Recommendations" items={analysis.recommendations} />
        <SummaryList
          title="Missing Keywords"
          items={analysis.keyword_analysis.missing_keywords.map(
            (keyword) => `The resume does not currently demonstrate experience with ${keyword}.`
          )}
        />
      </div>
    </div>
  );
}

function SkillImprovementPanel({ result }: { result: TailoringResponse }) {
  const report = result.ats_analysis.skill_improvement_report;

  return (
    <div className="rounded border border-line bg-white p-4">
      <h2 className="mb-3 text-lg font-semibold text-ink">Skill Improvement Recommendations</h2>
      <div className="grid gap-3 md:grid-cols-2">
        <SummaryList title="Technical Skills to Learn" items={report.technical_skills_to_learn} />
        <SummaryList title="Experience Areas to Build" items={report.experience_areas_to_build} />
        <SummaryList title="Suggested Projects" items={report.suggested_projects} />
        <SummaryList title="Certification Suggestions" items={report.certification_suggestions} />
        <SummaryList title="Interview Preparation Areas" items={report.interview_preparation_areas} />
      </div>
      <p className="mt-3 rounded border border-line bg-paper p-3 text-xs leading-5 text-neutral-700">
        {report.safety_note}
      </p>
    </div>
  );
}

function SummaryList({ title, items }: { title: string; items: string[] }) {
  return (
    <section className="rounded border border-line bg-paper p-3">
      <h3 className="text-sm font-semibold text-ink">{title}</h3>
      {items.length ? (
        <ul className="mt-2 list-disc space-y-1 pl-5 text-sm leading-5 text-neutral-700">
          {items.slice(0, 6).map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="mt-2 text-sm text-neutral-600">No items detected.</p>
      )}
    </section>
  );
}

function VersionHistoryPanel({
  versionHistory,
  onOpenVersion
}: {
  versionHistory: VersionHistoryItem[];
  onOpenVersion: (item: VersionHistoryItem) => void;
}) {
  return (
    <div className="rounded border border-line bg-white p-4">
      <h2 className="mb-3 text-lg font-semibold text-ink">Version History</h2>
      {versionHistory.length ? (
        <div className="grid gap-2">
          {versionHistory.map((item) => (
            <button
              key={`${item.runId}-${item.createdAt}`}
              type="button"
              onClick={() => onOpenVersion(item)}
              className="focus-ring rounded border border-line bg-paper p-3 text-left hover:bg-white"
            >
              <span className="block text-sm font-medium text-ink">
                {new Date(item.createdAt).toLocaleString()}
              </span>
              <span className="mt-1 block text-xs leading-5 text-neutral-600">
                JD: {item.jobDescriptionPreview || "No description preview"}
              </span>
            </button>
          ))}
        </div>
      ) : (
        <p className="text-sm text-neutral-600">Generated versions will be saved locally here.</p>
      )}
    </div>
  );
}

function ResumePreview({ resume }: { resume: TailoringResponse["tailored_resume"] }) {
  return (
    <div className="space-y-4 text-sm leading-6 text-ink">
      {resume.summary.length ? (
        <section>
          <h3 className="font-semibold">Summary</h3>
          <ul className="mt-1 list-disc space-y-1 pl-5">
            {resume.summary.map((bullet) => (
              <li key={bullet.source_claim_ids.join("-")}>{bullet.text}</li>
            ))}
          </ul>
        </section>
      ) : null}

      {resume.skills.length ? (
        <section>
          <h3 className="font-semibold">Skills</h3>
          <p className="mt-1">{resume.skills.join(", ")}</p>
        </section>
      ) : null}

      {resume.sections.map((section) => (
        <section key={section.name}>
          <h3 className="font-semibold">{section.name}</h3>
          <ul className="mt-1 list-disc space-y-1 pl-5">
            {section.items.map((item) => (
              <li key={item.source_claim_ids.join("-")}>{item.text}</li>
            ))}
          </ul>
        </section>
      ))}

      {resume.validation_warnings.length ? (
        <section className="border-t border-line pt-3">
          <h3 className="font-semibold text-coral">Validation Warnings</h3>
          <ul className="mt-1 list-disc space-y-1 pl-5 text-coral">
            {resume.validation_warnings.slice(0, 6).map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}
