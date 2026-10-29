from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from .models import Task, TaskComment
from .serializers import TaskSerializer, TaskCommentSerializer

class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
        user = self.request.user if self.request.user.is_authenticated else None
        queryset = Task.objects.all().select_related('project', 'assignee')

        # Filter by project, status, priority, or assignee
        project_id = self.request.query_params.get('project')
        status_param = self.request.query_params.get('status')
        priority_param = self.request.query_params.get('priority')
        assignee_param = self.request.query_params.get('assignee')

        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if status_param and status_param != 'all':
            queryset = queryset.filter(status=status_param)
        if priority_param and priority_param != 'all':
            queryset = queryset.filter(priority=priority_param)
        if assignee_param:
            queryset = queryset.filter(assignee_id=assignee_param)

        return queryset


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all().select_related('project', 'assignee')
    serializer_class = TaskSerializer

    def perform_update(self, serializer):
        # Auto-stamp completion timestamp if task marked done
        instance = serializer.instance
        new_status = serializer.validated_data.get('status', instance.status)
        if new_status == 'done' and instance.status != 'done':
            serializer.save(completed_at=timezone.now())
        elif new_status != 'done':
            serializer.save(completed_at=None)
        else:
            serializer.save()


class TaskCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskCommentSerializer

    def get_queryset(self):
        task_id = self.kwargs.get('task_pk')
        return TaskComment.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        from apps.authentication.models import User
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        task_id = self.kwargs.get('task_pk')
        serializer.save(task_id=task_id, author=user)

