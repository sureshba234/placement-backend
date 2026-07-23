from rest_framework import serializers
from .models import Application
from drives.serializers import DriveListSerializer


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """
    Used when a student applies to a drive. Student is set from
    request.user in the view, not from client input — never trust
    the client to tell us who they are.
    """
    class Meta:
        model = Application
        fields = ['id', 'drive', 'resume', 'status', 'applied_at']
        read_only_fields = ['status', 'applied_at']

    def validate_drive(self, drive):
        from django.utils import timezone
        if drive.status != drive.Status.OPEN:
            raise serializers.ValidationError("This drive is not open for applications.")
        if drive.application_deadline < timezone.now():
            raise serializers.ValidationError("The application deadline has passed.")
        return drive

    def validate(self, data):
        request = self.context['request']
        drive = data['drive']
        # Re-check eligibility at write-time too — the eligible/ list
        # endpoint filters what a student SEES, but a student could
        # still POST directly to a drive they don't qualify for.
        rules = drive.eligibility_rules.all()
        if rules and not all(rule.is_student_eligible(request.user) for rule in rules):
            raise serializers.ValidationError(
                "You do not meet the eligibility criteria for this drive."
            )
        return data


class ApplicationDetailSerializer(serializers.ModelSerializer):
    """Used for student's own application list — shows drive info nested."""
    drive = DriveListSerializer(read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'drive', 'resume', 'status',
            'match_score', 'missing_skills', 'applied_at', 'updated_at',
        ]


class ApplicantSerializer(serializers.ModelSerializer):
    """
    TPO-facing view of an application — surfaces student identity
    and contact info alongside application status.
    """
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    student_email = serializers.EmailField(source='student.email', read_only=True)
    student_branch = serializers.CharField(source='student.branch', read_only=True)
    student_cgpa = serializers.DecimalField(
        source='student.cgpa', max_digits=4, decimal_places=2, read_only=True
    )

    class Meta:
        model = Application
        fields = [
            'id', 'student_name', 'student_email', 'student_branch',
            'student_cgpa', 'status', 'match_score', 'missing_skills',
            'applied_at',
        ]