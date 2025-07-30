from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import CustomUser  # Ensure this is your custom user model

def login_view(request):
    if request.user.is_authenticated:
        role = request.user.role
        return redirect_to_dashboard(role)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            role = user.role
            return redirect_to_dashboard(role)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


def redirect_to_dashboard(role):
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'staff':
        return redirect('staff_dashboard')
    elif role == 'owner':
        return redirect('owner_dashboard')
    else:
        return redirect('login')  # fallback

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


@login_required
@user_passes_test(lambda u: not u.is_superuser)
def staff_dashboard(request):
    return render(request, 'staff_dashboard.html')

@login_required
@user_passes_test(lambda u: not u.is_superuser)
def owner_dashboard(request):
    return render(request, 'owner_dashboard.html')
