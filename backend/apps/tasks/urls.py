from django.urls import path
from .views import TaskListCreateView, TaskDetailView, TaskCommentListCreateView

urlpatterns = [
    path('', TaskListCreateView.as_view(), name='task-list-create'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    path('<int:task_pk>/comments/', TaskCommentListCreateView.as_view(), name='task-comments-list-create'),
]

