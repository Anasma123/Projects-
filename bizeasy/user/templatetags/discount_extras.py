"""
Discount template filters for the Bizeasy application.
Provides discount calculation functionality for Django templates.
"""

# Django imports
from django import template

# Register the template library
register = template.Library()


# ==============================================================================
# Discount Calculations
# ==============================================================================

@register.filter
def discount_percent(mrp, sale_rate):
    """Calculate discount percentage from MRP and sale rate."""
    try:
        mrp = float(mrp)
        sale = float(sale_rate)
        if mrp > 0:
            return round((mrp - sale) * 100.0 / mrp, 1)
    except (ValueError, TypeError):
        pass
    return None