from django.urls import path
from .views import (
    NotificationListView, NotificationMarkReadView,
    NotificationMarkAllReadView, ActivityLogListView
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-read'),
    path('mark-all-read/', NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),
    path('activity/', ActivityLogListView.as_view(), name='activity-list'),
]

