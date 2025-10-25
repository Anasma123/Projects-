from django.db import models
from accounts.models import User
from gallery.models import Design
from booking.models import Booking, Payment

class Feedback(models.Model):
    EVENT_TYPE_CHOICES = [
        ('wedding', 'Wedding'),
        ('party', 'Party'),
        ('festival', 'Festival'),
        ('other', 'Other'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, null=True, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='wedding')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    
    def __str__(self):
        if self.booking:
            return f"Feedback for Booking #{self.booking.id} - {self.subject}"
        return f"Feedback from {self.customer.username} - {self.subject}"

# Create your models here.