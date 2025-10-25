#!/usr/bin/env python
"""
Verification script for username validation implementation.
This script demonstrates that the username validation works as expected.
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

def test_username_validation():
    """Test the username validation functionality."""
    print("Testing username validation...")
    
    # Create a test user
    user = CustomUser.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )
    user.role = 'staff'
    user.save()
    
    print("Created test user with username 'testuser'")
    
    # Test 1: Case-sensitive validation - different case should be allowed
    print("\nTest 1: Case-sensitive validation")
    form_data = {
        'username': 'TestUser',  # Different case
        'email': 'test2@example.com',
        'password': 'testpass123',
        'confirm_password': 'testpass123'
    }
    
    form = StaffForm(data=form_data)
    is_valid = form.is_valid()
    print(f"Username 'TestUser' (different case) is valid: {is_valid}")
    
    if not is_valid and 'username' in form.errors:
        print(f"Errors: {form.errors['username']}")
    
    # Test 2: Exact duplicate should be rejected
    print("\nTest 2: Exact duplicate validation")
    form_data2 = {
        'username': 'testuser',  # Exact same username
        'email': 'test3@example.com',
        'password': 'testpass123',
        'confirm_password': 'testpass123'
    }
    
    form2 = StaffForm(data=form_data2)
    is_valid2 = form2.is_valid()
    print(f"Username 'testuser' (exact duplicate) is valid: {is_valid2}")
    
    if not is_valid2 and 'username' in form2.errors:
        print(f"Errors: {form2.errors['username']}")
    
    # Clean up
    user.delete()
    
    print("\nValidation tests completed!")

if __name__ == '__main__':
    test_username_validation()