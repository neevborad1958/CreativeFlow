from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('freelancer', 'Freelancer / Studio Admin'),
        ('client', 'Client'),
        ('team_member', 'Team Member'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='freelancer')
    phone = models.CharField(max_length=30, blank=True, null=True)
    company_name = models.CharField(max_length=150, blank=True, null=True)
    title = models.CharField(max_length=100, blank=True, default='Creative Professional')
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=85.00)
    currency = models.CharField(max_length=10, default='USD')
    bio = models.TextField(blank=True, default='')
    avatar_url = models.CharField(max_length=500, blank=True, default='')

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    notifications_enabled = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    sound_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.username}"

