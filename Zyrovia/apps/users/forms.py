from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import User


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))

    class Meta:
        model = User
        fields = ['full_name', 'phone_number', 'email', 'profile_image']

    def clean_phone_number(self):
        return User.objects.normalize_phone(self.cleaned_data['phone_number'])

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        if password:
            try:
                validate_password(password)
            except ValidationError as exc:
                self.add_error('password', exc)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    phone_number = forms.CharField(max_length=16)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}))

    def clean(self):
        cleaned_data = super().clean()
        phone_number = User.objects.normalize_phone(cleaned_data.get('phone_number'))
        password = cleaned_data.get('password')
        user = authenticate(phone_number=phone_number, password=password)
        if not user:
            raise forms.ValidationError('Invalid phone number or password.')
        if not user.is_active:
            raise forms.ValidationError('This account is inactive.')
        cleaned_data['user'] = user
        cleaned_data['phone_number'] = phone_number
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'phone_number', 'email', 'profile_image']

    def clean_phone_number(self):
        return User.objects.normalize_phone(self.cleaned_data['phone_number'])
