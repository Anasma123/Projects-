from django.test import TestCase
from django.core.exceptions import ValidationError
from .forms import StaffForm
from .models import CustomUser


class StaffFormTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user.role = 'staff'
        self.user.save()

    def test_username_case_insensitive_validation(self):
        """Test that username validation is case-insensitive"""
        # Try to create a user with the same username but different case
        form_data = {
            'full_name': 'Test User',
            'username': 'TestUser',  # Different case
            'email': 'test2@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        
        form = StaffForm(data=form_data)
        # This should be invalid since username validation is case-insensitive
        is_valid = form.is_valid()
        self.assertFalse(is_valid)

    def test_username_duplicate_case_insensitive(self):
        """Test that username duplicates are rejected (case-insensitive)"""
        # Try to create a user with the exact same username
        form_data = {
            'full_name': 'Test User',
            'username': 'testuser',  # Exact same username
            'email': 'test2@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        
        form = StaffForm(data=form_data)
        # This should be invalid since username is exactly the same
        is_valid = form.is_valid()
        self.assertFalse(is_valid)
        
    def test_full_name_field(self):
        """Test that full_name field is properly handled"""
        # Try to create a user with full_name
        form_data = {
            'full_name': 'John Doe',
            'username': 'johndoe',
            'email': 'john@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        
        form = StaffForm(data=form_data)
        # This should be valid
        self.assertTrue(form.is_valid())