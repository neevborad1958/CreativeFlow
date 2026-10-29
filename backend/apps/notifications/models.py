from django.db import models
from django.conf import settings

class Notification(models.Model):
    TYPE_CHOICES = [
        ('deadline', 'Deadline Alert'),
        ('revision', 'Revision Update'),
        ('approval', 'Client Approval'),
        ('invoice', 'Invoice Generated'),
        ('payment', 'Payment Received'),
        ('task', 'Task Assigned'),
    ]

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='task')
    link = models.CharField(max_length=500, blank=True, default='')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.title} for {self.recipient}"


class ActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=50)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} {self.action} at {self.created_at}"

