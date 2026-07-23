from django.db import models
from django.conf import settings


class Resume(models.Model):
    """
    A student's uploaded resume. `parsed_data` is populated later
    (Step 7) by a Celery task that extracts structured info from
    the uploaded file via a parsing library + LLM call.
    """

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resumes',
    )
    file = models.FileField(upload_to='resumes/%Y/%m/')

    parsed_data = models.JSONField(
        null=True, blank=True,
        help_text="Structured JSON extracted from the resume: skills, education, projects, etc."
    )
    is_parsed = models.BooleanField(default=False)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resume of {self.student.username} ({self.uploaded_at:%Y-%m-%d})"