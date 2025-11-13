"""
Advanced Django Views for the AI Voice Assistant
"""
import json
import logging
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Avg
from django.core.paginator import Paginator

# Import our AI modules
from .ai_assistant import AdvancedVoiceAssistant
from .ml.intent_classifier import IntentClassifier
from .nlp.advanced_nlp import AdvancedNLPProcessor
from .analytics.data_analytics import VoiceAssistantAnalytics

# Import Django models
from voice_app.models import VoiceCommand, UserProfile, SystemLog

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize shared AI components
intent_classifier = IntentClassifier()
nlp_processor = AdvancedNLPProcessor()
analytics_engine = VoiceAssistantAnalytics()

# Train the intent classifier (in production, you'd load a pre-trained model)
try:
    intent_classifier.train()
    logger.info("Intent classifier trained successfully")
except Exception as e:
    logger.error(f"Failed to train intent classifier: {e}")


class AdvancedIndexView(View):
    """Serve the advanced main page with analytics dashboard."""
    
    def get(self, request):
        # Get basic statistics for the dashboard
        stats = {
            "total_users": User.objects.count(),
            "total_commands": VoiceCommand.objects.count(),
            "total_logs": SystemLog.objects.count(),
            "recent_commands": VoiceCommand.objects.select_related('user').order_by('-created_at')[:5]
        }
        
        return render(request, 'advanced_index.html', {'stats': stats})


class AdvancedLoginView(View):
    """Handle user login with enhanced security."""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('advanced_index')
        return render(request, 'login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            # Log the login event
            SystemLog.objects.create(
                level='INFO',
                message=f'User {user.username} logged in',
                user=user
            )
            return redirect('advanced_index')
        else:
            messages.error(request, 'Invalid username or password.')
            SystemLog.objects.create(
                level='WARNING',
                message=f'Failed login attempt for username: {username}'
            )
            return render(request, 'login.html')


class AdvancedLogoutView(View):
    """Handle user logout."""
    
    def post(self, request):
        username = request.user.username if request.user.is_authenticated else 'Anonymous'
        logout(request)
        SystemLog.objects.create(
            level='INFO',
            message=f'User {username} logged out'
        )
        return redirect('advanced_index')


class AdvancedRegisterView(View):
    """Handle user registration."""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('advanced_index')
        return render(request, 'register.html')
    
    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validate input
        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'register.html')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'register.html')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Log the registration event
        SystemLog.objects.create(
            level='INFO',
            message=f'New user registered: {user.username}',
            user=user
        )
        
        messages.success(request, 'Account created successfully. Please log in.')
        return redirect('login')


