from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """User profile to store preferences and settings."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    language = models.CharField(max_length=10, default='en')
    voice_speed = models.IntegerField(default=150)  # Words per minute
    voice_volume = models.FloatField(default=0.9)  # 0.0 to 1.0
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class VoiceCommand(models.Model):
    """Store voice command history for analysis and improvement."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    command_text = models.TextField()
    response_text = models.TextField()
    intent = models.CharField(max_length=50, blank=True)
    entities = models.JSONField(default=dict, blank=True)
    processing_time = models.FloatField(default=0.0)  # In seconds
    success = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Voice Command'
        verbose_name_plural = 'Voice Commands'

    def __str__(self):
        return f"Command: {self.command_text[:50]}..."


class SystemLog(models.Model):
    """System logs for monitoring and debugging."""
    LEVEL_CHOICES = [
        ('DEBUG', 'Debug'),
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('CRITICAL', 'Critical'),
    ]
    
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'System Log'
        verbose_name_plural = 'System Logs'

    def __str__(self):
        return f"{self.level}: {self.message[:50]}..."
