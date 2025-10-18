from typing import TYPE_CHECKING, Any, TypedDict
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import timedelta
import csv
import json
from courses.models import Course, Module, Lesson, Enrollment, Payment, LessonProgress
from django.contrib.auth.models import User

# Type hints for annotated querysets
class CourseWithStats(TypedDict, total=False):
    """Type hint for Course objects with annotations"""
    enrollment_count: int
    total_revenue: float

class UserWithStats(TypedDict, total=False):
    """Type hint for User objects with annotations"""
    enrollment_count: int
    total_spent: float


def is_admin(user):
    """Check if user is admin (staff or superuser)"""
    return user.is_staff or user.is_superuser


def admin_login(request):
    """Admin login view"""
    if request.user.is_authenticated and is_admin(request.user):
        return redirect('lms_admin:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Static credentials for simple authentication
        if username == 'admin' and password == 'admin123':
            # Try to get or create admin user
            user, created = User.objects.get_or_create(
                username='admin',
                defaults={'is_staff': True, 'is_superuser': True}
            )
            if created:
                user.set_password('admin123')
                user.save()
            
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('lms_admin:dashboard')
        else:
            messages.error(request, 'Invalid credentials!')
    
    return render(request, 'lms_admin/login.html')


@login_required
@user_passes_test(is_admin)
def admin_logout(request):
    """Admin logout view"""
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('lms_admin:login')


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """Admin dashboard with comprehensive analytics"""
    # Basic stats
    courses = Course.objects.all()
    total_courses = courses.count()
    total_users = User.objects.filter(is_staff=False).count()
    total_enrollments = Enrollment.objects.count()
    
    # Revenue stats
    total_revenue = Payment.objects.filter(status='completed').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Recent enrollments (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_enrollments = Enrollment.objects.filter(
        enrolled_at__gte=thirty_days_ago
    ).count()
    
    # Top courses by enrollment
    top_courses = Course.objects.annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-enrollment_count')[:5]
    
    # Enrollment trend data (last 7 days)
    enrollment_trend = []
    for i in range(7):
        date = timezone.now() - timedelta(days=6-i)
        count = Enrollment.objects.filter(
            enrolled_at__date=date.date()
        ).count()
        enrollment_trend.append({
            'date': date.strftime('%m/%d'),
            'count': count
        })
    
    # Revenue breakdown by course
    revenue_by_course = Payment.objects.filter(
        status='completed'
    ).values(
        'course__title'
    ).annotate(
        revenue=Sum('amount'),
        count=Count('id')
    ).order_by('-revenue')[:5]
    
    # Recent payments
    recent_payments = Payment.objects.select_related(
        'user', 'course'
    ).order_by('-created_at')[:10]
    
    context = {
        'courses': courses,
        'total_courses': total_courses,
        'total_users': total_users,
        'total_enrollments': total_enrollments,
        'total_revenue': total_revenue,
        'recent_enrollments': recent_enrollments,
        'top_courses': top_courses,
        'enrollment_trend': json.dumps(enrollment_trend),
        'revenue_by_course': revenue_by_course,
        'recent_payments': recent_payments,
    }
    return render(request, 'lms_admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def create_course(request):
    """Create new course"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price', 0)
        is_free = request.POST.get('is_free') == 'on'
        image = request.FILES.get('image')
        
        course = Course.objects.create(
            title=title,
            description=description,
            price=price,
            is_free=is_free,
            image=image,
            created_by=request.user
        )
        
        messages.success(request, f'Course "{title}" created successfully!')
        return JsonResponse({'success': True, 'course_id': course.id})
    
    return render(request, 'lms_admin/create_course.html')


@login_required
@user_passes_test(is_admin)
def edit_course(request, course_id):
    """Edit existing course"""
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        course.title = request.POST.get('title')
        course.description = request.POST.get('description')
        course.price = request.POST.get('price', 0)
        course.is_free = request.POST.get('is_free') == 'on'
        
        if request.FILES.get('image'):
            course.image = request.FILES.get('image')
        
        course.save()
        messages.success(request, f'Course "{course.title}" updated successfully!')
        return redirect('lms_admin:dashboard')
    
    context = {'course': course}
    return render(request, 'lms_admin/edit_course.html', context)


@login_required
@user_passes_test(is_admin)
def delete_course(request, course_id):
    """Delete course"""
    course = get_object_or_404(Course, id=course_id)
    course_title = course.title
    course.delete()
    messages.success(request, f'Course "{course_title}" deleted successfully!')
    return redirect('lms_admin:dashboard')


@login_required
@user_passes_test(is_admin)
def add_module(request, course_id):
    """Add module to course"""
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        order = request.POST.get('order', 0)
        
        module = Module.objects.create(
            course=course,
            title=title,
            description=description,
            order=order
        )
        
        messages.success(request, f'Module "{title}" added successfully!')
        return JsonResponse({'success': True, 'module_id': module.id})
    
    # Redirect to course detail page where the modal exists
    return redirect('lms_admin:course_detail', course_id=course_id)


@login_required
@user_passes_test(is_admin)
def add_lesson(request, module_id):
    """Add lesson to module"""
    module = get_object_or_404(Module, id=module_id)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        lesson_type = request.POST.get('lesson_type')
        content = request.POST.get('content', '')
        video_url = request.POST.get('video_url', '')
        order = request.POST.get('order', 0)
        video_file = request.FILES.get('video_file')
        resource_file = request.FILES.get('resource_file')
        
        lesson = Lesson.objects.create(
            module=module,
            title=title,
            lesson_type=lesson_type,
            content=content,
            video_url=video_url,
            video_file=video_file,
            resource_file=resource_file,
            order=order
        )
        
        messages.success(request, f'Lesson "{title}" added successfully!')
        return JsonResponse({'success': True, 'lesson_id': lesson.id})
    
    # Redirect to course detail page where the modal exists
    course_id = module.course.id
    return redirect('lms_admin:course_detail', course_id=course_id)


@login_required
@user_passes_test(is_admin)
def edit_lesson(request, lesson_id):
    """Edit existing lesson"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    if request.method == 'POST':
        lesson.title = request.POST.get('title')
        lesson.lesson_type = request.POST.get('lesson_type')
        lesson.content = request.POST.get('content', '')
        lesson.video_url = request.POST.get('video_url', '')
        lesson.order = request.POST.get('order', 0)
        
        if request.FILES.get('video_file'):
            lesson.video_file = request.FILES.get('video_file')
        
        if request.FILES.get('resource_file'):
            lesson.resource_file = request.FILES.get('resource_file')
        
        lesson.save()
        messages.success(request, f'Lesson "{lesson.title}" updated successfully!')
        return JsonResponse({'success': True, 'lesson_id': lesson.id})
    
    context = {'lesson': lesson}
    return JsonResponse(context)


@login_required
@user_passes_test(is_admin)
def delete_lesson(request, lesson_id):
    """Delete lesson"""
    lesson = get_object_or_404(Lesson, id=lesson_id)
    course_id = lesson.module.course.id
    lesson_title = lesson.title
    lesson.delete()
    messages.success(request, f'Lesson "{lesson_title}" deleted successfully!')
    return redirect('lms_admin:course_detail', course_id=course_id)


@login_required
@user_passes_test(is_admin)
def course_detail(request, course_id):
    """View course details with modules and lessons"""
    course = get_object_or_404(Course, id=course_id)
    modules = course.modules.all()
    
    context = {
        'course': course,
        'modules': modules,
    }
    return render(request, 'lms_admin/course_detail.html', context)


@login_required
@user_passes_test(is_admin)
def user_management(request):
    """User management view with filters and actions"""
    # Get filter parameters
    search_query = request.GET.get('search', '')
    enrollment_filter = request.GET.get('enrollment', '')
    
    # Base queryset
    users = User.objects.filter(is_staff=False).annotate(
        enrollment_count=Count('enrollments'),
        total_spent=Sum('payments__amount', filter=Q(payments__status='completed'))
    )
    
    # Apply search filter
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Apply enrollment filter
    if enrollment_filter == 'active':
        users = users.filter(enrollment_count__gt=0)
    elif enrollment_filter == 'inactive':
        users = users.filter(enrollment_count=0)
    
    users = users.order_by('-date_joined')
    
    context = {
        'users': users,
        'search_query': search_query,
        'enrollment_filter': enrollment_filter,
    }
    return render(request, 'lms_admin/user_management.html', context)


@login_required
@user_passes_test(is_admin)
def toggle_user_status(request, user_id):
    """Toggle user active/inactive status"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id, is_staff=False)
        user.is_active = not user.is_active
        user.save()
        
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User "{user.username}" has been {status}.')
        return redirect('lms_admin:user_management')
    
    return redirect('lms_admin:user_management')


@login_required
@user_passes_test(is_admin)
def export_data(request):
    """Export data to CSV (courses, enrollments, transactions)"""
    export_type = request.GET.get('type', 'courses')
    
    response = HttpResponse(content_type='text/csv')
    
    if export_type == 'courses':
        response['Content-Disposition'] = 'attachment; filename="courses_data.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Title', 'Price', 'Is Free', 'Created By', 'Enrollments', 'Revenue', 'Created At'])
        
        courses = Course.objects.annotate(
            enrollment_count=Count('enrollments'),
            total_revenue=Sum('payments__amount', filter=Q(payments__status='completed'))
        )
        
        for course in courses:
            writer.writerow([
                course.id,
                course.title,
                course.price,
                'Yes' if course.is_free else 'No',
                course.created_by.username,
                course.enrollment_count,
                course.total_revenue or 0,
                course.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
    
    elif export_type == 'enrollments':
        response['Content-Disposition'] = 'attachment; filename="enrollments_data.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'User', 'Email', 'Course', 'Enrolled Date', 'Progress', 'Completed'])
        
        enrollments = Enrollment.objects.select_related('user', 'course')
        
        for enrollment in enrollments:
            writer.writerow([
                enrollment.id,
                enrollment.user.username,
                enrollment.user.email,
                enrollment.course.title,
                enrollment.enrolled_at.strftime('%Y-%m-%d %H:%M:%S'),
                f"{enrollment.progress}%",
                'Yes' if enrollment.completed else 'No'
            ])
    
    elif export_type == 'transactions':
        response['Content-Disposition'] = 'attachment; filename="transactions_data.csv"'
        writer = csv.writer(response)
        writer.writerow(['Order ID', 'Payment ID', 'User', 'Course', 'Amount', 'Status', 'Date'])
        
        payments = Payment.objects.select_related('user', 'course')
        
        for payment in payments:
            writer.writerow([
                payment.order_id,
                payment.payment_id,
                payment.user.username,
                payment.course.title,
                payment.amount,
                payment.status,
                payment.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
    
    else:
        # Export all users
        response['Content-Disposition'] = 'attachment; filename="users_data.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Username', 'Email', 'First Name', 'Last Name', 'Enrollments', 'Total Spent', 'Joined Date'])
        
        users = User.objects.filter(is_staff=False).annotate(
            enrollment_count=Count('enrollments'),
            total_spent=Sum('payments__amount', filter=Q(payments__status='completed'))
        )
        
        for user in users:
            writer.writerow([
                user.id,
                user.username,
                user.email,
                user.first_name,
                user.last_name,
                user.enrollment_count,
                user.total_spent or 0,
                user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
            ])
    
    return response
