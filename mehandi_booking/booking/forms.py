from django import forms
from .models import Booking, Payment, TimeSlot
from gallery.models import Category, SubCategory, Design

class BookingForm(forms.ModelForm):
    time_slot = forms.ModelChoiceField(
        queryset=TimeSlot.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    
    payment_option = forms.ChoiceField(
        choices=Booking.PAYMENT_OPTIONS,
        widget=forms.RadioSelect,
        required=True
    )
    
    class Meta:
        model = Booking
        fields = ['time_slot', 'booking_date', 'payment_option']

class CustomBookingForm(forms.ModelForm):
    CATEGORY_CHOICES = [('', 'Select Category')] + list(Category.objects.values_list('id', 'name'))
    
    category = forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_category'}),
        required=False
    )
    
    subcategory = forms.ModelChoiceField(
        queryset=SubCategory.objects.none(),  # Initially empty
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_subcategory'}),
        required=False
    )
    
    time_slot = forms.ModelChoiceField(
        queryset=TimeSlot.objects.filter(is_active=True),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    booking_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    
    payment_option = forms.ChoiceField(
        choices=Booking.PAYMENT_OPTIONS,
        widget=forms.RadioSelect,
        required=True
    )
    
    class Meta:
        model = Booking
        fields = ['category', 'subcategory', 'time_slot', 'booking_date', 'payment_option', 'phone_number', 'house_name', 'place', 'district', 'state', 'pincode', 'custom_design_image']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'house_name': forms.TextInput(attrs={'class': 'form-control'}),
            'place': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.TextInput(attrs={'class': 'form-control', 'value': 'Kasaragod', 'readonly': True}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'value': 'Kerala', 'readonly': True}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'custom_design_image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(CustomBookingForm, self).__init__(*args, **kwargs)
        # If category is selected, filter subcategories
        if 'category' in self.data:
            category_id = self.data.get('category')
            if category_id:
                try:
                    category_id = int(category_id)
                    # Direct assignment should work - ignoring linter error
                    self.fields['subcategory'].queryset = SubCategory.objects.filter(category_id=category_id).order_by('name')  # type: ignore
                except (ValueError, TypeError):
                    pass  # invalid input from the client; ignore and fallback to empty queryset
        elif self.instance.pk and self.instance.category:
            # Direct assignment should work - ignoring linter error
            self.fields['subcategory'].queryset = SubCategory.objects.filter(category=self.instance.category).order_by('name')  # type: ignore

class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['start_time', 'end_time', 'description', 'is_active']
        widgets = {
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }