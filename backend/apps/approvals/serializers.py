from rest_framework import serializers
from .models import Approval

class ApprovalSerializer(serializers.ModelSerializer):
    decided_by_name = serializers.ReadOnlyField(source='decided_by.get_full_name')
    deliverable_title = serializers.ReadOnlyField(source='version.deliverable.title')
    version_number = serializers.ReadOnlyField(source='version.version_number')
    project_id = serializers.ReadOnlyField(source='version.deliverable.project.id')
    project_name = serializers.ReadOnlyField(source='version.deliverable.project.name')

    class Meta:
        model = Approval
        fields = [
            'id', 'version', 'decided_by', 'decided_by_name', 'decision',
            'feedback', 'client_signature', 'created_at',
            'deliverable_title', 'version_number', 'project_id', 'project_name'
        ]
        read_only_fields = ['id', 'created_at']

