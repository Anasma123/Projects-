import json
import base64
import datetime
import random
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.decorators import method_decorator


def get_response(command):
    """
    Process voice commands and generate responses.
    """
    command = command.lower()
    
    # Time-related commands
    if "time" in command or "date" in command:
        now = datetime.datetime.now()
        return f"The current time is {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}"
    
    # Weather-related commands (simulated)
    elif "weather" in command:
        # In a real app, you would call a weather API
        weather_data = {
            "London": "15°C, Partly Cloudy",
            "New York": "18°C, Sunny",
            "Tokyo": "22°C, Clear",
            "Paris": "16°C, Overcast",
            "Sydney": "25°C, Sunny"
        }
        
        # Extract city if mentioned
        for city in weather_data.keys():
            if city.lower() in command:
                return f"The current weather in {city} is {weather_data[city]}"
        
        # Default to London
        return f"The current weather in London is {weather_data['London']}"
    
    # News-related commands (simulated)
    elif "news" in command or "headlines" in command:
        headlines = [
            "Scientists discover new species in deep ocean",
            "Stock markets reach all-time high",
            "New breakthrough in renewable energy technology",
            "International summit addresses climate change concerns",
            "Tech company announces revolutionary new product"
        ]
        
        selected_headlines = random.sample(headlines, min(3, len(headlines)))
        news_str = "Here are the latest headlines: "
        for i, headline in enumerate(selected_headlines, 1):
            news_str += f"{i}. {headline}. "
        
        return news_str
    
    # Reminder-related commands (simulated)
    elif "remind" in command or "reminder" in command:
        return "Reminder set successfully. I'll remind you in 1 minute."
    
    # Help command
    elif "help" in command:
        return ("I can help you with the following tasks: "
                "Tell you the time and date, check the weather, read the news, "
                "and set reminders. Just say what you need!")
    
    # Exit command
    elif "exit" in command or "quit" in command or "goodbye" in command:
        return "Goodbye! Have a great day!"
    
    # Default response
    else:
        responses = [
            "I'm sorry, I didn't understand that. Can you please repeat?",
            "I'm not sure what you mean. Try asking for the time, weather, news, or to set a reminder.",
            "I didn't catch that. Say 'help' to hear what I can do."
        ]
        return random.choice(responses)


class IndexView(View):
    """Serve the main page."""
    def get(self, request):
        return render(request, 'index.html')


class WebInterfaceView(View):
    """Serve the basic web interface."""
    def get(self, request):
        return render(request, 'web_interface.html')


class AdvancedWebInterfaceView(View):
    """Serve the advanced web interface."""
    def get(self, request):
        return render(request, 'advanced_web_interface.html')


class WebSocketVoiceInterfaceView(View):
    """Serve the WebSocket voice interface."""
    def get(self, request):
        return render(request, 'websocket_voice_interface.html')


class ProcessAudioView(View):
    """Process audio data sent from the client."""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            # Get audio data from request
            data = json.loads(request.body)
            audio_data = data.get('audio')
            
            if not audio_data:
                return JsonResponse({'error': 'No audio data received'}, status=400)
            
            # Decode base64 audio data
            # Note: In a real implementation, you would process the actual audio
            # For this demo, we'll simulate recognition
            
            # Simulate speech recognition
            recognized_text = "what time is it"  # This would be the actual recognized text
            
            # Process the command
            response_text = get_response(recognized_text)
            
            # In a real implementation, you would convert response_text to speech
            # and return the audio data
            
            return JsonResponse({
                'success': True,
                'recognized_text': recognized_text,
                'response_text': response_text,
                'audio_response': ''  # This would be base64 encoded audio data
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class ProcessTextView(View):
    """Process text command sent from the client."""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        try:
            # Get text command from request
            data = json.loads(request.body)
            command = data.get('command')
            
            if not command:
                return JsonResponse({'error': 'No command received'}, status=400)
            
            # Process the command
            response_text = get_response(command)
            
            return JsonResponse({
                'success': True,
                'response_text': response_text
            })
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class LoginView(View):
    """Handle user login."""
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
        return render(request, 'login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'login.html')


class LogoutView(View):
    """Handle user logout."""
    def post(self, request):
        logout(request)
        return redirect('index')


class RegisterView(View):
    """Handle user registration."""
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('index')
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
        from .models import UserProfile
        UserProfile.objects.create(user=user)
        
        messages.success(request, 'Account created successfully. Please log in.')
        return redirect('login')


class WebSocketVoiceInterfaceView(View):
    """Serve the WebSocket voice interface."""
    def get(self, request):
        return render(request, 'websocket_voice_interface.html')
