from rest_framework import serializers
from .models import ProjectFile

class ProjectFileSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.ReadOnlyField(source='uploaded_by.get_full_name')
    project_name = serializers.ReadOnlyField(source='project.name')

    class Meta:
        model = ProjectFile
        fields = [
            'id', 'project', 'project_name', 'name', 'file', 'file_url',
            'file_size_bytes', 'file_type', 'category', 'uploaded_by',
            'uploaded_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

