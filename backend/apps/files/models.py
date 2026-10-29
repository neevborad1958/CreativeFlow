from django.db import models
from django.conf import settings
from apps.projects.models import Project

class ProjectFile(models.Model):
    CATEGORY_CHOICES = [
        ('asset', 'Asset'),
        ('reference', 'Reference Material'),
        ('brand_guideline', 'Brand Guideline'),
        ('deliverable_export', 'Deliverable Export'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='project_files/', blank=True, null=True)
    file_url = models.CharField(max_length=500, blank=True, default='')
    file_size_bytes = models.BigIntegerField(default=0)
    file_type = models.CharField(max_length=100, default='application/octet-stream')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='asset')
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.project.name})"

