from django.core.management.base import BaseCommand
from ...models import Discount, Purchase, Product

class Command(BaseCommand):
    help = 'Clear all discount-related data from the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of all discount-related data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                'This will reset all discount-related data. Run with --confirm to proceed.'
            )
            return

        # Count records before deletion
        discount_count = Discount._default_manager.count()
        product_count = Product._default_manager.count()
        purchase_count = Purchase._default_manager.filter(mrp__isnull=False).exclude(mrp=0).count()
        
        # Reset sale_rate to match mrp for all purchases with MRP
        purchases_updated = 0
        for purchase in Purchase._default_manager.filter(mrp__isnull=False):
            if purchase.mrp and purchase.mrp > 0:
                purchase.sale_rate = float(purchase.mrp)
                purchase.save()
                purchases_updated += 1
        
        # Delete all discounts
        Discount._default_manager.all().delete()
        
        self.stdout.write(
            f'Successfully reset {purchases_updated} purchases and deleted {discount_count} discounts'
        )