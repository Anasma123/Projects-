from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    phone_validator = RegexValidator(regex=r'^\+?[1-9]\d{7,14}$', message='Enter a valid phone number in international format.')

    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=16, unique=True, validators=[phone_validator])
    email = models.EmailField(blank=True, null=True)
    profile_image = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} ({self.phone_number})'
