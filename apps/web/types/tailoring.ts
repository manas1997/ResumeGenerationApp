export type TailoringRequest = {
  source_resume: {
    raw_text: string;
  };
  job_description: {
    raw_text: string;
  };
  preferences: {
    target_role?: string;
    seniority?: string;
    years_of_experience?: number;
    skills_emphasis: string[];
    tone: string;
  };
};

export type TailoredBullet = {
  text: string;
  source_claim_ids: string[];
  jd_keywords: string[];
};

export type TailoredSection = {
  name: string;
  items: TailoredBullet[];
};

export type TailoredResume = {
  summary: TailoredBullet[];
  skills: string[];
  sections: TailoredSection[];
  validation_warnings: string[];
};

export type Scorecard = {
  keyword_match_score: number;
  semantic_alignment_score: number;
  ats_compatibility_score: number;
  recruiter_readability_score: number;
  technical_skill_match_score: number;
  experience_match_score: number;
  leadership_match_score: number;
  domain_match_score: number;
  compatibility_confidence: string;
  matched_keywords: string[];
  missing_keywords: Array<{
    keyword: string;
    support_status: "supported" | "unsupported" | "ambiguous";
    reason: string;
  }>;
  improvement_recommendations: string[];
};

export type AtsAnalysisDashboard = {
  ats_compatibility_score: number;
  keyword_match_score: number;
  technical_skill_match: number;
  experience_match: number;
  leadership_match: number;
  domain_match: number;
  keyword_analysis: {
    jd_keywords: string[];
    resume_keywords: string[];
    matched_keywords: string[];
    missing_keywords: string[];
    coverage_percentage: number;
  };
  missing_skills: SkillGapItem[];
  weakly_demonstrated_skills: SkillGapItem[];
  strongly_demonstrated_skills: SkillGapItem[];
  experience_gaps: Array<{
    responsibility: string;
    evidence_strength: "missing" | "weak" | "strong";
    best_matching_claim_id?: string | null;
    explanation: string;
  }>;
  compatibility_checks: Array<{
    name: string;
    status: "pass" | "warning" | "fail";
    detail: string;
  }>;
  strengths: string[];
  gaps: string[];
  recommendations: string[];
  skill_improvement_report: {
    technical_skills_to_learn: string[];
    experience_areas_to_build: string[];
    suggested_projects: string[];
    certification_suggestions: string[];
    interview_preparation_areas: string[];
    safety_note: string;
  };
};

export type SkillGapItem = {
  skill: string;
  level: "missing" | "weak" | "strong";
  evidence_claim_ids: string[];
  explanation: string;
};

export type OutputAssetLinks = {
  tailored_resume_pdf_url?: string | null;
  original_resume_pdf_url?: string | null;
  ats_report_pdf_url?: string | null;
  tailored_page_count?: number | null;
  original_page_count?: number | null;
};

export type ChangeExplanation = {
  original_text: string;
  tailored_text: string;
  source_claim_ids: string[];
  jd_keywords: string[];
  reason: string;
  recruiter_benefit: string;
  ats_benefit: string;
};

export type TailoringResponse = {
  run_id: string;
  tailored_resume: TailoredResume;
  scorecard: Scorecard;
  ats_analysis: AtsAnalysisDashboard;
  comparison: ChangeExplanation[];
  output_assets: OutputAssetLinks;
};
