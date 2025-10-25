#!/usr/bin/env python
"""
Verification script for the new staff functionality.
This script demonstrates that the new full_name field and case-insensitive username validation work as expected.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bizeasy.settings')
django.setup()

from user.forms import StaffForm
from user.models import CustomUser

def test_new_staff_functionality():
    """Test the new staff functionality."""
    print("Testing new staff functionality...")
    
    # Test 1: Creating a user with full_name and username
    print("\nTest 1: Creating a user with full_name and username")
    form_data = {
        'full_name': 'John Doe',
        'username': 'johndoe',
        'email': 'john@example.com',
        'password': 'testpass123',
        'confirm_password': 'testpass123'
    }
    
    form = StaffForm(data=form_data)
    is_valid = form.is_valid()
    print(f"Form with full_name 'John Doe' and username 'johndoe' is valid: {is_valid}")
    
    if is_valid:
        user = form.save()
        print(f"User created successfully. Full name: {user.full_name}, Username: {user.username}")
        # Clean up
        user.delete()
    
    # Test 2: Case-insensitive username validation
    print("\nTest 2: Case-insensitive username validation")
    
    # Create a test user
    user = CustomUser.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    user.role = 'staff'
    user.save()
    
    # Try to create another user with the same username but different case
    form_data2 = {
        'full_name': 'Test User',
        'username': 'TestUser',  # Different case
        'email': 'test2@example.com',
        'password': 'testpass123',
        'confirm_password': 'testpass123'
    }
    
    form2 = StaffForm(data=form_data2)
    is_valid2 = form2.is_valid()
    print(f"Username 'TestUser' (different case from 'testuser') is valid: {is_valid2}")
    
    if not is_valid2 and hasattr(form2, 'errors') and form2.errors:
        # Print all errors
        print(f"Errors: {form2.errors}")
    
    # Clean up
    user.delete()
    
    print("\nNew staff functionality tests completed!")

if __name__ == '__main__':
    test_new_staff_functionality()