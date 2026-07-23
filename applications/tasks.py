import requests
from celery import shared_task
from django.conf import settings


@shared_task(bind=True, max_retries=3)
def trigger_match_scoring(self, application_id):
    """
    Calls the FastAPI matching service to compute and store the
    match_score/missing_skills for a given application. Runs async
    via Celery so the student's apply request isn't blocked waiting
    on embedding computation.

    Retries on failure — e.g. if the matching service is briefly
    unavailable or the resume hasn't finished parsing yet.
    """
    url = f"{settings.MATCHING_SERVICE_URL}/match-application/{application_id}"

    try:
        response = requests.post(url, timeout=15)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as exc:
        # Backs off progressively: 10s, 20s, 30s between retries
        raise self.retry(exc=exc, countdown=10 * (self.request.retries + 1))