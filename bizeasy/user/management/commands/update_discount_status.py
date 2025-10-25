"""
Management command to update discount status based on dates.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from ...models import Discount, Purchase

class Command(BaseCommand):
    help = 'Update discount status based on start and end dates'

    def handle(self, *args, **options):
        today = timezone.now().date()
        updated_count = 0
        activated_count = 0
        expired_count = 0
        
        # Get all discounts
        discounts = Discount._default_manager.all()
        
        for discount in discounts:
            old_status = discount.status
            
            # Determine status based on dates
            if discount.start_date <= today <= discount.end_date:
                discount.status = 'active'
            elif today < discount.start_date:
                discount.status = 'pending'
            else:
                discount.status = 'rejected'  # Expired
            
            # Save the discount with updated status
            discount.save()
            updated_count += 1
            
            # If discount just became active, update the purchase's sale_rate
            if old_status != 'active' and discount.status == 'active':
                try:
                    purchase = discount.product.purchase
                    if purchase:
                        # Calculate discounted price
                        original_mrp = float(purchase.mrp)
                        discount_amount = original_mrp * (discount.discount_percent / 100)
                        discounted_price = original_mrp - discount_amount
                        
                        # Update the purchase's sale_rate
                        purchase.sale_rate = discounted_price
                        purchase.save()
                        activated_count += 1
                        self.stdout.write(
                            f'Activated discount for {discount.product.name}: {discount.discount_percent}% off'
                        )
                except Exception as e:
                    self.stdout.write(
                        f'Error updating purchase for discount {discount.id}: {str(e)}'
                    )
            
            # If discount just expired, revert the purchase's sale_rate
            if old_status == 'active' and discount.status == 'rejected':
                try:
                    purchase = discount.product.purchase
                    if purchase:
                        # Revert to original MRP
                        purchase.sale_rate = float(purchase.mrp)
                        purchase.save()
                        expired_count += 1
                        self.stdout.write(
                            f'Expired discount for {discount.product.name}, reverted to MRP'
                        )
                except Exception as e:
                    self.stdout.write(
                        f'Error reverting purchase for expired discount {discount.id}: {str(e)}'
                    )
        
        self.stdout.write(
            f'Successfully updated status for {updated_count} discounts. '
            f'Activated {activated_count} discounts. '
            f'Expired {expired_count} discounts.'
        )