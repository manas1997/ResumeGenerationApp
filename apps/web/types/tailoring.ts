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
  compatibility_confidence: string;
  matched_keywords: string[];
  missing_keywords: Array<{
    keyword: string;
    support_status: "supported" | "unsupported" | "ambiguous";
    reason: string;
  }>;
  improvement_recommendations: string[];
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
  comparison: ChangeExplanation[];
};

