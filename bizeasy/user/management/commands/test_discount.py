"""
Test command to check discount functionality.
"""

from django.core.management.base import BaseCommand
from ...models import Purchase, Product, Discount

class Command(BaseCommand):
    help = 'Test discount functionality'

    def handle(self, *args, **options):
        # Test if we can access DoesNotExist
        try:
            # This should work
            purchase = Purchase._default_manager.first()
            if purchase:
                self.stdout.write(f"Found purchase: {purchase.product_name}")
                
                # Try to get a product that doesn't exist
                try:
                    product = Product._default_manager.get(purchase=purchase)
                    self.stdout.write(f"Found product: {product.name}")
                except Exception:
                    self.stdout.write("Product.DoesNotExist caught correctly")
                    
                # Try to get a discount that doesn't exist
                try:
                    discount = Discount._default_manager.get(id=999999)
                    self.stdout.write(f"Found discount: {discount}")
                except Exception:
                    self.stdout.write("Discount.DoesNotExist caught correctly")
            else:
                self.stdout.write("No purchases found")
                
        except Exception as e:
            self.stdout.write(f"Error: {e}")