from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def notify_eligible_students(drive_id):
    """
    Notifies all students eligible for a newly created/opened drive.
    Currently logs to console instead of sending real email/SMS —
    swap the `send_notification` call for a real provider later
    (Django's send_mail, Twilio, etc.) without touching the logic
    that determines *who* gets notified.
    """
    from drives.models import Drive
    from accounts.models import User

    try:
        drive = Drive.objects.get(id=drive_id)
    except Drive.DoesNotExist:
        return f"Drive {drive_id} not found"

    if drive.status != Drive.Status.OPEN:
        return f"Drive {drive_id} is not open, skipping notifications"

    rules = drive.eligibility_rules.all()
    students = User.objects.filter(role=User.Role.STUDENT)

    notified_count = 0
    for student in students:
        if not rules or all(rule.is_student_eligible(student) for rule in rules):
            send_notification(student, drive)
            notified_count += 1

    return f"Notified {notified_count} students for drive {drive_id}"



def send_notification(student, drive):
    """
    Sends a real email via Django's send_mail, using whatever
    EMAIL_BACKEND is configured in settings (SMTP in production/dev
    with real credentials). Wrapped in try/except so one student's
    invalid/missing email doesn't crash the whole notification task
    for everyone else in the loop.
    """
    if not student.email:
        return

    subject = f"New Placement Drive: {drive.title} at {drive.company_name}"
    message = (
        f"Hi {student.first_name or student.username},\n\n"
        f"A new drive you're eligible for has just opened:\n\n"
        f"Position: {drive.title}\n"
        f"Company: {drive.company_name}\n"
        f"Deadline: {drive.application_deadline.strftime('%B %d, %Y at %I:%M %p')}\n\n"
        f"Log in to the Placement Command Center to apply.\n\n"
        f"— Placement Cell"
    )

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [student.email],
            fail_silently=False,
        )
    except Exception as e:
        # Log rather than crash — a single bad email address or
        # transient SMTP issue shouldn't fail the whole batch task.
        print(f"[EMAIL ERROR] Failed to notify {student.email}: {e}")