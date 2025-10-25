import logging
from django.core.management.base import BaseCommand
from user.models import Discount

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Remove expired discounts automatically'

    def handle(self, *args, **options):
        try:
            # Use the class method to remove expired discounts
            removed_count = Discount.remove_expired_discounts()
            
            if removed_count > 0:
                message = f'Successfully removed {removed_count} expired discounts'
                self.stdout.write(message)
                logger.info(message)
            else:
                message = 'No expired discounts found'
                self.stdout.write(message)
                logger.info(message)
                
        except Exception as e:
            error_message = f'Error removing expired discounts: {str(e)}'
            self.stdout.write(error_message)
            logger.error(error_message)