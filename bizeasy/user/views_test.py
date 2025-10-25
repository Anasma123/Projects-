"""
Test views for debugging discount functionality.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Purchase, Product, Discount

def test_add_discount(request, purchase_id):
    """Test add discount functionality."""
    try:
        purchase = get_object_or_404(Purchase, id=purchase_id)
        return render(request, 'add_discount.html', {
            'purchase': purchase,
            'existing_discount': None
        })
    except Exception as e:
        print(f"Error in test_add_discount: {e}")
        import traceback
        traceback.print_exc()
        return render(request, 'add_discount.html', {
            'error': str(e)
        })