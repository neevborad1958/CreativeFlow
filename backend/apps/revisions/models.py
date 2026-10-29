from django.db import models
from django.conf import settings
from apps.projects.models import Project, Deliverable, DeliverableVersion

class RevisionRequest(models.Model):
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('in_review', 'In Review'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='revisions')
    deliverable = models.ForeignKey(Deliverable, on_delete=models.CASCADE, related_name='revision_requests')
    version = models.ForeignKey(DeliverableVersion, on_delete=models.SET_NULL, null=True, blank=True)
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default='Revision Request')
    description = models.TextField()
    reference_attachment_url = models.CharField(max_length=500, blank=True, default='')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='submitted')
    freelancer_response = models.TextField(blank=True, default='')
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Revision #{self.id} for {self.deliverable.title} ({self.get_status_display()})"

