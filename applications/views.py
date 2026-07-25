from rest_framework.response import Response
import csv
from django.http import HttpResponse
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.core.cache import cache
from django.db.models import Count
from accounts.permissions import IsStudent, IsTPOAdmin, IsRecruiter
from django.db.models import Count, Q
from django.conf import settings
from .tasks import trigger_match_scoring


from accounts.permissions import IsStudent, IsTPOAdmin
from .models import Application
from .serializers import (
    ApplicationCreateSerializer,
    ApplicationDetailSerializer,
    ApplicantSerializer,
)
from .tasks import trigger_match_scoring


class ApplyToDriveView(generics.CreateAPIView):
    """Student applies to a drive."""
    serializer_class = ApplicationCreateSerializer
    permission_classes = [IsStudent]

    def perform_create(self, serializer):
        application = serializer.save(student=self.request.user)
        if settings.USE_CELERY:
            trigger_match_scoring.delay(application.id)
        else:
            trigger_match_scoring(application.id)


class MyApplicationsView(generics.ListAPIView):
    """Student views their own applications across all drives."""
    serializer_class = ApplicationDetailSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return Application.objects.filter(
            student=self.request.user
        ).select_related('drive').order_by('-applied_at')


class DriveApplicantsView(generics.ListAPIView):
    """
    TPO views all applicants for a specific drive.
    URL: /api/applications/drive/<drive_id>/applicants/
    """
    serializer_class = ApplicantSerializer
    permission_classes = [IsTPOAdmin]

    def get_queryset(self):
        drive_id = self.kwargs['drive_id']
        return Application.objects.filter(
            drive_id=drive_id
        ).select_related('student').order_by('-match_score', '-applied_at')


class UpdateApplicationStatusView(generics.UpdateAPIView):
    """TPO updates an applicant's status (shortlisted/rejected/selected)."""
    queryset = Application.objects.all()
    serializer_class = ApplicantSerializer
    permission_classes = [IsTPOAdmin]
    http_method_names = ['patch']

    def get_serializer(self, *args, **kwargs):
        kwargs['partial'] = True
        return super().get_serializer(*args, **kwargs)


class ExportApplicantsCSVView(generics.GenericAPIView):
    """
    TPO exports all applicants for a drive as CSV.
    Kept as a plain APIView-style export rather than a serializer
    round-trip since we're streaming a file response, not JSON.
    """
    permission_classes = [IsTPOAdmin]

    def get(self, request, drive_id):
        applications = Application.objects.filter(
            drive_id=drive_id
        ).select_related('student', 'drive')

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="applicants_drive_{drive_id}.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Student Name', 'Email', 'Branch', 'CGPA',
            'Status', 'Match Score', 'Applied At',
        ])

        for app in applications:
            writer.writerow([
                app.student.get_full_name() or app.student.username,
                app.student.email,
                app.student.branch,
                app.student.cgpa,
                app.status,
                app.match_score or '',
                app.applied_at.strftime('%Y-%m-%d %H:%M'),
            ])

        return response


class DriveAnalyticsView(generics.GenericAPIView):
    """
    TPO-facing: applicant count breakdown by status for a drive.
    Cached for 2 minutes — analytics dashboards don't need to be
    second-by-second fresh, and this avoids re-running a GROUP BY
    query on every dashboard refresh/poll.
    """
    permission_classes = [IsTPOAdmin]

    def get(self, request, drive_id):
        cache_key = f'drive_analytics:{drive_id}'
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        counts = (
            Application.objects.filter(drive_id=drive_id)
            .values('status')
            .annotate(count=Count('id'))
        )
        data = {row['status']: row['count'] for row in counts}
        data['total'] = sum(data.values())

        cache.set(cache_key, data, timeout=120)  # 2 minutes
        return Response(data)

class RecruiterShortlistView(generics.ListAPIView):
    """
    Recruiter views shortlisted (or selected) candidates for drives
    they posted. Recruiters only see candidates who've been marked
    'shortlisted' or 'selected' — not the full raw applicant pool,
    which stays TPO-only via DriveApplicantsView.
    """
    serializer_class = ApplicantSerializer
    permission_classes = [IsRecruiter]

    def get_queryset(self):
        drive_id = self.kwargs['drive_id']
        return Application.objects.filter(
            drive_id=drive_id,
            drive__recruiter=self.request.user,
            status__in=['shortlisted', 'selected'],
        ).select_related('student').order_by('-match_score')


class OverallAnalyticsView(generics.GenericAPIView):
    """
    TPO-facing: institution-wide placement stats — selected count
    by branch, and applicant/selection totals per drive. Distinct
    from DriveAnalyticsView (Step 11.7), which is scoped to a
    single drive's status breakdown.
    """
    permission_classes = [IsTPOAdmin]

    def get(self, request):
        cache_key = 'overall_analytics'
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        # Placement % by branch: selected count vs total applications
        # per branch, computed via the student FK relation.
        branch_stats = (
            Application.objects.values('student__branch')
            .annotate(
                total=Count('id'),
                selected=Count('id', filter=Q(status='selected')),
            )
            .exclude(student__branch='')
            .order_by('student__branch')
        )

        branch_data = [
            {
                'branch': row['student__branch'],
                'total': row['total'],
                'selected': row['selected'],
                'placement_rate': round((row['selected'] / row['total']) * 100, 1) if row['total'] else 0,
            }
            for row in branch_stats
        ]

        # Drive-wise stats: applicant count + selected count per drive
        drive_stats = (
            Application.objects.values('drive__id', 'drive__title', 'drive__company_name')
            .annotate(
                total=Count('id'),
                selected=Count('id', filter=Q(status='selected')),
            )
            .order_by('-total')
        )

        drive_data = [
            {
                'drive_id': row['drive__id'],
                'title': row['drive__title'],
                'company_name': row['drive__company_name'],
                'total': row['total'],
                'selected': row['selected'],
            }
            for row in drive_stats
        ]

        data = {'by_branch': branch_data, 'by_drive': drive_data}
        cache.set(cache_key, data, timeout=120)  # 2 minutes, same TTL as DriveAnalyticsView
        return Response(data)


class MyScoreHistoryView(generics.ListAPIView):
    """
    Student-facing: their own match scores across all applications,
    ordered chronologically — used to chart improvement (or decline)
    over time as they apply to more drives with different resumes.
    """
    serializer_class = ApplicationDetailSerializer
    permission_classes = [IsStudent]

    def get_queryset(self):
        return Application.objects.filter(
            student=self.request.user,
            match_score__isnull=False,
        ).select_related('drive').order_by('applied_at')