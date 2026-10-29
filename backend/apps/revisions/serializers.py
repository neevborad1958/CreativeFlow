from rest_framework import serializers
from .models import RevisionRequest

class RevisionRequestSerializer(serializers.ModelSerializer):
    project_name = serializers.ReadOnlyField(source='project.name')
    deliverable_title = serializers.ReadOnlyField(source='deliverable.title')
    version_number = serializers.ReadOnlyField(source='version.version_number')
    requested_by_name = serializers.ReadOnlyField(source='requested_by.get_full_name')

    class Meta:
        model = RevisionRequest
        fields = [
            'id', 'project', 'project_name', 'deliverable', 'deliverable_title',
            'version', 'version_number', 'requested_by', 'requested_by_name',
            'title', 'description', 'reference_attachment_url', 'status',
            'freelancer_response', 'resolved_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

