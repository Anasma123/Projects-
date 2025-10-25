"""
Mathematical template filters for the Bizeasy application.
Provides mathematical operations for Django templates.
"""

# Django imports
from django import template

# Register the template library
register = template.Library()


# ==============================================================================
# Mathematical Operations
# ==============================================================================

@register.filter
def mul(value, arg):
    """Multiplies the arg and the value."""
    try:
        return value * arg
    except (ValueError, TypeError):
        return ''