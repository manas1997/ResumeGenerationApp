"use client";

import {
  Activity,
  AlertTriangle,
  BadgeCheck,
  Brain,
  Columns2,
  Crosshair,
  Download,
  FileText,
  Gauge,
  History,
  RotateCcw,
  Sparkles,
  Target,
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

type ResultTab = "preview" | "ats" | "resume" | "growth" | "history";

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
    <main className="system-shell min-h-screen">
      <header className="sticky top-0 z-30 border-b border-cyan-300/20 bg-slate-950/76 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-4">
          <div className="flex items-center gap-3">
            <div className="grid h-11 w-11 place-items-center rounded-md border border-cyan-300/40 bg-cyan-950/60 shadow-[0_0_28px_rgba(34,211,238,0.25)]">
              <Sparkles aria-hidden className="h-5 w-5 text-cyan-200" />
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-200/80">
                System Online
              </p>
              <h1 className="text-xl font-semibold text-cyan-50">Resume Hunter Console</h1>
            </div>
          </div>
          <div className="hidden items-center gap-2 md:flex">
            <span className="status-chip px-3 py-1 text-xs font-semibold">Truth Locked</span>
            <span className="status-chip px-3 py-1 text-xs font-semibold">ATS Scan Ready</span>
          </div>
          <button
            type="button"
            onClick={reset}
            className="focus-ring ghost-button inline-flex h-10 items-center gap-2 px-3 text-sm font-medium"
          >
            <RotateCcw aria-hidden className="h-4 w-4" />
            Reset
          </button>
        </div>
      </header>

      <form onSubmit={onSubmit} className="mx-auto grid max-w-7xl gap-5 px-5 py-6 lg:grid-cols-[1.02fr_0.98fr]">
        <section className="grid gap-4">
          <div className="system-panel p-4">
            <label className="mb-2 flex items-center gap-2 text-sm font-semibold text-cyan-50" htmlFor="resume">
              <FileText aria-hidden className="h-4 w-4 text-cyan-200" />
              Source Resume Matrix
            </label>
            <textarea
              id="resume"
              value={resumeText}
              onChange={(event) => setResumeText(event.target.value)}
              className="focus-ring field-surface min-h-72 w-full p-3 text-sm leading-6"
              placeholder="Paste the master resume text here."
            />
            <p className="mt-2 text-xs text-cyan-100/60">{resumeText.length.toLocaleString()} characters loaded</p>
          </div>

          <div className="system-panel p-4">
            <label className="mb-2 flex items-center gap-2 text-sm font-semibold text-cyan-50" htmlFor="jd">
              <Target aria-hidden className="h-4 w-4 text-cyan-200" />
              Job Gate Briefing
            </label>
            <textarea
              id="jd"
              value={jdText}
              onChange={(event) => setJdText(event.target.value)}
              className="focus-ring field-surface min-h-72 w-full p-3 text-sm leading-6"
              placeholder="Paste the job description text here."
            />
            <p className="mt-2 text-xs text-cyan-100/60">{jdText.length.toLocaleString()} characters analyzed</p>
          </div>

          <div className="system-panel grid gap-3 p-4 md:grid-cols-2">
            <label className="grid gap-2 text-sm font-medium text-cyan-50">
              Target Role
              <input
                value={targetRole}
                onChange={(event) => setTargetRole(event.target.value)}
                className="focus-ring field-surface h-10 px-3 text-sm"
                placeholder="Senior Backend Engineer"
              />
            </label>
            <label className="grid gap-2 text-sm font-medium text-cyan-50">
              Seniority
              <input
                value={seniority}
                onChange={(event) => setSeniority(event.target.value)}
                className="focus-ring field-surface h-10 px-3 text-sm"
                placeholder="Senior"
              />
            </label>
            <label className="grid gap-2 text-sm font-medium text-cyan-50">
              Years
              <input
                value={years}
                onChange={(event) => setYears(event.target.value)}
                className="focus-ring field-surface h-10 px-3 text-sm"
                inputMode="numeric"
                placeholder="8"
              />
            </label>
            <label className="grid gap-2 text-sm font-medium text-cyan-50">
              Skills Emphasis
              <input
                value={skills}
                onChange={(event) => setSkills(event.target.value)}
                className="focus-ring field-surface h-10 px-3 text-sm"
                placeholder="Python, FastAPI, AWS"
              />
            </label>
          </div>

          <button
            type="submit"
            disabled={!canSubmit || isLoading}
            className="focus-ring command-button inline-flex h-12 items-center justify-center gap-2 px-4 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-50"
          >
            <Wand2 aria-hidden className="h-4 w-4" />
            {isLoading ? "Awakening Resume Core" : "Start Tailoring Quest"}
          </button>

          {error ? (
            <div className="system-panel flex items-start gap-2 border-rose-300/40 p-3 text-sm text-rose-200">
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
      <div className="system-panel p-6">
        <div className="mb-4 flex items-center gap-3">
          <div className="grid h-12 w-12 place-items-center rounded-md border border-cyan-300/30 bg-cyan-950/40">
            <Gauge aria-hidden className="h-5 w-5 text-cyan-200" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-cyan-50">Awaiting System Scan</h2>
            <p className="text-sm text-cyan-100/64">Load resume and JD data to unlock the dashboard.</p>
          </div>
        </div>
        <div className="grid gap-3 md:grid-cols-3">
          {["Parse", "Match", "Rewrite"].map((step, index) => (
            <div key={step} className="rounded-md border border-cyan-300/20 bg-slate-950/50 p-3">
              <p className="text-xs uppercase tracking-[0.22em] text-cyan-200/60">Phase 0{index + 1}</p>
              <p className="mt-1 text-sm font-semibold text-cyan-50">{step}</p>
            </div>
          ))}
        </div>
        <p className="mt-4 text-sm leading-6 text-cyan-100/64">
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
  const [activeTab, setActiveTab] = useState<ResultTab>("preview");
  const tabs: Array<{ id: ResultTab; label: string; icon: typeof FileText }> = [
    { id: "preview", label: "Preview", icon: FileText },
    { id: "ats", label: "ATS Scan", icon: Crosshair },
    { id: "resume", label: "Resume", icon: BadgeCheck },
    { id: "growth", label: "Growth", icon: Brain },
    { id: "history", label: "History", icon: History }
  ];

  return (
    <>
      <div className="system-panel p-4">
        <div className="mb-4 flex items-start justify-between gap-3">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-200/70">
              Quest Result
            </p>
            <h2 className="text-lg font-semibold text-cyan-50">Hunter Rank Scorecard</h2>
            <p className="text-sm capitalize text-cyan-100/64">
              Confidence: {scorecard.compatibility_confidence}
            </p>
          </div>
          <span className="status-chip px-3 py-1 text-xs font-semibold">
            {scorecard.matched_keywords.length} matched
          </span>
        </div>
        <div className="grid gap-3 md:grid-cols-2">
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

      <div className="system-panel p-3">
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-5">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                type="button"
                data-active={activeTab === tab.id}
                onClick={() => setActiveTab(tab.id)}
                className="tab-button focus-ring inline-flex h-10 items-center justify-center gap-2 px-3 text-sm font-semibold"
              >
                <Icon aria-hidden className="h-4 w-4" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {activeTab === "preview" ? (
        <>
          <PdfPreviewPanel result={result} />
          <DownloadPanel result={result} />
          <ChangeSummaryPanel result={result} />
        </>
      ) : null}
      {activeTab === "ats" ? <AtsDashboard result={result} /> : null}
      {activeTab === "resume" ? (
        <div className="system-panel p-4">
          <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold text-cyan-50">
            <BadgeCheck aria-hidden className="h-5 w-5 text-cyan-200" />
            Tailored Resume
          </h2>
          <ResumePreview resume={resume} />
        </div>
      ) : null}
      {activeTab === "growth" ? <SkillImprovementPanel result={result} /> : null}
      {activeTab === "history" ? (
        <VersionHistoryPanel versionHistory={versionHistory} onOpenVersion={onOpenVersion} />
      ) : null}
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
    <div className="system-panel p-4">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h2 className="flex items-center gap-2 text-lg font-semibold text-cyan-50">
            <Activity aria-hidden className="h-5 w-5 text-cyan-200" />
            Resume Preview
          </h2>
          <p className="text-sm text-cyan-100/64">
            Pages: {assets.tailored_page_count ?? "Pending PDF export"}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setZoom((value) => Math.max(70, value - 10))}
            className="focus-ring ghost-button grid h-9 w-9 place-items-center"
            aria-label="Zoom out"
          >
            <ZoomOut aria-hidden className="h-4 w-4" />
          </button>
          <span className="w-14 text-center text-sm tabular-nums text-cyan-100">{zoom}%</span>
          <button
            type="button"
            onClick={() => setZoom((value) => Math.min(160, value + 10))}
            className="focus-ring ghost-button grid h-9 w-9 place-items-center"
            aria-label="Zoom in"
          >
            <ZoomIn aria-hidden className="h-4 w-4" />
          </button>
          <button
            type="button"
            onClick={() => setCompare((value) => !value)}
            className="focus-ring ghost-button inline-flex h-9 items-center gap-2 px-3 text-sm"
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
        <div className="rounded-md border border-dashed border-cyan-300/28 bg-slate-950/50 p-4 text-sm leading-6 text-cyan-100/70">
          PDF preview will render after the template-preserving export endpoint returns PDF URLs.
          Modified sections are listed below in the change summary.
        </div>
      )}
    </div>
  );
}

