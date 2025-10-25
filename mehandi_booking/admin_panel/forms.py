from django import forms
from .models import Feedback
from booking.models import Booking

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['booking', 'event_type', 'subject', 'rating', 'message']
        widgets = {
            'booking': forms.Select(attrs={'class': 'form-control'}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        customer = kwargs.pop('customer', None)
        super(FeedbackForm, self).__init__(*args, **kwargs)
        if customer:
            # Filter bookings to only show completed bookings for this customer
            self.fields['booking'].queryset = Booking.objects.filter(
                customer=customer,
                status='completed'
            ).order_by('-created_at')  # type: ignore