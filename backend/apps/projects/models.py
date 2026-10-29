from django.db import models
from django.conf import settings
from apps.clients.models import Client

class Project(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('in_review', 'In Review'),
        ('changes_requested', 'Changes Requested'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    PROJECT_TYPES = [
        ('Brand Identity', 'Brand Identity'),
        ('UI/UX Design', 'UI/UX Design'),
        ('3D & Motion', '3D & Motion'),
        ('Video Production', 'Video Production'),
        ('Web Design & Dev', 'Web Design & Dev'),
        ('Design System', 'Design System'),
    ]

    name = models.CharField(max_length=250)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='projects')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
        null=True,
        blank=True
    )
    description = models.TextField(blank=True)
    project_type = models.CharField(max_length=50, choices=PROJECT_TYPES, default='UI/UX Design')
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    budget = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=10, default='USD')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='in_progress')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    revision_allowance = models.PositiveIntegerField(default=3)
    brief_content = models.TextField(blank=True, default='')
    reference_links = models.TextField(blank=True, default='')
    cover_image_url = models.CharField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.name} - {self.client.name}"


class ProjectMembership(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(max_length=50, default='collaborator')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')


class Deliverable(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('in_review', 'In Review'),
        ('changes_requested', 'Changes Requested'),
        ('approved', 'Approved'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='deliverables')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    format_type = models.CharField(max_length=50, default='Figma')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.title} ({self.project.name})"


class DeliverableVersion(models.Model):
    deliverable = models.ForeignKey(Deliverable, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField(default=1)
    file_url = models.CharField(max_length=500)
    file_name = models.CharField(max_length=255)
    file_size_bytes = models.BigIntegerField(default=0)
    file_type = models.CharField(max_length=100, default='image/png')
    notes = models.TextField(blank=True, default='')
    is_final = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']
        unique_together = ('deliverable', 'version_number')

    def __str__(self):
        return f"{self.deliverable.title} v{self.version_number}"

