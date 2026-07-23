from celery import shared_task
from .models import Resume
from .text_extraction import extract_text_from_resume
from .llm_parser import parse_resume_text


@shared_task(bind=True, max_retries=2)
def parse_resume_task(self, resume_id):
    """
    Background task: extract text from the uploaded resume file,
    send it to the parser, and save the result.
    """
    try:
        resume = Resume.objects.get(id=resume_id)
    except Resume.DoesNotExist:
        return f"Resume {resume_id} not found"

    try:
        raw_text = extract_text_from_resume(resume.file)
        parsed_data = parse_resume_text(raw_text)

        resume.parsed_data = parsed_data
        resume.is_parsed = True
        resume.save(update_fields=['parsed_data', 'is_parsed'])

        return f"Resume {resume_id} parsed successfully"

    except Exception as exc:
        raise self.retry(exc=exc, countdown=10 * (self.request.retries + 1))
