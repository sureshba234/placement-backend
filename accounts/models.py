from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model with role-based access.
    We extend AbstractUser (not AbstractBaseUser) so we keep
    Django's built-in auth machinery (password hashing, permissions,
    admin integration) and just add our role field on top.
    """

    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        TPO_ADMIN = 'tpo_admin', 'TPO Admin'
        RECRUITER = 'recruiter', 'Recruiter'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    # Common fields useful across all roles
    phone_number = models.CharField(max_length=15, blank=True)

    # Student-specific (nullable for non-students)
    college = models.ForeignKey(
        'colleges.College',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
    )
    branch = models.CharField(max_length=100, blank=True)
    cgpa = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )
    backlog_count = models.PositiveIntegerField(default=0)
    graduation_year = models.PositiveIntegerField(null=True, blank=True)

    # Recruiter-specific
    company_name = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_tpo_admin(self):
        return self.role == self.Role.TPO_ADMIN

    @property
    def is_recruiter(self):
        return self.role == self.Role.RECRUITER

# Create your models here.
