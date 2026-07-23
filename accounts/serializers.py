from rest_framework import serializers
from .models import User


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'first_name', 'last_name',
            'branch', 'cgpa', 'backlog_count', 'graduation_year', 'company_name',
        ]

class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Used for students to update their own profile fields.
    Deliberately excludes role, username, and other fields a
    student shouldn't be able to change themselves.
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number',
            'college', 'branch', 'cgpa', 'backlog_count', 'graduation_year',
        ]