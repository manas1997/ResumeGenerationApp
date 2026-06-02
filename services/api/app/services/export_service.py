from app.schemas.resume import TailoredResume


def render_resume_html(resume: TailoredResume) -> str:
    skill_text = ", ".join(resume.skills)
    summary_items = "".join(f"<li>{bullet.text}</li>" for bullet in resume.summary)
    sections = []
    for section in resume.sections:
        items = "".join(f"<li>{item.text}</li>" for item in section.items)
        sections.append(f"<section><h2>{section.name}</h2><ul>{items}</ul></section>")

    return f"""
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>
      body {{ font-family: Arial, Helvetica, sans-serif; font-size: 10.5pt; line-height: 1.35; }}
      h1 {{ font-size: 18pt; margin: 0 0 8px; }}
      h2 {{ font-size: 11.5pt; border-bottom: 1px solid #222; margin: 14px 0 6px; }}
      ul {{ margin: 0 0 8px 18px; padding: 0; }}
      li {{ margin-bottom: 4px; }}
      .skills {{ margin-bottom: 8px; }}
    </style>
  </head>
  <body>
    <h1>Tailored Resume</h1>
    <section>
      <h2>Summary</h2>
      <ul>{summary_items}</ul>
    </section>
    <section>
      <h2>Skills</h2>
      <div class="skills">{skill_text}</div>
    </section>
    {''.join(sections)}
  </body>
</html>
"""

