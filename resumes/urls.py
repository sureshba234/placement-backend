from django.urls import path
from .views import ResumeUploadView, MyResumesView

urlpatterns = [
    path('upload/', ResumeUploadView.as_view(), name='resume-upload'),
    path('mine/', MyResumesView.as_view(), name='resume-mine'),
]
