"""
Management command to run discount status updates periodically.
This command can be scheduled to run at regular intervals.
"""

import time
import logging
from django.core.management.base import BaseCommand
from django.core.management import call_command

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run discount status updates periodically'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=3600,  # 1 hour default
            help='Interval in seconds between updates (default: 3600 seconds/1 hour)'
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run once and exit instead of running continuously'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        once = options['once']
        
        if once:
            self.stdout.write('Running discount status update once...')
            try:
                call_command('update_discount_status')
                self.stdout.write(
                    self.style.SUCCESS('Discount status update completed successfully')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error running discount status update: {str(e)}')
                )
            return
        
        self.stdout.write(f'Starting periodic discount status updates every {interval} seconds...')
        self.stdout.write('Press Ctrl+C to stop')
        
        while True:
            try:
                self.stdout.write('Running discount status update...')
                call_command('update_discount_status')
                self.stdout.write(
                    self.style.SUCCESS(f'Discount status update completed. Next run in {interval} seconds.')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error running discount status update: {str(e)}')
                )
            
            # Wait for the specified interval
            time.sleep(interval)