function PdfFrame({ title, url, zoom }: { title: string; url: string; zoom: number }) {
  return (
    <div className="overflow-hidden rounded-md border border-cyan-300/24 bg-slate-950/50">
      <div className="border-b border-cyan-300/20 bg-slate-950/70 px-3 py-2 text-sm font-medium text-cyan-50">{title}</div>
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
    <div className="system-panel p-4">
      <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold text-cyan-50">
        <Download aria-hidden className="h-5 w-5 text-cyan-200" />
        Downloads
      </h2>
      <div className="grid gap-2 md:grid-cols-3">
        {links.map(([label, href]) =>
          href ? (
            <a
              key={label}
              href={href}
              download
              className="focus-ring ghost-button inline-flex h-10 items-center justify-center gap-2 px-3 text-sm font-medium"
            >
              <Download aria-hidden className="h-4 w-4" />
              {label}
            </a>
          ) : (
            <button
              key={label}
              type="button"
              disabled
              className="inline-flex h-10 cursor-not-allowed items-center justify-center gap-2 rounded-md border border-cyan-300/12 bg-slate-900/60 px-3 text-sm font-medium text-slate-500"
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
    <div className="system-panel p-4">
      <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold text-cyan-50">
        <Crosshair aria-hidden className="h-5 w-5 text-cyan-200" />
        ATS Analysis Dashboard
      </h2>
      <div className="grid gap-3 md:grid-cols-2">
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
    <div className="system-panel p-4">
      <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold text-cyan-50">
        <Brain aria-hidden className="h-5 w-5 text-cyan-200" />
        Skill Improvement Recommendations
      </h2>
      <div className="grid gap-3 md:grid-cols-2">
        <SummaryList title="Technical Skills to Learn" items={report.technical_skills_to_learn} />
        <SummaryList title="Experience Areas to Build" items={report.experience_areas_to_build} />
        <SummaryList title="Suggested Projects" items={report.suggested_projects} />
        <SummaryList title="Certification Suggestions" items={report.certification_suggestions} />
        <SummaryList title="Interview Preparation Areas" items={report.interview_preparation_areas} />
      </div>
      <p className="mt-3 rounded-md border border-cyan-300/20 bg-slate-950/50 p-3 text-xs leading-5 text-cyan-100/70">
        {report.safety_note}
      </p>
    </div>
  );
}

function SummaryList({ title, items }: { title: string; items: string[] }) {
  return (
    <section className="rounded-md border border-cyan-300/20 bg-slate-950/48 p-3 transition hover:border-cyan-300/42 hover:bg-cyan-950/16">
      <h3 className="text-sm font-semibold text-cyan-50">{title}</h3>
      {items.length ? (
        <ul className="holo-list mt-2 list-disc space-y-1 pl-5 text-sm leading-5 text-cyan-100/72">
          {items.slice(0, 6).map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="mt-2 text-sm text-cyan-100/52">No items detected.</p>
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
    <div className="system-panel p-4">
      <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold text-cyan-50">
        <History aria-hidden className="h-5 w-5 text-cyan-200" />
        Version History
      </h2>
      {versionHistory.length ? (
        <div className="grid gap-2">
          {versionHistory.map((item) => (
            <button
              key={`${item.runId}-${item.createdAt}`}
              type="button"
              onClick={() => onOpenVersion(item)}
              className="focus-ring rounded-md border border-cyan-300/20 bg-slate-950/50 p-3 text-left transition hover:border-cyan-300/48 hover:bg-cyan-950/20"
            >
              <span className="block text-sm font-medium text-cyan-50">
                {new Date(item.createdAt).toLocaleString()}
              </span>
              <span className="mt-1 block text-xs leading-5 text-cyan-100/60">
                JD: {item.jobDescriptionPreview || "No description preview"}
              </span>
            </button>
          ))}
        </div>
      ) : (
        <p className="text-sm text-cyan-100/60">Generated versions will be saved locally here.</p>
      )}
    </div>
  );
}

function ResumePreview({ resume }: { resume: TailoringResponse["tailored_resume"] }) {
  return (
    <div className="space-y-4 text-sm leading-6 text-cyan-100/78">
      {resume.summary.length ? (
        <section className="rounded-md border border-cyan-300/18 bg-slate-950/40 p-3">
          <h3 className="font-semibold text-cyan-50">Summary</h3>
          <ul className="holo-list mt-1 list-disc space-y-1 pl-5">
            {resume.summary.map((bullet) => (
              <li key={bullet.source_claim_ids.join("-")}>{bullet.text}</li>
            ))}
          </ul>
        </section>
      ) : null}

      {resume.skills.length ? (
        <section className="rounded-md border border-cyan-300/18 bg-slate-950/40 p-3">
          <h3 className="font-semibold text-cyan-50">Skills</h3>
          <p className="mt-2 flex flex-wrap gap-2">
            {resume.skills.slice(0, 32).map((skill) => (
              <span key={skill} className="status-chip px-2 py-1 text-xs font-medium">
                {skill}
              </span>
            ))}
          </p>
        </section>
      ) : null}

      {resume.sections.map((section) => (
        <section key={section.name} className="rounded-md border border-cyan-300/18 bg-slate-950/40 p-3">
          <h3 className="font-semibold text-cyan-50">{section.name}</h3>
          <ul className="holo-list mt-1 list-disc space-y-1 pl-5">
            {section.items.map((item) => (
              <li key={item.source_claim_ids.join("-")}>{item.text}</li>
            ))}
          </ul>
        </section>
      ))}

      {resume.validation_warnings.length ? (
        <section className="rounded-md border border-rose-300/28 bg-rose-950/20 p-3">
          <h3 className="font-semibold text-rose-200">Validation Warnings</h3>
          <ul className="mt-1 list-disc space-y-1 pl-5 text-rose-100/80">
            {resume.validation_warnings.slice(0, 6).map((warning) => (
              <li key={warning}>{warning}</li>
            ))}
          </ul>
        </section>
      ) : null}
    </div>
  );
}

function ChangeSummaryPanel({ result }: { result: TailoringResponse }) {
  return (
    <div className="system-panel p-4">
      <h2 className="mb-3 flex items-center gap-2 text-lg font-semibold text-cyan-50">
        <Sparkles aria-hidden className="h-5 w-5 text-cyan-200" />
        Modified Sections
      </h2>
      <div className="grid gap-3">
        {result.comparison.slice(0, 8).map((change, index) => (
          <div
            key={`${change.source_claim_ids.join("-")}-${index}`}
            className="rounded-md border border-cyan-300/20 bg-slate-950/48 p-3 transition hover:border-cyan-300/44"
          >
            <div className="mb-2 flex flex-wrap items-center gap-2">
              <span className="status-chip px-2 py-1 text-xs font-semibold">
                Claim {change.source_claim_ids.join(", ")}
              </span>
              {change.jd_keywords.slice(0, 4).map((keyword) => (
                <span key={keyword} className="rounded-sm border border-indigo-300/28 bg-indigo-950/40 px-2 py-1 text-xs text-indigo-100">
                  {keyword}
                </span>
              ))}
            </div>
            <p className="text-sm font-medium text-cyan-50">{change.tailored_text}</p>
            <p className="mt-1 text-xs leading-5 text-cyan-100/62">{change.reason}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
