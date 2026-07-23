from rest_framework import serializers
from .models import Resume


class ResumeUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'file', 'is_parsed', 'parsed_data', 'uploaded_at']
        read_only_fields = ['is_parsed', 'parsed_data', 'uploaded_at']
