from django.conf import settings
from django.db import models


class ReportTargetType(models.TextChoices):
    DRIVER = 'driver', 'Driver'
    SHOP = 'shop', 'Shop'
    SERVICE_PROVIDER = 'service_provider', 'Service Provider'


class PlatformReport(models.Model):
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submitted_reports')
    target_type = models.CharField(max_length=32, choices=ReportTargetType.choices)
    target_id = models.PositiveIntegerField()
    reason = models.TextField(max_length=1200)
    is_resolved = models.BooleanField(default=False)
    resolution_note = models.CharField(max_length=255, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_reports',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['is_resolved', '-created_at']

    def __str__(self):
        return f'{self.target_type}:{self.target_id} ({self.reporter_id})'
