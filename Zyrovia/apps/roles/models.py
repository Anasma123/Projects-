from django.conf import settings
from django.db import models


class RoleChoices(models.TextChoices):
    CUSTOMER = 'customer', 'Customer'
    DRIVER = 'driver', 'Driver'
    SHOP_OWNER = 'shop_owner', 'Shop Owner'
    SERVICE_PROVIDER = 'service_provider', 'Service Provider'


class UserRole(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assigned_roles')
    role = models.CharField(max_length=32, choices=RoleChoices.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'role')
        ordering = ['role']

    def __str__(self):
        return f'{self.user_id}:{self.role}'

    @classmethod
    def assign_role(cls, user, role: str):
        cls.objects.get_or_create(user=user, role=role)

    @classmethod
    def remove_role(cls, user, role: str):
        cls.objects.filter(user=user, role=role).delete()
