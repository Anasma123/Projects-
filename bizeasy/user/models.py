# users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('owner', 'Owner'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')

    def is_admin(self):
        return self.role == 'admin'

    def is_staff_user(self):  # to avoid conflict with Django's `is_staff` boolean
        return self.role == 'staff'

    def is_owner(self):
        return self.role == 'owner'

    def __str__(self):
        return f"{self.username} ({self.role})"

# catagory

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)  # 👈 Add this line

    def __str__(self):
        return self.name
    
# subcategory

class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"


# purchase model

class Purchase(models.Model):
    product_name = models.CharField(max_length=100)  
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, default=1)
    quantity = models.PositiveIntegerField()
    product_rate = models.FloatField()
    total_rate = models.FloatField()  # quantity * product_rate
    date = models.DateField()
    mrp = models.FloatField()
    notes = models.TextField(blank=True, null=True)
    change_price = models.FloatField(blank=True, null=True)  # For edit use
    sale_rate = models.FloatField(blank=True, null=True)  # For sale rate

    def __str__(self):
        return f"{self.product_name} - {self.date}"
    
from django.db import models
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP


class Product(models.Model):
    name = models.CharField(max_length=200)
    purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, blank=True, null=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)  # Max Retail Price
    purchase_rate = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    stock_quantity = models.PositiveIntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        sub = f" ({self.subcategory.name})" if self.subcategory else ""
        return f"{self.name}{sub}"

    def get_latest_selling_price(self):
        latest = self.sellingproduct_set.order_by('-date_added').first()
        if latest and latest.selling_price is not None:
            return latest.selling_price
        return self.selling_price

    def get_active_discount(self):
        today = timezone.now().date()
        return Discount.objects.filter(
            product=self,
            start_date__lte=today,
            end_date__gte=today
        ).order_by('-start_date').first()

    def get_discount_percent(self):
        discount = self.get_active_discount()
        if discount:
            return discount.discount_percent
        return None

    def get_discount_amount(self):
        discount_percent = self.get_discount_percent()
        selling = self.get_latest_selling_price()
        try:
            if discount_percent is not None and selling is not None:
                amount = (Decimal(discount_percent) / Decimal('100.00')) * Decimal(selling)
                # round to 2 decimals
                return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except Exception:
            pass
        return Decimal('0.00')

    def get_final_price(self):
        selling = self.get_latest_selling_price()
        discount_amount = self.get_discount_amount()
        try:
            if selling is None:
                return None
            final = Decimal(selling) - Decimal(discount_amount)
            return final.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except Exception:
            return selling

    def stock_status(self):
        qty = self.stock_quantity
        if qty > 15:
            return 'High'
        elif qty > 5:
            return 'Medium'
        else:
            return 'Low'

    def in_stock(self):
        return self.stock_quantity > 0


class SellingProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.product.name} - ₹{self.selling_price}"


class Discount(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount_percent = models.PositiveIntegerField()  # 0 to 100
    start_date = models.DateField()
    end_date = models.DateField()

    def is_active(self):
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

    def discounted_price(self):
        selling = self.product.get_latest_selling_price()
        if selling is None:
            return None
        try:
            discount_amount = (Decimal(self.discount_percent) / Decimal('100.00')) * Decimal(selling)
            final = Decimal(selling) - discount_amount
            return final.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except Exception:
            return None

    def __str__(self):
        return f"{self.product.name} - {self.discount_percent}%"




# billing model

class Billing(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('final', 'Finalized'),
        ('cancelled', 'Cancelled'),
    ]
    created_at = models.DateTimeField(default=timezone.now)
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    roundoff = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    final_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    def subtotal(self):
        return sum(item.line_total() for item in self.items.all())

    def gst_amount(self):
        if self.gst_percent:
            base = self.subtotal()
            return (base * self.gst_percent / Decimal(100)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return Decimal('0.00')

    def compute_final_amount(self):
        amt = self.subtotal() + self.gst_amount() + self.roundoff
        return amt.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def save(self, *args, **kwargs):
        self.final_amount = self.compute_final_amount()
        super().save(*args, **kwargs)
        # Sync income
        Income.objects.update_or_create(
            billing=self,
            defaults={'amount': self.final_amount, 'recorded_at': timezone.now()}
        )

    def __str__(self):
        return f"Bill #{self.id} - {self.created_at.date()}"

class BillingItem(models.Model):
    billing = models.ForeignKey(Billing, related_name='items', on_delete=models.CASCADE)

    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)

    def line_total(self):
        return (self.product.final_price * self.quantity).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

class Income(models.Model):
    billing = models.OneToOneField(Billing, related_name='income', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    recorded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Income Bill#{self.billing.id}: {self.amount}"