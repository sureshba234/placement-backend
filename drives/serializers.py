from rest_framework import serializers
from .models import Drive, EligibilityRule


class EligibilityRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EligibilityRule
        fields = [
            'id', 'min_cgpa', 'max_backlogs', 'allowed_branches',
            'min_graduation_year', 'max_graduation_year',
        ]


class DriveSerializer(serializers.ModelSerializer):
    """
    Full serializer — includes nested eligibility rules.
    Used for TPO create/update and detail views.
    """
    eligibility_rules = EligibilityRuleSerializer(many=True, required=False)

    class Meta:
        model = Drive
        fields = [
            'id', 'title', 'company_name', 'description', 'job_description',
            'status', 'application_deadline', 'created_by',
            'created_at', 'updated_at', 'eligibility_rules',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        rules_data = validated_data.pop('eligibility_rules', [])
        drive = Drive.objects.create(**validated_data)
        for rule_data in rules_data:
            EligibilityRule.objects.create(drive=drive, **rule_data)
        return drive


class DriveListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views (student's eligible-drives
    feed) — no need to ship full JD text and nested rules every time.
    """
    class Meta:
        model = Drive
        fields = [
            'id', 'title', 'company_name', 'status', 'application_deadline',
        ]

class RecruiterDriveSerializer(serializers.ModelSerializer):
    """
    Simplified drive creation for recruiters — no eligibility_rules
    nesting, since in this design TPOs own eligibility criteria;
    recruiters just post the JD and view results.
    """
    class Meta:
        model = Drive
        fields = [
            'id', 'title', 'company_name', 'description', 'job_description',
            'status', 'application_deadline', 'recruiter',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['recruiter', 'created_at', 'updated_at']