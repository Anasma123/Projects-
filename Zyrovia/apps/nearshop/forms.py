from django import forms
from django.utils import timezone

from apps.locations.models import Country, District, Locality, State
from .models import CategoryRequestStatus, Offer, Product, Shop, ShopCategory, ShopCategoryRequest, ShopChat, ShopRating


class ShopForm(forms.ModelForm):
    class Meta:
        model = Shop
        fields = [
            'shop_name',
            'category',
            'address',
            'country',
            'state',
            'district',
            'locality',
            'location_text',
            'phone_number',
            'description',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].queryset = Country.objects.order_by('name')
        self.fields['category'].queryset = ShopCategory.objects.filter(is_active=True).order_by('name')
        self.fields['state'].queryset = State.objects.none()
        self.fields['district'].queryset = District.objects.none()
        self.fields['locality'].queryset = Locality.objects.none()

        if self.instance and self.instance.pk:
            if self.instance.country_id:
                self.fields['state'].queryset = State.objects.filter(country_id=self.instance.country_id).order_by('name')
            if self.instance.state_id:
                self.fields['district'].queryset = District.objects.filter(state_id=self.instance.state_id).order_by('name')
            if self.instance.district_id:
                self.fields['locality'].queryset = Locality.objects.filter(district_id=self.instance.district_id).order_by('name')
        elif self.data:
            country_id = self.data.get('country')
            state_id = self.data.get('state')
            district_id = self.data.get('district')
            if country_id and country_id.isdigit():
                self.fields['state'].queryset = State.objects.filter(country_id=country_id).order_by('name')
            if state_id and state_id.isdigit():
                self.fields['district'].queryset = District.objects.filter(state_id=state_id).order_by('name')
            if district_id and district_id.isdigit():
                self.fields['locality'].queryset = Locality.objects.filter(district_id=district_id).order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        for field_name in ['country', 'state', 'district', 'locality']:
            if not cleaned_data.get(field_name):
                self.add_error(field_name, 'This field is required.')
        if not cleaned_data.get('category'):
            self.add_error('category', 'This field is required.')
        return cleaned_data


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'category', 'price', 'stock_quantity', 'is_available']


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['title', 'description', 'discount_percent', 'valid_until']
        widgets = {
            'valid_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_valid_until(self):
        value = self.cleaned_data['valid_until']
        if value <= timezone.now():
            raise forms.ValidationError('Offer validity must be in the future.')
        return value


class ShopChatForm(forms.ModelForm):
    class Meta:
        model = ShopChat
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Message the shop owner...'}),
        }


class ShopRatingForm(forms.ModelForm):
    class Meta:
        model = ShopRating
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Star') for i in range(1, 6)]),
            'review_text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional review'}),
        }


class ShopCategoryRequestForm(forms.ModelForm):
    class Meta:
        model = ShopCategoryRequest
        fields = ['category_name', 'description']

    def clean_category_name(self):
        category_name = self.cleaned_data['category_name'].strip()
        if ShopCategory.objects.filter(name__iexact=category_name, is_active=True).exists():
            raise forms.ValidationError('This shop category already exists.')

        if ShopCategoryRequest.objects.filter(
            requested_by=self.initial.get('requested_by'),
            status=CategoryRequestStatus.PENDING,
            category_name__iexact=category_name,
        ).exists():
            raise forms.ValidationError('You already have a pending request for this category.')
        return category_name
