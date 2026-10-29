from rest_framework import serializers
from .models import Notification, ActivityLog

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'recipient', 'title', 'message', 'notification_type', 'link', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class ActivityLogSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.get_full_name')

    class Meta:
        model = ActivityLog
        fields = ['id', 'user', 'user_name', 'action', 'target_type', 'target_id', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

