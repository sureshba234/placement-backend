import requests
from celery import shared_task
from django.conf import settings


@shared_task(bind=True, max_retries=3)
def trigger_match_scoring(self, application_id):
    """
    Computes resume-JD match score directly via Groq — no separate
    FastAPI service needed. Reads resume parsed_data and drive
    job_description from the database, calls Groq, writes results back.
    """
    from applications.models import Application
    from applications.matching import compute_match

    try:
        app = Application.objects.select_related(
            'resume', 'drive'
        ).get(id=application_id)
    except Application.DoesNotExist:
        return f"Application {application_id} not found"

    if not app.resume or not app.resume.is_parsed or not app.resume.parsed_data:
        raise self.retry(
            exc=ValueError("Resume not parsed yet"),
            countdown=15
        )

    # Flatten parsed resume JSON into plain text for the LLM
    parsed = app.resume.parsed_data
    skills = ', '.join(parsed.get('skills', []))
    education = ' | '.join(
        f"{e.get('degree')} at {e.get('institution')}"
        for e in parsed.get('education', [])
    )
    projects = ' | '.join(
        f"{p.get('title')}: {p.get('description')}"
        for p in parsed.get('projects', [])
    )
    resume_text = f"Skills: {skills}\nEducation: {education}\nProjects: {projects}"
    jd_text = app.drive.job_description or ""

    if not jd_text:
        return f"Drive {app.drive.id} has no job description — skipping match"

    try:
        result = compute_match(resume_text, jd_text)
        app.match_score = result['match_score']
        app.missing_skills = result['missing_skills']
        app.save(update_fields=['match_score', 'missing_skills'])
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=10 * (self.request.retries + 1))