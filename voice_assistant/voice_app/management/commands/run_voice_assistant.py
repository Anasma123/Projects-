import os
from django.core.management.base import BaseCommand
from django.core.management import execute_from_command_line


class Command(BaseCommand):
    help = 'Run the voice assistant Django server'

    def add_arguments(self, parser):
        parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the server on')
        parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')

    def handle(self, *args, **options):
        host = options['host']
        port = options['port']
        
        self.stdout.write(
            self.style.SUCCESS(f'Starting voice assistant server at http://{host}:{port}')
        )
        
        # Set the environment variable to make sure Django uses the correct settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'voice_assistant_django.settings')
        
        # Run the Django development server
        execute_from_command_line(['manage.py', 'runserver', f'{host}:{port}'])