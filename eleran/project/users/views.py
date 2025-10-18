from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from django.conf import settings
from courses.models import Course, Enrollment, Payment, Module, Lesson, LessonProgress
import uuid


def home(request):
    """Home page view"""
    courses = Course.objects.filter(is_published=True)
    context = {'courses': courses}
    return render(request, 'users/home.html', context)


def user_login(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_staff:
                login(request, user)
                
                # Handle Remember Me functionality
                if not remember_me:
                    request.session.set_expiry(0)  # Session expires on browser close
                else:
                    request.session.set_expiry(1209600)  # 2 weeks
                
                messages.success(request, 'Login successful!')
                return redirect('users:dashboard')
            else:
                messages.error(request, 'Invalid credentials!')
        else:
            messages.error(request, 'Invalid credentials!')
    
    return render(request, 'users/login.html')


def user_register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('users:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        
        if password != password2:
            messages.error(request, 'Passwords do not match!')
            return redirect('users:register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists!')
            return redirect('users:register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return redirect('users:register')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        login(request, user)
        messages.success(request, 'Registration successful!')
        return redirect('users:home')
    
    return render(request, 'users/register.html')


@login_required
def user_logout(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('users:home')


@login_required
def dashboard(request):
    """User dashboard with personalized stats and course recommendations"""
    # Get user's enrolled courses
    enrolled_courses = Enrollment.objects.filter(user=request.user).select_related('course')
    enrolled_count = enrolled_courses.count()
    
    # Get enrolled course IDs
    enrolled_course_ids = enrolled_courses.values_list('course_id', flat=True)
    
    # Get recommended courses (published, not enrolled, popular)
    recommended_courses = Course.objects.filter(
        is_published=True
    ).exclude(
        id__in=enrolled_course_ids
    ).annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-enrollment_count', '-created_at')[:6]
    
    # Get all available courses for browsing
    all_courses = Course.objects.filter(is_published=True).annotate(
        enrollment_count=Count('enrollments')
    ).order_by('-created_at')
    
    context = {
        'enrolled_courses': enrolled_courses,
        'enrolled_count': enrolled_count,
        'recommended_courses': recommended_courses,
        'all_courses': all_courses,
        'user': request.user,
    }
    return render(request, 'users/dashboard.html', context)


def course_list(request):
    """List all published courses"""
    courses = Course.objects.filter(is_published=True)
    context = {'courses': courses}
    return render(request, 'users/course_list.html', context)


def course_detail(request, course_id):
    """View course details with immersive learning environment"""
    course = get_object_or_404(Course, id=course_id, is_published=True)
    modules = course.modules.prefetch_related('lessons').all()
    
    is_enrolled = False
    enrollment = None
    lesson_progress_data = {}
    current_lesson = None
    
    if request.user.is_authenticated:
        try:
            enrollment = Enrollment.objects.get(user=request.user, course=course)
            is_enrolled = True
            
            # Get all lesson progress for this user in this course
            progress_records = LessonProgress.objects.filter(
                user=request.user,
                lesson__module__course=course
            )
            lesson_progress_data = {lp.lesson_id: lp for lp in progress_records}
            
            # Get the first incomplete lesson or the first lesson
            for module in modules:
                for lesson in module.lessons.all():
                    if lesson.id not in lesson_progress_data or not lesson_progress_data[lesson.id].completed:
                        current_lesson = lesson
                        break
                if current_lesson:
                    break
            
            # If all lessons completed, show the first lesson
            if not current_lesson and modules.exists():
                first_module = modules.first()
                if first_module and first_module.lessons.exists():
                    current_lesson = first_module.lessons.first()
            
            # Calculate overall progress
            total_lessons = sum(module.lessons.count() for module in modules)
            completed_lessons = sum(1 for lp in lesson_progress_data.values() if lp.completed)
            
            if total_lessons > 0:
                enrollment.progress = int((completed_lessons / total_lessons) * 100)
                enrollment.save()
        except Enrollment.DoesNotExist:
            pass
    
    context = {
        'course': course,
        'modules': modules,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'lesson_progress': lesson_progress_data,
        'current_lesson': current_lesson,
    }
    
    if is_enrolled:
        return render(request, 'users/course_view.html', context)
    else:
        return render(request, 'users/course_detail.html', context)


@login_required
def enroll_course(request, course_id):
    """Enroll user in a course"""
    course = get_object_or_404(Course, id=course_id)
    
    if course.is_free:
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user,
            course=course
        )
        if created:
            messages.success(request, f'Successfully enrolled in "{course.title}"!')
        else:
            messages.info(request, 'You are already enrolled in this course.')
        return redirect('users:my_courses')
    else:
        # For paid courses, redirect to payment
        return redirect('users:payment', course_id=course.id)


@login_required
def my_courses(request):
    """View user's enrolled courses"""
    enrollments = Enrollment.objects.filter(user=request.user)
    context = {'enrollments': enrollments}
    return render(request, 'users/my_courses.html', context)


@login_required
def payment(request, course_id):
    """Payment page for course with Razorpay integration"""
    course = get_object_or_404(Course, id=course_id)
    
    if request.method == 'POST':
        # Create payment record
        order_id = f"ORDER_{uuid.uuid4().hex[:10].upper()}"
        payment = Payment.objects.create(
            user=request.user,
            course=course,
            amount=course.price,
            order_id=order_id,
            status='pending'
        )
        
        # Check if Razorpay is enabled
        if getattr(settings, 'RAZORPAY_ENABLED', False):
            # In production, verify Razorpay signature here
            # For now, mark as completed
            payment.status = 'completed'
            payment.payment_id = request.POST.get('razorpay_payment_id', f"PAY_{uuid.uuid4().hex[:10].upper()}")
        else:
            # Demo payment - automatically complete
            payment.status = 'completed'
            payment.payment_id = f"PAY_{uuid.uuid4().hex[:10].upper()}"
        
        payment.save()
        
        # Create enrollment
        Enrollment.objects.get_or_create(
            user=request.user,
            course=course
        )
        
        messages.success(request, f'Payment successful! You are now enrolled in "{course.title}"')
        return redirect('users:my_courses')
    
    # GET request - show payment page
    context = {
        'course': course,
        'razorpay_enabled': getattr(settings, 'RAZORPAY_ENABLED', False),
        'razorpay_key_id': getattr(settings, 'RAZORPAY_KEY_ID', ''),
        'order_id': f"ORDER_{uuid.uuid4().hex[:10].upper()}",
    }
    return render(request, 'users/payment.html', context)


@login_required
def mark_lesson_complete(request, lesson_id):
    """Mark a lesson as complete and update progress"""
    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        # Check if user is enrolled in the course
        enrollment = Enrollment.objects.filter(
            user=request.user,
            course=lesson.module.course
        ).first()
        
        if not enrollment:
            return JsonResponse({'success': False, 'error': 'Not enrolled in this course'}, status=403)
        
        # Create or update lesson progress
        progress, created = LessonProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson,
            defaults={'completed': True, 'completed_at': timezone.now()}
        )
        
        if not created and not progress.completed:
            progress.completed = True
            progress.completed_at = timezone.now()
            progress.save()
        
        # Update overall course progress
        total_lessons = Lesson.objects.filter(module__course=enrollment.course).count()
        completed_lessons = LessonProgress.objects.filter(
            user=request.user,
            lesson__module__course=enrollment.course,
            completed=True
        ).count()
        
        if total_lessons > 0:
            enrollment.progress = int((completed_lessons / total_lessons) * 100)
            if enrollment.progress == 100:
                enrollment.completed = True
            enrollment.save()
        
        return JsonResponse({
            'success': True,
            'progress': enrollment.progress,
            'completed_lessons': completed_lessons,
            'total_lessons': total_lessons
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)


@login_required
def view_lesson(request, course_id, lesson_id):
    """View a specific lesson within the course"""
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id)
    
    # Check enrollment
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    
    modules = course.modules.prefetch_related('lessons').all()
    lesson_progress_data = {}
    
    # Get all lesson progress
    progress_records = LessonProgress.objects.filter(
        user=request.user,
        lesson__module__course=course
    )
    lesson_progress_data = {lp.lesson_id: lp for lp in progress_records}
    
    context = {
        'course': course,
        'modules': modules,
        'current_lesson': lesson,
        'enrollment': enrollment,
        'lesson_progress': lesson_progress_data,
        'is_enrolled': True,
    }
    
    return render(request, 'users/course_view.html', context)
