from django.db import models
from accounts.models import User
from gallery.models import Design, Category, SubCategory

# Create your models here.

class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_time']
        # Removed unique constraint to allow same time slots on different dates
    
    def __str__(self):
        return f"{self.start_time}-{self.end_time}"
    
    @property
    def display_name(self):
        return f"{self.start_time.strftime('%I:%M %p')} to {self.end_time.strftime('%I:%M %p')}"

class Booking(models.Model):
    PAYMENT_OPTIONS = [
        ('full', 'Full Payment'),
        ('advance', 'Advance Payment (40%)'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    design = models.ForeignKey(Design, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.SET_NULL, null=True, blank=True)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    payment_option = models.CharField(max_length=10, choices=PAYMENT_OPTIONS, default='full')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_completed_at = models.DateTimeField(null=True, blank=True)
    
    # Custom booking fields
    phone_number = models.CharField(max_length=15, blank=True)
    house_name = models.CharField(max_length=100, blank=True)
    place = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=50, default='Kasaragod')
    state = models.CharField(max_length=50, default='Kerala')
    pincode = models.CharField(max_length=10, blank=True)
    custom_design_image = models.ImageField(upload_to='custom_designs/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.design:
            return f"{self.customer.username} - {self.design.name}"
        else:
            return f"{self.customer.username} - Custom Booking"
    
    @property
    def is_custom_booking(self):
        return self.design is None
    
    @property
    def advance_amount(self):
        """Calculate 40% advance amount"""
        return round(float(self.total_amount) * 0.4, 2)
    
    @property
    def amount_to_pay(self):
        """Return the amount to be paid based on payment option"""
        if self.payment_option == 'advance':
            return self.advance_amount
        return float(self.total_amount)

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking'),
        ('paypal', 'PayPal'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    refund_transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment for {self.booking} - {self.status}"