"""
App configuration for the Bizeasy user application.
"""

# Django imports
from django.apps import AppConfig


class UserConfig(AppConfig):
    """Configuration class for the user app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'