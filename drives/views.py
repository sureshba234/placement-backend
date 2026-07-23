from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from django.core.cache import cache
from accounts.permissions import IsRecruiter
from .serializers import RecruiterDriveSerializer
from rest_framework.response import Response



from accounts.permissions import IsTPOAdmin, IsStudent
from .models import Drive
from .serializers import DriveSerializer, DriveListSerializer
from .tasks import notify_eligible_students

class DriveCreateView(generics.CreateAPIView):
    """
    TPO-only endpoint to create a new drive, optionally with
    nested eligibility_rules in the same request body.
    """
    queryset = Drive.objects.all()
    serializer_class = DriveSerializer
    permission_classes = [IsTPOAdmin]

    def perform_create(self, serializer):
        drive = serializer.save(created_by=self.request.user)
        if drive.status == Drive.Status.OPEN:
            notify_eligible_students.delay(drive.id)

class DriveListAllView(generics.ListAPIView):
    """
    TPO/admin view — list every drive regardless of eligibility,
    for management purposes.
    """
    queryset = Drive.objects.all().order_by('-created_at')
    serializer_class = DriveSerializer
    permission_classes = [IsTPOAdmin]


class DriveDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Drive.objects.all()
    serializer_class = DriveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        # Only TPO admins can edit/delete
        if request.method not in permissions.SAFE_METHODS:
            if not request.user.is_tpo_admin:
                raise PermissionDenied("Only TPO admins can modify drives.")



class EligibleDrivesView(generics.ListAPIView):
    serializer_class = DriveListSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        student = self.request.user
        version = cache.get('drives_cache_version', 1)
        cache_key = f'eligible_drives:v{version}:student:{student.id}'

        cached_ids = cache.get(cache_key)
        if cached_ids is not None:
            return Drive.objects.filter(id__in=cached_ids)

        open_drives = Drive.objects.filter(
            status=Drive.Status.OPEN,
            application_deadline__gte=timezone.now(),
        ).prefetch_related('eligibility_rules')

        eligible_ids = []
        for drive in open_drives:
            rules = drive.eligibility_rules.all()
            if not rules or all(rule.is_student_eligible(student) for rule in rules):
                eligible_ids.append(drive.id)

        cache.set(cache_key, eligible_ids, timeout=300)
        return Drive.objects.filter(id__in=eligible_ids)

class RecruiterDriveCreateView(generics.CreateAPIView):
    """
    Recruiter posts a JD directly — always starts as pending_approval,
    regardless of what status the recruiter sends in the request body.
    A TPO must explicitly approve it before it goes live and becomes
    visible to students.
    """
    serializer_class = RecruiterDriveSerializer
    permission_classes = [IsRecruiter]

    def perform_create(self, serializer):
        serializer.save(
            recruiter=self.request.user,
            created_by=self.request.user,
            status=Drive.Status.PENDING_APPROVAL,
        )
        # Note: no notify_eligible_students call here anymore —
        # notifications only fire once a TPO approves the drive
        # (see ApproveDriveView below), not the moment a recruiter
        # submits it.class RecruiterDriveCreateView(generics.CreateAPIView):
    """
    Recruiter posts a JD directly — always starts as pending_approval,
    regardless of what status the recruiter sends in the request body.
    A TPO must explicitly approve it before it goes live and becomes
    visible to students.
    """
    serializer_class = RecruiterDriveSerializer
    permission_classes = [IsRecruiter]

    def perform_create(self, serializer):
        serializer.save(
            recruiter=self.request.user,
            created_by=self.request.user,
            status=Drive.Status.PENDING_APPROVAL,
        )
        # Note: no notify_eligible_students call here anymore —
        # notifications only fire once a TPO approves the drive
        # (see ApproveDriveView below), not the moment a recruiter
        # submits it.


class RecruiterDriveListView(generics.ListAPIView):
    """Recruiter views only the drives they've posted."""
    serializer_class = RecruiterDriveSerializer
    permission_classes = [IsRecruiter]

    def get_queryset(self):
        return Drive.objects.filter(recruiter=self.request.user).order_by('-created_at')


class ApproveDriveView(generics.GenericAPIView):
    """
    TPO-only: approves a pending_approval drive, flipping it to open
    and triggering the eligible-student notification exactly once,
    at approval time rather than at recruiter-submission time.
    """
    permission_classes = [IsTPOAdmin]
    queryset = Drive.objects.all()

    def post(self, request, pk):
        try:
            drive = Drive.objects.get(pk=pk)
        except Drive.DoesNotExist:
            return Response({'detail': 'Drive not found.'}, status=404)

        if drive.status != Drive.Status.PENDING_APPROVAL:
            return Response(
                {'detail': 'Only drives pending approval can be approved.'},
                status=400,
            )

        drive.status = Drive.Status.OPEN
        drive.save(update_fields=['status'])
        notify_eligible_students.delay(drive.id)

        return Response({'detail': f'Drive {drive.id} approved and now open.'})


class PendingDrivesView(generics.ListAPIView):
    """TPO views all drives awaiting approval."""
    serializer_class = DriveSerializer
    permission_classes = [IsTPOAdmin]

    def get_queryset(self):
        return Drive.objects.filter(
            status=Drive.Status.PENDING_APPROVAL
        ).order_by('-created_at')