from rest_framework import generics
from django.conf import settings
from accounts.permissions import IsStudent
from .models import Resume
from .serializers import ResumeUploadSerializer
from .tasks import parse_resume_task


class ResumeUploadView(generics.CreateAPIView):
    serializer_class = ResumeUploadSerializer
    permission_classes = [IsStudent]

    def perform_create(self, serializer):
        resume = serializer.save(student=self.request.user)
        if settings.USE_CELERY:
            parse_resume_task.delay(resume.id)
        else:
            # Run synchronously in production where no Celery worker runs
            parse_resume_task(resume.id)


class MyResumesView(generics.ListAPIView):
    serializer_class = ResumeUploadSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return Resume.objects.filter(
            student=self.request.user
        ).order_by('-uploaded_at')