from rest_framework import generics
from accounts.permissions import IsStudent
from .models import Resume
from .serializers import ResumeUploadSerializer
from .tasks import parse_resume_task


class ResumeUploadView(generics.CreateAPIView):
    """
    Student uploads a resume. Triggers the async parsing task
    immediately after save — student doesn't wait for the parser.
    """
    serializer_class = ResumeUploadSerializer
    permission_classes = [IsStudent]

    def perform_create(self, serializer):
        resume = serializer.save(student=self.request.user)
        parse_resume_task.delay(resume.id)


class MyResumesView(generics.ListAPIView):
    """Student views their uploaded resumes and parsing status."""
    serializer_class = ResumeUploadSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return Resume.objects.filter(
            student=self.request.user
        ).order_by('-uploaded_at')
