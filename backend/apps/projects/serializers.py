from rest_framework import serializers
from .models import Project, ProjectMembership, Deliverable, DeliverableVersion
from apps.clients.serializers import ClientSerializer
from apps.authentication.serializers import UserSerializer

class DeliverableVersionSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.ReadOnlyField(source='uploaded_by.get_full_name')

    class Meta:
        model = DeliverableVersion
        fields = [
            'id', 'deliverable', 'version_number', 'file_url', 'file_name',
            'file_size_bytes', 'file_type', 'notes', 'is_final', 'is_approved',
            'uploaded_by', 'uploaded_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class DeliverableSerializer(serializers.ModelSerializer):
    versions = DeliverableVersionSerializer(many=True, read_only=True)
    latest_version = serializers.SerializerMethodField()

    class Meta:
        model = Deliverable
        fields = [
            'id', 'project', 'title', 'description', 'format_type',
            'status', 'created_at', 'updated_at', 'versions', 'latest_version'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_latest_version(self, obj):
        latest = obj.versions.first()
        return DeliverableVersionSerializer(latest).data if latest else None


class ProjectSerializer(serializers.ModelSerializer):
    client_name = serializers.ReadOnlyField(source='client.name')
    client_company = serializers.ReadOnlyField(source='client.company_name')
    owner_name = serializers.ReadOnlyField(source='owner.get_full_name')
    deliverables_count = serializers.SerializerMethodField()
    tasks_count = serializers.SerializerMethodField()
    completed_tasks_count = serializers.SerializerMethodField()
    revisions_used = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'client', 'client_name', 'client_company',
            'owner', 'owner_name', 'description', 'project_type',
            'start_date', 'due_date', 'budget', 'currency', 'status',
            'priority', 'revision_allowance', 'brief_content',
            'reference_links', 'cover_image_url', 'created_at', 'updated_at',
            'deliverables_count', 'tasks_count', 'completed_tasks_count',
            'revisions_used'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_deliverables_count(self, obj):
        return obj.deliverables.count()

    def get_tasks_count(self, obj):
        return obj.tasks.count() if hasattr(obj, 'tasks') else 0

    def get_completed_tasks_count(self, obj):
        return obj.tasks.filter(status='done').count() if hasattr(obj, 'tasks') else 0

    def get_revisions_used(self, obj):
        if hasattr(obj, 'revisions'):
            return obj.revisions.filter(status__in=['in_progress', 'resolved']).count()
        return 0


class ProjectDetailSerializer(ProjectSerializer):
    deliverables = DeliverableSerializer(many=True, read_only=True)

    class Meta(ProjectSerializer.Meta):
        fields = ProjectSerializer.Meta.fields + ['deliverables']

