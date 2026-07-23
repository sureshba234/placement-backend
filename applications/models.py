from django.db import models
from django.conf import settings
from drives.models import Drive
from resumes.models import Resume


class Application(models.Model):
    """
    A student's application to a specific Drive. One student can
    apply to a drive only once — enforced via unique_together.
    """

    class Status(models.TextChoices):
        APPLIED = 'applied', 'Applied'
        SHORTLISTED = 'shortlisted', 'Shortlisted'
        REJECTED = 'rejected', 'Rejected'
        SELECTED = 'selected', 'Selected'

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
    )
    drive = models.ForeignKey(
        Drive,
        on_delete=models.CASCADE,
        related_name='applications',
    )
    resume = models.ForeignKey(
        Resume,
        on_delete=models.SET_NULL,
        null=True,
        related_name='applications',
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.APPLIED,
    )

    # Populated in Phase 2 by the FastAPI matching service
    match_score = models.FloatField(
        null=True, blank=True,
        help_text="Resume-JD similarity score (0-100), written by the matching service"
    )
    missing_skills = models.JSONField(
        default=list, blank=True,
        help_text="Skills present in JD but missing from resume"
    )

    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'drive')

    def __str__(self):
        return f"{self.student.username} -> {self.drive.title} ({self.status})"