"""voice_assistant_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from voice_app.views import IndexView, WebInterfaceView, AdvancedWebInterfaceView, WebSocketVoiceInterfaceView, ProcessAudioView, ProcessTextView, LoginView, LogoutView, RegisterView
from ai_modules.views import AdvancedIndexView, AdvancedLoginView, AdvancedLogoutView, AdvancedRegisterView, AdvancedProcessAudioView, AdvancedProcessTextView, AdvancedAnalyticsView, AdvancedCommandHistoryView, AdvancedUserProfileView, AdvancedSystemLogsView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view(), name='index'),
    path('web_interface.html', WebInterfaceView.as_view(), name='web_interface'),
    path('advanced_web_interface.html', AdvancedWebInterfaceView.as_view(), name='advanced_web_interface'),
    path('websocket_voice_interface.html', WebSocketVoiceInterfaceView.as_view(), name='websocket_voice_interface'),
    path('process_audio/', ProcessAudioView.as_view(), name='process_audio'),
    path('process_text/', ProcessTextView.as_view(), name='process_text'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    
    # Advanced AI views
    path('ai/', AdvancedIndexView.as_view(), name='advanced_index'),
    path('ai/login/', AdvancedLoginView.as_view(), name='advanced_login'),
    path('ai/logout/', AdvancedLogoutView.as_view(), name='advanced_logout'),
    path('ai/register/', AdvancedRegisterView.as_view(), name='advanced_register'),
    path('ai/process_audio/', AdvancedProcessAudioView.as_view(), name='advanced_process_audio'),
    path('ai/process_text/', AdvancedProcessTextView.as_view(), name='advanced_process_text'),
    path('ai/analytics/', AdvancedAnalyticsView.as_view(), name='advanced_analytics'),
    path('ai/history/', AdvancedCommandHistoryView.as_view(), name='command_history'),
    path('ai/profile/', AdvancedUserProfileView.as_view(), name='user_profile'),
    path('ai/logs/', AdvancedSystemLogsView.as_view(), name='system_logs'),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
