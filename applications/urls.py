from django.urls import path
from .views import (
    ApplyToDriveView,
    MyApplicationsView,
    DriveApplicantsView,
    UpdateApplicationStatusView,
    ExportApplicantsCSVView,
    DriveAnalyticsView,
    RecruiterShortlistView,
    OverallAnalyticsView,
    MyScoreHistoryView,
)

urlpatterns = [
    path('apply/', ApplyToDriveView.as_view(), name='application-apply'),
    path('mine/', MyApplicationsView.as_view(), name='application-mine'),
    path('drive/<int:drive_id>/applicants/', DriveApplicantsView.as_view(), name='drive-applicants'),
    path('drive/<int:drive_id>/export/', ExportApplicantsCSVView.as_view(), name='drive-export-csv'),
    path('<int:pk>/status/', UpdateApplicationStatusView.as_view(), name='application-status'),
    path('drive/<int:drive_id>/analytics/', DriveAnalyticsView.as_view(), name='drive-analytics'),
    path('drive/<int:drive_id>/shortlist/', RecruiterShortlistView.as_view(), name='drive-shortlist'),
    path('analytics/overall/', OverallAnalyticsView.as_view(), name='overall-analytics'),
    path('score-history/', MyScoreHistoryView.as_view(), name='score-history'),
]