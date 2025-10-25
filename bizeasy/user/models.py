
# Models module for the Bizeasy application.
# Defines all data structures and database relationships.


# Standard library imports
from decimal import Decimal, ROUND_HALF_UP
from random import random

# Django imports
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


# ==============================================================================
# User Management Models
# ==============================================================================

class CustomUser(AbstractUser):
    """Custom user model with role-based access control."""
    
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('staff', 'Staff'),
        ('owner', 'Owner'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='staff')
    
    # Additional fields for staff members
    full_name = models.CharField(max_length=150, blank=True, null=True)
    session_number = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    # Fields for tracking staff activity
    last_login_time = models.DateTimeField(blank=True, null=True)
    work_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def is_admin(self):
        return self.role == 'admin'

    def is_staff_user(self):  # to avoid conflict with Django's `is_staff` boolean
        return self.role == 'staff'

    def is_owner(self):
        return self.role == 'owner'

    def __str__(self):
        return f"{self.username} ({self.role})"


# ==============================================================================
# Category Management Models
# ==============================================================================

class Category(models.Model):
    """Model representing a product category."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def clean(self):
        """Validate model fields before saving."""
        from django.db.models import Q
        # Check for case-insensitive duplicate names
        if self.name:
            name_str = str(self.name).strip()
            # Exclude the current instance when editing
            existing_categories = Category._default_manager.filter(
                name__iexact=name_str
            )
            if self.pk:
                existing_categories = existing_categories.exclude(pk=self.pk)
            
            if existing_categories.exists():
                raise ValidationError(f"A category with the name '{name_str}' already exists (case-insensitive).")
    
    def save(self, *args, **kwargs):
        # Run validation
        self.clean()
        # If description is empty, set default description
        if not self.description:
            self.description = f"All items of {self.name} company"
        super().save(*args, **kwargs)


class SubCategory(models.Model):
    """Model representing a product subcategory."""
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        # Removed unique_together constraint to allow case-insensitive validation at application level
        pass

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    def clean(self):
        """Validate model fields before saving."""
        from django.db.models import Q
        # Check for case-insensitive duplicate names within the same category
        if self.name:
            name_str = str(self.name).strip()
            # Exclude the current instance when editing
            existing_subcategories = SubCategory._default_manager.filter(
                category=self.category,
                name__iexact=name_str
            )
            if self.pk:
                existing_subcategories = existing_subcategories.exclude(pk=self.pk)
            
            if existing_subcategories.exists():
                raise ValidationError(f"A subcategory with the name '{name_str}' already exists in this category (case-insensitive).")
        
    def save(self, *args, **kwargs):
        # Run validation
        self.clean()
        # Always update description to match current category and name
        self.description = f"{self.category.name} {self.name} items"
        # Convert name to title case for consistency
        if self.name:
            self.name = str(self.name).strip().title()
        super().save(*args, **kwargs)


# ==============================================================================
# Purchase Management Models
# ==============================================================================

class Purchase(models.Model):
    """Model representing a product purchase."""
    
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
    expire_date = models.DateField(blank=True, null=True) 
    is_deleted = models.BooleanField(default=False)  # Soft delete flag

    def __str__(self):
        return str(f"{self.product_name} - {self.date}")
    
    def clean(self):
        """Validate model fields before saving."""
        # Validate that product_name is not empty
        if not self.product_name or not str(self.product_name).strip():
            raise ValidationError("Product name is required.")
        
        # Validate that product_name is at least 2 characters
        if len(str(self.product_name).strip()) < 2:
            raise ValidationError("Product name must be at least 2 characters long.")
        
        # Validate quantity
        if self.quantity is None or self.quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        
        # Validate product_rate
        if self.product_rate is None or self.product_rate < 0:
            raise ValidationError("Product rate cannot be negative.")
        
        # Validate mrp
        if self.mrp is None or self.mrp < 0:
            raise ValidationError("MRP cannot be negative.")
        
        # Validate that MRP is not less than product rate
        if self.mrp is not None and self.product_rate is not None and self.mrp < self.product_rate:
            raise ValidationError("MRP cannot be less than the product rate.")
        
        # Validate sale_rate if provided
        if self.sale_rate is not None:
            if self.sale_rate < 0:
                raise ValidationError("Sale rate cannot be negative.")
            
            # Validate that sale rate is not greater than MRP
            if self.mrp is not None and self.sale_rate > self.mrp:
                raise ValidationError("Sale rate cannot be greater than MRP.")
            
            # Validate that sale rate is not less than product rate
            if self.sale_rate < self.product_rate:
                raise ValidationError("Sale rate cannot be less than the product rate.")
        
        # Validate date
        if not self.date:
            raise ValidationError("Date is required.")
        
        # Validate expire_date if provided
        if self.expire_date and self.date and self.expire_date < self.date:
            raise ValidationError("Expire date cannot be before the purchase date.")
    
    def save(self, *args, **kwargs):
        """Override save method to include validation and auto-calculate total_rate."""
        # Run validation
        self.clean()
        
        # Auto-calculate total_rate if not provided or if quantity/product_rate changed
        if self.quantity is not None and self.product_rate is not None:
            self.total_rate = self.quantity * self.product_rate
        
        # If notes is empty, set default description
        if not self.notes:
            category_name = self.category.name if self.category else "Unknown Category"
            subcategory_name = self.subcategory.name if self.subcategory else "Unknown Subcategory"
            self.notes = f"Purchase of {self.product_name} in {category_name} - {subcategory_name}"
        
        # Call the parent save method
        super().save(*args, **kwargs)
    
    def delete(self, using=None, keep_parents=False):
        """Soft delete - mark as deleted instead of actual deletion"""
        self.is_deleted = True
        self.save()  # Use save() instead of self.save() to run validation
        # Return a tuple to match the signature of the parent method
        return (1, {self._meta.label: 1})
        
    def hard_delete(self):
        """Actually delete from database"""
        return super().delete()
        
    def alive(self):
        """Return only non-deleted objects"""
        return Purchase.objects.filter(is_deleted=False)
        
    def dead(self):
        """Return only deleted objects"""
        return Purchase.objects.filter(is_deleted=True)

    def get_active_discount(self):
        """Get the active discount for this purchase."""
        # First get the Product associated with this Purchase
        try:
            product = Product.objects.get(purchase=self)
        except Exception:
            return None
            
        # Then get the active discount for that Product
        today = timezone.now().date()
        try:
            discount = Discount._default_manager.filter(
                product=product,
                start_date__lte=today,
                end_date__gte=today
            ).first()
            return discount
        except Exception:
            return None

    def get_final_price(self):
        """Get the final price after applying active discount."""
        # First check if there's an active discount
        discount = self.get_active_discount()
        
        if discount and self.mrp:
            # Calculate discounted price
            discount_amount = (self.mrp * discount.discount_percent) / 100
            final_price = self.mrp - discount_amount
            return final_price
        
        # If no active discount, return MRP or sale_rate if set
        if self.sale_rate is not None:
            return self.sale_rate
        return self.mrp

    def is_discount_active(self):
        """Check if there's an active discount for this purchase."""
        return self.get_active_discount() is not None

    def get_discount_info(self):
        """Get discount information for this purchase."""
        discount = self.get_active_discount()
        if discount:
            return {
                'percent': discount.discount_percent,
                'start_date': discount.start_date,
                'end_date': discount.end_date,
                'is_active': True
            }
        return {
            'percent': 0,
            'start_date': None,
            'end_date': None,
            'is_active': False
        }


