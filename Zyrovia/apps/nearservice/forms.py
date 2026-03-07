from django import forms
from django.db.models import Q

from apps.locations.models import Country, District, Locality, State
from .models import (
    CategoryRequestStatus,
    ServiceAreaScope,
    ServiceCategory,
    ServiceCategoryRequest,
    ServiceChat,
    ServiceProvider,
    ServiceRating,
    ServiceRequest,
)


class ServiceCategoryForm(forms.ModelForm):
    class Meta:
        model = ServiceCategory
        fields = ['name', 'description', 'is_active']


class ServiceProviderForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        fields = [
            'category',
            'experience_years',
            'service_area_scope',
            'country',
            'state',
            'district',
            'locality',
            'phone_number',
            'description',
            'is_available',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ServiceCategory.objects.filter(is_active=True)
        self.fields['country'].queryset = Country.objects.all().order_by('name')
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
        scope = cleaned_data.get('service_area_scope')
        if scope == ServiceAreaScope.SPECIFIC:
            for field_name in ['country', 'state', 'district', 'locality']:
                if not cleaned_data.get(field_name):
                    self.add_error(field_name, 'This field is required for given-location scope.')
        else:
            cleaned_data['country'] = None
            cleaned_data['state'] = None
            cleaned_data['district'] = None
            cleaned_data['locality'] = None
        return cleaned_data


class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['category', 'provider', 'problem_description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ServiceCategory.objects.filter(is_active=True)
        self.fields['provider'].queryset = ServiceProvider.objects.filter(
            is_available=True,
            is_active=True,
            is_verified=True,
            category__is_active=True,
        ).select_related('user', 'category', 'country', 'state', 'district', 'locality')

        country_id = kwargs.get('initial', {}).get('country_id') if kwargs.get('initial') else None
        state_id = kwargs.get('initial', {}).get('state_id') if kwargs.get('initial') else None
        district_id = kwargs.get('initial', {}).get('district_id') if kwargs.get('initial') else None
        locality_id = kwargs.get('initial', {}).get('locality_id') if kwargs.get('initial') else None

        if self.data:
            country_id = self.data.get('country_id') or country_id
            state_id = self.data.get('state_id') or state_id
            district_id = self.data.get('district_id') or district_id
            locality_id = self.data.get('locality_id') or locality_id

        if country_id and str(country_id).isdigit():
            self.fields['provider'].queryset = self.fields['provider'].queryset.filter(
                Q(service_area_scope=ServiceAreaScope.ALL) | Q(country_id=country_id)
            )
        if state_id and str(state_id).isdigit():
            self.fields['provider'].queryset = self.fields['provider'].queryset.filter(
                Q(service_area_scope=ServiceAreaScope.ALL) | Q(state_id=state_id)
            )
        if district_id and str(district_id).isdigit():
            self.fields['provider'].queryset = self.fields['provider'].queryset.filter(
                Q(service_area_scope=ServiceAreaScope.ALL) | Q(district_id=district_id)
            )
        if locality_id and str(locality_id).isdigit():
            self.fields['provider'].queryset = self.fields['provider'].queryset.filter(
                Q(service_area_scope=ServiceAreaScope.ALL) | Q(locality_id=locality_id)
            )


class ServiceChatForm(forms.ModelForm):
    class Meta:
        model = ServiceChat
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Type a message...'}),
        }


class ServiceRatingForm(forms.ModelForm):
    class Meta:
        model = ServiceRating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Star') for i in range(1, 6)]),
            'review': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional review'}),
        }


class ServiceCategoryRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceCategoryRequest
        fields = ['category_name', 'description']

    def clean_category_name(self):
        category_name = self.cleaned_data['category_name'].strip()
        if ServiceCategory.objects.filter(name__iexact=category_name).exists():
            raise forms.ValidationError('This service category already exists.')

        if ServiceCategoryRequest.objects.filter(
            requested_by=self.initial.get('requested_by'),
            status=CategoryRequestStatus.PENDING,
            category_name__iexact=category_name,
        ).exists():
            raise forms.ValidationError('You already have a pending request for this category.')
        return category_name
