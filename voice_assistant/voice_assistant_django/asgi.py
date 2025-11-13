"""
ASGI config for voice_assistant_django project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voice_assistant_django.settings')

django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter
from voice_assistant_django.routing import application as voice_application

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": voice_application,
})
