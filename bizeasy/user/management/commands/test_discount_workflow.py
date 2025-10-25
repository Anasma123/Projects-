"""
Management command to test the complete discount workflow.
Creates sample discounts with different statuses for testing.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from ...models import Discount, Product, Purchase

class Command(BaseCommand):
    help = 'Create sample discounts for testing the workflow'

    def handle(self, *args, **options):
        # Get today's date
        today = timezone.now().date()
        
        # Get some sample products/purchases (you might need to adjust this based on your data)
        purchases = Purchase._default_manager.filter(mrp__isnull=False, mrp__gt=0)[:3]
        
        if not purchases:
            self.stdout.write(
                self.style.WARNING('No purchases with MRP found. Please add some products first.')
            )
            return
        
        created_count = 0
        
        for i, purchase in enumerate(purchases):
            # Try to get or create a product for this purchase
            try:
                product = Product._default_manager.get(purchase=purchase)
            except Product.DoesNotExist:
                # Create a product if it doesn't exist
                product = Product._default_manager.create(
                    name=f"Test Product {i+1}",
                    purchase=purchase,
                    category=purchase.category,
                    subcategory=purchase.subcategory,
                    mrp=purchase.mrp or 100,
                    purchase_rate=purchase.product_rate or 80,
                    selling_price=purchase.mrp or 100,
                    stock_quantity=purchase.quantity or 10,
                    final_price=purchase.mrp or 100
                )
            
            # Create different types of discounts for testing
            if i == 0:
                # Pending discount (future start date)
                start_date = today + timedelta(days=7)
                end_date = today + timedelta(days=30)
                status = 'pending'
                discount_percent = 10
            elif i == 1:
                # Active discount (current)
                start_date = today - timedelta(days=7)
                end_date = today + timedelta(days=7)
                status = 'active'
                discount_percent = 15
            else:
                # Expired discount (past end date)
                start_date = today - timedelta(days=30)
                end_date = today - timedelta(days=7)
                status = 'rejected'
                discount_percent = 20
            
            # Create or update the discount
            discount, created = Discount._default_manager.update_or_create(
                product=product,
                defaults={
                    'discount_percent': discount_percent,
                    'start_date': start_date,
                    'end_date': end_date,
                    'status': status
                }
            )
            
            if created:
                self.stdout.write(
                    f'Created {status} discount for {product.name}: {discount_percent}% '
                    f'({start_date} to {end_date})'
                )
            else:
                self.stdout.write(
                    f'Updated discount for {product.name}: {discount_percent}% '
                    f'({start_date} to {end_date}) - Status: {status}'
                )
            
            created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created/updated {created_count} sample discounts. '
                f'Run "python manage.py update_discount_status" to update statuses.'
            )
        )