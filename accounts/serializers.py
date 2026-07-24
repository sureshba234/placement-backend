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


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'first_name', 'last_name',
            'branch', 'cgpa', 'backlog_count', 'graduation_year', 'company_name',
        ]


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number',
            'college', 'branch', 'cgpa', 'backlog_count', 'graduation_year',
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """
    Public registration endpoint. Role defaults to student —
    TPO admins and recruiters must be created via admin panel
    since those are privileged roles that shouldn't be
    self-assignable.
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name', 'role',
        ]

    def validate_role(self, value):
        # Prevent self-assignment of privileged roles
        if value in ['tpo_admin', 'recruiter']:
            raise serializers.ValidationError(
                "TPO admin and recruiter accounts must be created by an administrator."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user