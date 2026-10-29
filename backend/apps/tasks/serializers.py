from rest_framework import serializers
from .models import Task, TaskComment
from apps.authentication.serializers import UserSerializer

class TaskCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.get_full_name')

    class Meta:
        model = TaskComment
        fields = ['id', 'task', 'author', 'author_name', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    project_name = serializers.ReadOnlyField(source='project.name')
    client_name = serializers.ReadOnlyField(source='project.client.name')
    assignee_name = serializers.ReadOnlyField(source='assignee.get_full_name')
    comments = TaskCommentSerializer(many=True, read_only=True)
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'project', 'project_name', 'client_name', 'title',
            'description', 'assignee', 'assignee_name', 'status',
            'priority', 'start_date', 'due_date', 'completed_at',
            'order_index', 'is_overdue', 'comments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_is_overdue(self, obj):
        from django.utils import timezone
        if obj.due_date and obj.status != 'done':
            return obj.due_date < timezone.now().date()
        return False

