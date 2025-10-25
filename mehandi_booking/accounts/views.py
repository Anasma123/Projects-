from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import CustomUserCreationForm
from .models import User
from gallery.models import Category, SubCategory, Design
from booking.models import Booking, Payment
from admin_panel.models import Feedback

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect based on user type
            # Get the user from the custom User model
            try:
                custom_user = User.objects.get(pk=user.pk)
                if custom_user.user_type == 'admin':
                    return redirect('admin_home')
                else:
                    # Check if there's a next parameter to redirect to
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('user_home')
            except User.DoesNotExist:
                # Default to user home if user_type is not set
                return redirect('user_home')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'accounts/login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')

def home(request):
    # Get some designs to display on the home page
    featured_designs = Design.objects.all()[:6]  # Get first 6 designs
    categories = Category.objects.all()
    
    # Check if there's a specific design ID in the URL
    design_id = request.GET.get('design')
    specific_design = None
    if design_id:
        try:
            specific_design = get_object_or_404(Design, id=design_id)
        except:
            specific_design = None
    
    # Redirect authenticated users to their respective dashboards
    if request.user.is_authenticated:
        # Get the user from the custom User model
        try:
            custom_user = User.objects.get(pk=request.user.pk)
            if custom_user.user_type == 'admin':
                return redirect('admin_home')
            else:
                # Check if there's a next parameter to redirect to
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('user_home')
        except User.DoesNotExist:
            # Default to user home if user_type is not set
            return redirect('user_home')
    
    # For non-authenticated users, render the home page with session info and designs
    context = {
        'featured_designs': featured_designs,
        'categories': categories,
        'specific_design': specific_design,
        'gallery_session_active': request.session.get('last_visited_gallery', False),
        'last_viewed_design': request.session.get('last_viewed_design', None),
        'last_viewed_design_name': request.session.get('last_viewed_design_name', ''),
    }
    
    return render(request, 'accounts/home.html', context)

def admin_home(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Access denied!')
        return redirect('home')
    
    # Check if user has user_type attribute and if it's admin
    try:
        custom_user = User.objects.get(pk=request.user.pk)
        if custom_user.user_type != 'admin':
            messages.error(request, 'Access denied!')
            return redirect('home')
    except User.DoesNotExist:
        messages.error(request, 'Access denied!')
        return redirect('home')
    
    # Get statistics for admin dashboard
    total_bookings = Booking.objects.count()
    pending_bookings = Booking.objects.filter(status='pending').count()
    total_designs = Design.objects.count()
    total_feedback = Feedback.objects.count()
    
    context = {
        'total_bookings': total_bookings,
        'pending_bookings': pending_bookings,
        'total_designs': total_designs,
        'total_feedback': total_feedback,
    }
    
    return render(request, 'accounts/admin_home.html', context)

def user_home(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Access denied!')
        return redirect('home')
    
    # Check if user has user_type attribute and if it's admin
    try:
        custom_user = User.objects.get(pk=request.user.pk)
        if custom_user.user_type == 'admin':
            messages.error(request, 'Access denied!')
            return redirect('home')
    except User.DoesNotExist:
        pass  # Continue if user_type is not set
    
    # Get statistics for user dashboard
    my_bookings_count = Booking.objects.filter(customer=request.user).count()
    active_bookings_count = Booking.objects.filter(customer=request.user, status='pending').count()
    
    # Calculate total spent
    payments = Payment.objects.filter(booking__customer=request.user, status='completed')
    total_spent = sum(payment.amount for payment in payments)
    
    context = {
        'my_bookings_count': my_bookings_count,
        'active_bookings_count': active_bookings_count,
        'total_spent': total_spent,
    }
    
    return render(request, 'accounts/user_home.html', context)