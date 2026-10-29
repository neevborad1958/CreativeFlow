from django.db import models
from django.conf import settings
from apps.projects.models import DeliverableVersion

class Approval(models.Model):
    DECISION_CHOICES = [
        ('approved', 'Approved'),
        ('changes_requested', 'Changes Requested'),
        ('rejected', 'Rejected'),
    ]

    version = models.ForeignKey(DeliverableVersion, on_delete=models.CASCADE, related_name='approvals')
    decided_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    decision = models.CharField(max_length=30, choices=DECISION_CHOICES, default='approved')
    feedback = models.TextField(blank=True, default='')
    client_signature = models.CharField(max_length=150, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_decision_display()} - {self.version} by {self.decided_by}"