@method_decorator(csrf_exempt, name='dispatch')
class AdvancedProcessAudioView(View):
    """Process audio data with advanced AI capabilities."""
    
    def post(self, request):
        try:
            # Get audio data from request
            data = json.loads(request.body)
            audio_data = data.get('audio')
            
            if not audio_data:
                return JsonResponse({'error': 'No audio data received'}, status=400)
            
            # Initialize advanced voice assistant
            assistant = AdvancedVoiceAssistant(user=request.user if request.user.is_authenticated else None)
            
            # Simulate speech recognition (in a real app, you'd process actual audio)
            recognized_text = "what time is it"  # This would be the actual recognized text
            
            # Process the command with advanced AI
            response_text = assistant.generate_response(recognized_text)
            
            # Log the interaction
            if request.user.is_authenticated:
                SystemLog.objects.create(
                    level='INFO',
                    message=f'Audio command processed: {recognized_text}',
                    user=request.user
                )
            
            # In a real implementation, you would convert response_text to speech
            # and return the audio data
            
            return JsonResponse({
                'success': True,
                'recognized_text': recognized_text,
                'response_text': response_text,
                'audio_response': ''  # This would be base64 encoded audio data
            })
        
        except Exception as e:
            error_msg = f"Error processing audio: {str(e)}"
            logger.error(error_msg)
            SystemLog.objects.create(
                level='ERROR',
                message=error_msg,
                user=request.user if request.user.is_authenticated else None
            )
            return JsonResponse({'error': error_msg}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class AdvancedProcessTextView(View):
    """Process text command with advanced AI capabilities."""
    
    def post(self, request):
        try:
            # Get text command from request
            data = json.loads(request.body)
            command = data.get('command')
            
            if not command:
                return JsonResponse({'error': 'No command received'}, status=400)
            
            # Initialize advanced voice assistant
            assistant = AdvancedVoiceAssistant(user=request.user if request.user.is_authenticated else None)
            
            # Process the command with advanced AI
            response_text = assistant.generate_response(command)
            
            # Log the interaction
            if request.user.is_authenticated:
                SystemLog.objects.create(
                    level='INFO',
                    message=f'Text command processed: {command}',
                    user=request.user
                )
            
            return JsonResponse({
                'success': True,
                'response_text': response_text,
                'intent_analysis': intent_classifier.predict(command),
                'nlp_analysis': nlp_processor.process_text(command) if nlp_processor.nlp else {}
            })
        
        except Exception as e:
            error_msg = f"Error processing text: {str(e)}"
            logger.error(error_msg)
            SystemLog.objects.create(
                level='ERROR',
                message=error_msg,
                user=request.user if request.user.is_authenticated else None
            )
            return JsonResponse({'error': error_msg}, status=500)


class AdvancedAnalyticsView(View):
    """Display advanced analytics dashboard."""
    
    @method_decorator(login_required)
    def get(self, request):
        # Load data from database
        analytics_engine.load_data_from_database()
        
        # Generate analytics report
        report = analytics_engine.generate_comprehensive_report()
        
        # Get additional statistics
        command_stats = VoiceCommand.objects.aggregate(
            total_commands=Count('id'),
            avg_processing_time=Avg('processing_time')
        )
        
        user_stats = User.objects.aggregate(
            total_users=Count('id'),
            new_users_today=Count('id', filter=Count('date_joined__date', timezone.now().date()))
        )
        
        # Get recent commands for display
        recent_commands = VoiceCommand.objects.select_related('user').order_by('-created_at')[:10]
        
        context = {
            'report': report,
            'command_stats': command_stats,
            'user_stats': user_stats,
            'recent_commands': recent_commands
        }
        
        return render(request, 'analytics_dashboard.html', context)


class AdvancedCommandHistoryView(View):
    """Display command history with filtering and pagination."""
    
    @method_decorator(login_required)
    def get(self, request):
        # Get filter parameters
        intent_filter = request.GET.get('intent', '')
        user_filter = request.GET.get('user', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        # Build query
        commands = VoiceCommand.objects.select_related('user').order_by('-created_at')
        
        if intent_filter:
            commands = commands.filter(intent=intent_filter)
        
        if user_filter:
            commands = commands.filter(user__username__icontains=user_filter)
        
        if date_from:
            commands = commands.filter(created_at__gte=date_from)
        
        if date_to:
            commands = commands.filter(created_at__lte=date_to)
        
        # Paginate results
        paginator = Paginator(commands, 20)  # Show 20 commands per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get unique intents for filter dropdown
        intents = VoiceCommand.objects.values_list('intent', flat=True).distinct()
        
        context = {
            'page_obj': page_obj,
            'intents': intents,
            'intent_filter': intent_filter,
            'user_filter': user_filter,
            'date_from': date_from,
            'date_to': date_to
        }
        
        return render(request, 'command_history.html', context)


class AdvancedUserProfileView(View):
    """Manage user profile and preferences."""
    
    @method_decorator(login_required)
    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            # Create profile if it doesn't exist
            profile = UserProfile.objects.create(user=request.user)
        
        return render(request, 'user_profile.html', {'profile': profile})
    
    @method_decorator(login_required)
    def post(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            
            # Update profile fields
            profile.language = request.POST.get('language', profile.language)
            profile.voice_speed = int(request.POST.get('voice_speed', profile.voice_speed))
            profile.voice_volume = float(request.POST.get('voice_volume', profile.voice_volume))
            profile.updated_at = timezone.now()
            profile.save()
            
            messages.success(request, 'Profile updated successfully.')
            SystemLog.objects.create(
                level='INFO',
                message=f'User {request.user.username} updated profile',
                user=request.user
            )
            
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
            SystemLog.objects.create(
                level='ERROR',
                message=f'Profile update failed for {request.user.username}: {str(e)}',
                user=request.user
            )
        
        return redirect('user_profile')


class AdvancedSystemLogsView(View):
    """Display system logs with filtering."""
    
    @method_decorator(login_required)
    def get(self, request):
        # Check if user is staff/admin
        if not request.user.is_staff:
            messages.error(request, 'Access denied.')
            return redirect('advanced_index')
        
        # Get filter parameters
        level_filter = request.GET.get('level', '')
        user_filter = request.GET.get('user', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        # Build query
        logs = SystemLog.objects.select_related('user').order_by('-timestamp')
        
        if level_filter:
            logs = logs.filter(level=level_filter)
        
        if user_filter:
            logs = logs.filter(user__username__icontains=user_filter)
        
        if date_from:
            logs = logs.filter(timestamp__gte=date_from)
        
        if date_to:
            logs = logs.filter(timestamp__lte=date_to)
        
        # Paginate results
        paginator = Paginator(logs, 50)  # Show 50 logs per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Get unique levels for filter dropdown
        levels = SystemLog.objects.values_list('level', flat=True).distinct()
        
        context = {
            'page_obj': page_obj,
            'levels': levels,
            'level_filter': level_filter,
            'user_filter': user_filter,
            'date_from': date_from,
            'date_to': date_to
        }
        
        return render(request, 'system_logs.html', context)