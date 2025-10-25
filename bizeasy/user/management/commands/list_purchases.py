"""
Management command to list purchases.
"""

from django.core.management.base import BaseCommand
from ...models import Purchase

class Command(BaseCommand):
    help = 'List purchases'

    def handle(self, *args, **options):
        purchases = Purchase._default_manager.all()[:5]
        self.stdout.write(f"Total purchases: {purchases.count()}")
        for purchase in purchases:
            self.stdout.write(f"ID: {purchase.id}, Name: {purchase.product_name}")