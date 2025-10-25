from django.core.management.base import BaseCommand
from ...models import Discount

class Command(BaseCommand):
    help = 'Clear all discounts from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all discounts',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                'This will delete ALL discounts. Run with --confirm to proceed.'
            )
            return

        # Count discounts before deletion
        count = Discount._default_manager.count()
        
        # Delete all discounts
        Discount._default_manager.all().delete()
        
        self.stdout.write(
            f'Successfully deleted {count} discounts'
        )