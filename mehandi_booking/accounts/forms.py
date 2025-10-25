from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
import re

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True)
    phone = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'full_name', 'email', 'password1', 'password2', 'phone', 'address')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the default label for full_name
        self.fields['full_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['phone'].widget.attrs.update({'class': 'form-control'})
        self.fields['address'].widget.attrs.update({'class': 'form-control', 'rows': 3})
        
        # Set placeholders
        self.fields['username'].widget.attrs.update({'placeholder': 'Enter your username'})
        self.fields['full_name'].widget.attrs.update({'placeholder': 'Enter your full name'})
        self.fields['email'].widget.attrs.update({'placeholder': 'Enter your email address'})
        self.fields['phone'].widget.attrs.update({'placeholder': 'Enter your 10-digit phone number'})
        self.fields['address'].widget.attrs.update({'placeholder': 'Enter your address'})
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            # Call the parent method to handle the case when username is empty
            return super().clean_username()
        
        # Check for case-insensitive duplicates
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("A user with that username already exists (case-insensitive).")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        
        # Check for duplicate emails
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:
            raise forms.ValidationError("Phone number is required.")
        
        # Remove any non-digit characters
        phone_digits = re.sub(r'\D', '', phone)
        
        # Check if it's exactly 10 digits
        if len(phone_digits) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        
        # Check if it contains only digits
        if not phone_digits.isdigit():
            raise forms.ValidationError("Phone number must contain only digits.")
        
        return phone
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Set the full name in both first_name and full_name fields
        user.first_name = self.cleaned_data['full_name']
        user.full_name = self.cleaned_data['full_name']
        user.user_type = 'customer'  # All new registrations are customers
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
        return user