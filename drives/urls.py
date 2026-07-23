from django.urls import path
from .views import (
    DriveCreateView,
    DriveListAllView,
    DriveDetailView,
    EligibleDrivesView,
    RecruiterDriveCreateView,
    RecruiterDriveListView,
    ApproveDriveView, 
    PendingDrivesView,
)


urlpatterns = [
    path('create/', DriveCreateView.as_view(), name='drive-create'),
    path('all/', DriveListAllView.as_view(), name='drive-list-all'),
    path('eligible/', EligibleDrivesView.as_view(), name='drive-eligible'),
    path('recruiter/create/', RecruiterDriveCreateView.as_view(), name='recruiter-drive-create'),
    path('recruiter/mine/', RecruiterDriveListView.as_view(), name='recruiter-drive-mine'),
    path('pending/', PendingDrivesView.as_view(), name='drive-pending'),
    path('<int:pk>/approve/', ApproveDriveView.as_view(), name='drive-approve'),
    path('<int:pk>/', DriveDetailView.as_view(), name='drive-detail'),
    
]