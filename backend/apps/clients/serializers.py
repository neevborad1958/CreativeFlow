from rest_framework import serializers
from .models import Client

class ClientSerializer(serializers.ModelSerializer):
    projects_count = serializers.SerializerMethodField()
    active_projects_count = serializers.SerializerMethodField()
    total_invoiced = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            'id', 'created_by', 'user', 'name', 'company_name',
            'email', 'phone', 'website', 'address', 'notes',
            'avatar_url', 'is_archived', 'created_at', 'updated_at',
            'projects_count', 'active_projects_count', 'total_invoiced'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_projects_count(self, obj):
        return obj.projects.count() if hasattr(obj, 'projects') else 0

    def get_active_projects_count(self, obj):
        if hasattr(obj, 'projects'):
            return obj.projects.filter(status__in=['in_progress', 'in_review', 'changes_requested']).count()
        return 0

    def get_total_invoiced(self, obj):
        if hasattr(obj, 'invoices'):
            return sum(inv.total for inv in obj.invoices.exclude(status='cancelled'))
        return 0.0

