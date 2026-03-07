from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, render

from apps.roles.forms import RoleAssignmentForm
from apps.roles.models import UserRole

from .forms import LoginForm, ProfileUpdateForm, RegisterForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Welcome to Zyrovia. Your account is ready.')
        return redirect('core:dashboard')
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    form = LoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.cleaned_data['user']
        login(request, user)
        next_url = request.GET.get('next') or request.POST.get('next') or 'core:dashboard'
        messages.success(request, 'Signed in successfully.')
        return redirect(next_url)
    return render(request, 'users/login.html', {'form': form, 'next': request.GET.get('next', '')})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('core:dashboard')


@login_required
def profile_view(request):
    user = request.user
    profile_form = ProfileUpdateForm(request.POST or None, instance=user)
    role_form = RoleAssignmentForm(request.POST or None)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile' and profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('users:profile')
        if action == 'add_role' and role_form.is_valid():
            UserRole.assign_role(user=user, role=role_form.cleaned_data['role'])
            messages.success(request, 'Role added successfully.')
            return redirect('users:profile')
        if action == 'remove_role':
            role = request.POST.get('role')
            UserRole.remove_role(user=user, role=role)
            messages.success(request, 'Role removed successfully.')
            return redirect('users:profile')

    roles = user.assigned_roles.all()
    return render(request, 'users/profile.html', {'profile_form': profile_form, 'role_form': role_form, 'roles': roles})