# ==============================================================================
# Product Management Models
# ==============================================================================

class Product(models.Model):
    """Model representing a product."""
    
    final_price = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=200)
    purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, blank=True, null=True)
    mrp = models.DecimalField(max_digits=10, decimal_places=2)  # Max Retail Price
    purchase_rate = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    stock_quantity = models.PositiveIntegerField(default=0)
    date_added = models.DateTimeField(default=timezone.now)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        sub = f" ({self.subcategory.name})" if self.subcategory else ""
        return f"{self.name}{sub}"

    def get_latest_selling_price(self):
        # Type hint to help linter understand the relationship
        # sellingproduct_set is created by the ForeignKey in SellingProduct
        latest = self.sellingproduct_set.order_by('-date_added').first()  # type: ignore
        if latest and latest.selling_price is not None:
            return latest.selling_price
        return self.selling_price

    def get_active_discount(self):
        today = timezone.now().date()
        return Discount._default_manager.filter(
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

    def get_discount_info(self):
        """Get discount information for this product."""
        discount = self.get_active_discount()
        if discount:
            return {
                'percent': discount.discount_percent,
                'start_date': discount.start_date,
                'end_date': discount.end_date,
                'is_active': True
            }
        return {
            'percent': 0,
            'start_date': None,
            'end_date': None,
            'is_active': False
        }


class SellingProduct(models.Model):
    """Model representing a product's selling price history."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.product.name} - ₹{self.selling_price}"


class Discount(models.Model):
    """Model representing a product discount."""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('rejected', 'Rejected'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    discount_percent = models.PositiveIntegerField()  # 0 to 100
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def is_active(self):
        today = timezone.now().date()
        return self.status == 'active' and self.start_date <= today <= self.end_date

    def is_expired(self):
        """Check if the discount has expired."""
        today = timezone.now().date()
        return today > self.end_date

    def discounted_price(self):
        selling = self.product.get_latest_selling_price()
        if selling is None:
            return None
        try:
            discount_amount = (Decimal(str(self.discount_percent)) / Decimal('100.00')) * Decimal(str(selling))
            final = Decimal(str(selling)) - Decimal(str(discount_amount))
            return final.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except Exception:
            return None

    @classmethod
    def remove_expired_discounts(cls):
        """Remove all expired discounts from the database."""
        today = timezone.now().date()
        expired_discounts = cls._default_manager.filter(end_date__lt=today)
        count = expired_discounts.count()
        if count > 0:
            expired_discounts.delete()
        return count

    def __str__(self):
        return f"{self.product.name} - {self.discount_percent}%"


# ==============================================================================
# Billing/Invoice Models
# ==============================================================================

class Invoice(models.Model):
    """Model representing an invoice."""
    
    bill_number = models.CharField(max_length=50, unique=True)
    date = models.DateField(default=timezone.now)
    customer_name = models.CharField(max_length=200)
    customer_phone = models.CharField(max_length=30, blank=True, null=True)
    customer_address = models.TextField(blank=True, null=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))  # overall discount if any
    # gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    # gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    roundoff = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    created_by = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.bill_number} - {self.customer_name} ({self.date})"

    def calculate_totals(self):
        # helper to recalc based on items
        # Type hint to help linter understand the relationship
        # items is created by the related_name in InvoiceItem
        items = self.items.all()  # type: ignore
        subtotal = sum((it.total for it in items), Decimal('0.00'))
        # gst_amount = (subtotal * (self.gst_percent or Decimal('0.00'))) / Decimal('100.00')
        total = subtotal - (self.discount_amount or Decimal('0.00')) - (self.roundoff or Decimal('0.00'))
        # quantize to 2 decimals
        subtotal = subtotal.quantize(Decimal('0.01'))
        # gst_amount = gst_amount.quantize(Decimal('0.01'))
        total = total.quantize(Decimal('0.01'))
        self.subtotal = subtotal
        # self.gst_amount = gst_amount
        self.total = total
        return

class InvoiceItem(models.Model):
    """Model representing an invoice item."""
    
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    purchase = models.ForeignKey('Purchase', on_delete=models.PROTECT)  # 👈 instead of Product
    quantity = models.PositiveIntegerField(default=1)
    rate = models.DecimalField(max_digits=12, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def calculate_line(self):
        qty = Decimal(self.quantity)
        rate = Decimal(self.rate)
        if self.discount_percent:
            disc_amt = (rate * qty) * (Decimal(self.discount_percent) / Decimal('100.00'))
        else:
            disc_amt = Decimal('0.00')
        self.discount_amount = disc_amt.quantize(Decimal('0.01'))
        line_total = (rate * qty) - self.discount_amount
        self.discount_amount = disc_amt.quantize(Decimal('0.01'))
        self.total = line_total.quantize(Decimal('0.01'))
        return