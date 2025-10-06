# C:\Users\user\OneDrive\Desktop\bizeasy\bizeasy\user\templatetags\math_filters.py

from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiplies the arg and the value"""
    try:
        return value * arg
    except (ValueError, TypeError):
        return ''