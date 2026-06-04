from app.schemas.ats import AtsAnalysisDashboard


def render_ats_report_html(analysis: AtsAnalysisDashboard) -> str:
    missing = "".join(f"<li>{item.explanation}</li>" for item in analysis.missing_skills)
    weak = "".join(f"<li>{item.explanation}</li>" for item in analysis.weakly_demonstrated_skills)
    strengths = "".join(f"<li>{strength}</li>" for strength in analysis.strengths)
    recommendations = "".join(f"<li>{item}</li>" for item in analysis.recommendations)
    technical = "".join(
        f"<li>{skill}</li>" for skill in analysis.skill_improvement_report.technical_skills_to_learn
    )
    experience = "".join(
        f"<li>{area}</li>" for area in analysis.skill_improvement_report.experience_areas_to_build
    )
    projects = "".join(
        f"<li>{project}</li>" for project in analysis.skill_improvement_report.suggested_projects
    )
    certifications = "".join(
        f"<li>{cert}</li>" for cert in analysis.skill_improvement_report.certification_suggestions
    )
    interview = "".join(
        f"<li>{area}</li>" for area in analysis.skill_improvement_report.interview_preparation_areas
    )

    return f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>
      body {{ font-family: Arial, Helvetica, sans-serif; font-size: 10.5pt; line-height: 1.45; }}
      h1 {{ font-size: 18pt; margin: 0 0 12px; }}
      h2 {{ font-size: 12pt; margin: 18px 0 6px; border-bottom: 1px solid #222; }}
      .scores {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }}
      .score {{ border: 1px solid #ddd; padding: 8px; }}
      ul {{ margin-top: 4px; }}
    </style>
  </head>
  <body>
    <h1>ATS Analysis Report</h1>
    <section class="scores">
      <div class="score">ATS Compatibility: {analysis.ats_compatibility_score:.0f}</div>
      <div class="score">Keyword Match: {analysis.keyword_match_score:.0f}</div>
      <div class="score">Technical Skill Match: {analysis.technical_skill_match:.0f}</div>
      <div class="score">Experience Match: {analysis.experience_match:.0f}</div>
      <div class="score">Leadership Match: {analysis.leadership_match:.0f}</div>
      <div class="score">Domain Match: {analysis.domain_match:.0f}</div>
    </section>
    <h2>Strengths</h2>
    <ul>{strengths}</ul>
    <h2>Gaps</h2>
    <h3>Missing Skills</h3>
    <ul>{missing}</ul>
    <h3>Weakly Demonstrated Skills</h3>
    <ul>{weak}</ul>
    <h2>Recommendations</h2>
    <ul>{recommendations}</ul>
    <h2>Skill Improvement Recommendations</h2>
    <h3>Technical Skills to Learn</h3>
    <ul>{technical}</ul>
    <h3>Experience Areas to Build</h3>
    <ul>{experience}</ul>
    <h3>Suggested Projects</h3>
    <ul>{projects}</ul>
    <h3>Certification Suggestions</h3>
    <ul>{certifications}</ul>
    <h3>Interview Preparation Areas</h3>
    <ul>{interview}</ul>
    <p>{analysis.skill_improvement_report.safety_note}</p>
  </body>
</html>
"""


def render_ats_report_pdf_bytes(analysis: AtsAnalysisDashboard) -> bytes:
    from weasyprint import HTML

    return HTML(string=render_ats_report_html(analysis)).write_pdf()

