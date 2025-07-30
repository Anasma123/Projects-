# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('owner', 'Owner'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')

    def is_admin(self):
        return self.role == 'admin'

    def is_staff_user(self):  # to avoid conflict with Django's `is_staff` boolean
        return self.role == 'staff'

    def is_owner(self):
        return self.role == 'owner'

    def __str__(self):
        return f"{self.username} ({self.role})"
