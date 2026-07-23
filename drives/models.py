from django.db import models
from django.conf import settings


class Drive(models.Model):
    """
    A placement drive posted by a TPO — e.g. "TCS Ninja 2026" or
    "Google SDE Internship". Recruiters are optionally linked if
    they post directly (Step 3 keeps this simple; recruiter-side
    posting comes in a later phase).
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PENDING_APPROVAL = 'pending_approval', 'Pending Approval'
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'


    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    job_description = models.TextField(
        help_text="Full JD text, used later for resume-JD matching"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='drives_created',
    )
    recruiter = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='drives_as_recruiter',
    limit_choices_to={'role': 'recruiter'},
)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    application_deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} @ {self.company_name}"


class EligibilityRule(models.Model):
    """
    Eligibility rules for a Drive. Kept as a separate model (not
    inline fields on Drive) so a single drive can have multiple
    rules — e.g. different CGPA cutoffs per branch.
    """

    drive = models.ForeignKey(
        Drive,
        on_delete=models.CASCADE,
        related_name='eligibility_rules',
    )

    min_cgpa = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )
    max_backlogs = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Maximum allowed active backlogs. Null = no limit."
    )
    allowed_branches = models.JSONField(
        default=list, blank=True,
        help_text='List of allowed branch names, e.g. ["CSE", "ECE"]. Empty = all branches.'
    )
    min_graduation_year = models.PositiveIntegerField(null=True, blank=True)
    max_graduation_year = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Rules for {self.drive.title}"

    def is_student_eligible(self, student):
        """
        Core eligibility check — used by the rule engine in Step 4.
        Kept here as a model method since it's tightly coupled to
        this rule's own fields.
        """
        if self.min_cgpa is not None and (
            student.cgpa is None or student.cgpa < self.min_cgpa
        ):
            return False

        if self.max_backlogs is not None and (
            student.backlog_count > self.max_backlogs
        ):
            return False

        if self.allowed_branches and student.branch not in self.allowed_branches:
            return False

        if self.min_graduation_year is not None and (
            student.graduation_year is None
            or student.graduation_year < self.min_graduation_year
        ):
            return False

        if self.max_graduation_year is not None and (
            student.graduation_year is None
            or student.graduation_year > self.max_graduation_year
        ):
            return False

        return True
