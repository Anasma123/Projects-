from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from user.models import Category, SubCategory, Purchase, Product, SellingProduct, Discount, Invoice, InvoiceItem

class Command(BaseCommand):
    help = 'Clear all data from the database while preserving table structure'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm that you want to delete all data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.ERROR('This command will delete all data from your database. '
                               'If you are sure, please run with --confirm')
            )
            return

        # Models to clear (in proper order to avoid foreign key issues)
        models_to_clear = [
            (InvoiceItem, 'InvoiceItem'),
            (Invoice, 'Invoice'),
            (Discount, 'Discount'),
            (SellingProduct, 'SellingProduct'),
            (Product, 'Product'),
            (Purchase, 'Purchase'),
            (SubCategory, 'SubCategory'),
            (Category, 'Category'),
            (get_user_model(), 'CustomUser'),
        ]
        
        cleared_count = 0
        
        # Clear each model
        for model, model_name in models_to_clear:
            try:
                count = model.objects.all().delete()
                self.stdout.write(
                    self.style.SUCCESS(f'Cleared {count[0] if count else 0} records from {model_name}')
                )
                cleared_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error clearing {model_name}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully cleared data from {cleared_count} models')
        )