"""
Custom template tags for the Bizeasy application.
Provides additional functionality for Django templates.
"""

# Django imports
from django import template

# Register the template library
register = template.Library()


# ==============================================================================
# Mathematical Operations
# ==============================================================================

@register.filter
def multiply(value, arg):
    """Multiply two values together."""
    return value * arg