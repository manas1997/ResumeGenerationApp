from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.ai.providers import get_ai_provider
from app.core.config import settings
from app.schemas.tailoring import TailoringRequest, TailoringResponse
from app.services.ats_analysis import build_ats_analysis
from app.services.jd_parser import parse_job_description
from app.services.resume_parser import parse_resume_text
from app.services.scoring import compute_scorecard
from app.services.tailoring_engine import tailor_resume

router = APIRouter()


@router.post("", response_model=TailoringResponse)
def create_tailoring_run(request: TailoringRequest) -> TailoringResponse:
    resume_text = request.source_resume.raw_text.strip()
    jd_text = request.job_description.raw_text.strip()

    if not resume_text:
        raise HTTPException(status_code=400, detail="Source resume text is required.")
    if not jd_text:
        raise HTTPException(status_code=400, detail="Job description text is required.")
    if len(resume_text) > settings.max_resume_chars:
        raise HTTPException(status_code=413, detail="Source resume text is too large.")
    if len(jd_text) > settings.max_jd_chars:
        raise HTTPException(status_code=413, detail="Job description text is too large.")

    parsed_resume = parse_resume_text(resume_text)
    parsed_jd = parse_job_description(jd_text)
    scorecard = compute_scorecard(parsed_resume, parsed_jd)
    ats_analysis = build_ats_analysis(parsed_resume, parsed_jd, scorecard)
    tailored = tailor_resume(
        parsed_resume,
        parsed_jd,
        request.preferences,
        scorecard,
        ai_provider=get_ai_provider(),
    )

    return TailoringResponse(
        run_id=str(uuid4()),
        parsed_resume=parsed_resume,
        parsed_job_description=parsed_jd,
        tailored_resume=tailored.resume,
        scorecard=scorecard,
        ats_analysis=ats_analysis,
        comparison=tailored.comparison,
    )
