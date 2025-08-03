# templatetags/discount_extras.py
from django import template

register = template.Library()

@register.filter
def discount_percent(mrp, sale_rate):
    try:
        mrp = float(mrp)
        sale = float(sale_rate)
        if mrp > 0:
            return round((mrp - sale) * 100.0 / mrp, 1)
    except (ValueError, TypeError):
        pass
    return None
