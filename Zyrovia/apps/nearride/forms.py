from django import forms
from apps.locations.models import Country, District, Locality, LocationRequest, LocationRequestStatus, State
from .models import CategoryRequestStatus, DriverProfile, RideCategory, RideCategoryRequest, RideChatMessage, RideRequest, RideRating
from .services import get_prioritized_driver_queryset


class DriverChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        display_name = obj.name or (obj.user.full_name if obj.user_id else '') or obj.phone_number
        district_name = obj.district.name if obj.district_id else 'N/A'
        locality_name = obj.locality.name if obj.locality_id else 'N/A'
        status = 'Active' if obj.is_online else 'Offline'
        return f'{display_name} - {obj.get_vehicle_type_display()} - {district_name} - {locality_name} - {status} - {obj.phone_number}'


class DriverProfileForm(forms.ModelForm):
    class Meta:
        model = DriverProfile
        fields = [
            'name',
            'phone_number',
            'vehicle_type',
            'vehicle_number',
            'country',
            'state',
            'district',
            'locality',
            'current_location',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['country'].queryset = Country.objects.order_by('name')
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
        country = cleaned_data.get('country')
        state = cleaned_data.get('state')
        district = cleaned_data.get('district')
        locality = cleaned_data.get('locality')
        if state and country and state.country_id != country.id:
            self.add_error('state', 'Selected state does not belong to the country.')
        if district and state and district.state_id != state.id:
            self.add_error('district', 'Selected district does not belong to the state.')
        if locality and district and locality.district_id != district.id:
            self.add_error('locality', 'Selected locality does not belong to the district.')
        return cleaned_data


class RideRequestForm(forms.ModelForm):
    DRIVER_SCOPE_DISTRICT = 'district'
    DRIVER_SCOPE_ALL = 'all'
    DRIVER_SCOPE_CHOICES = (
        (DRIVER_SCOPE_DISTRICT, 'District Wise'),
        (DRIVER_SCOPE_ALL, 'All Drivers'),
    )

    driver_scope = forms.ChoiceField(choices=DRIVER_SCOPE_CHOICES, initial=DRIVER_SCOPE_DISTRICT)
    driver_profile = DriverChoiceField(queryset=DriverProfile.objects.none(), empty_label='Select Driver')

    class Meta:
        model = RideRequest
        fields = [
            'ride_category',
            'driver_profile',
            'pickup_country',
            'pickup_state',
            'pickup_district',
            'pickup_locality',
            'pickup_location',
            'destination_country',
            'destination_state',
            'destination_district',
            'destination_locality',
            'destination',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pickup_country'].queryset = Country.objects.order_by('name')
        self.fields['destination_country'].queryset = Country.objects.order_by('name')
        self.fields['ride_category'].queryset = RideCategory.objects.filter(is_active=True).order_by('name')
        self.fields['pickup_state'].queryset = State.objects.none()
        self.fields['pickup_district'].queryset = District.objects.none()
        self.fields['pickup_locality'].queryset = Locality.objects.none()
        self.fields['destination_state'].queryset = State.objects.none()
        self.fields['destination_district'].queryset = District.objects.none()
        self.fields['destination_locality'].queryset = Locality.objects.none()

        self._init_pickup_hierarchy()
        self._init_destination_hierarchy()
        self._init_driver_queryset()

    @staticmethod
    def _safe_int(value):
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _init_driver_queryset(self):
        if self.instance and self.instance.pk:
            ride_category_id = self.instance.ride_category_id
            pickup_state_id = self.instance.pickup_state_id
            pickup_district_id = self.instance.pickup_district_id
            pickup_locality_id = self.instance.pickup_locality_id
        else:
            ride_category_id = self._safe_int(self.data.get('ride_category'))
            pickup_state_id = self._safe_int(self.data.get('pickup_state'))
            pickup_district_id = self._safe_int(self.data.get('pickup_district'))
            pickup_locality_id = self._safe_int(self.data.get('pickup_locality'))
        scope = self.data.get('driver_scope') or self.DRIVER_SCOPE_DISTRICT
        district_only = scope == self.DRIVER_SCOPE_DISTRICT

        self.fields['driver_profile'].queryset = get_prioritized_driver_queryset(
            ride_category_id=ride_category_id,
            pickup_state_id=pickup_state_id,
            pickup_district_id=pickup_district_id,
            pickup_locality_id=pickup_locality_id,
            district_only=district_only,
        )

    def _init_pickup_hierarchy(self):
        if self.instance and self.instance.pk:
            if self.instance.pickup_country_id:
                self.fields['pickup_state'].queryset = State.objects.filter(country_id=self.instance.pickup_country_id).order_by('name')
            if self.instance.pickup_state_id:
                self.fields['pickup_district'].queryset = District.objects.filter(state_id=self.instance.pickup_state_id).order_by('name')
            if self.instance.pickup_district_id:
                self.fields['pickup_locality'].queryset = Locality.objects.filter(district_id=self.instance.pickup_district_id).order_by('name')
            return
        country_id = self.data.get('pickup_country')
        state_id = self.data.get('pickup_state')
        district_id = self.data.get('pickup_district')
        if country_id and country_id.isdigit():
            self.fields['pickup_state'].queryset = State.objects.filter(country_id=country_id).order_by('name')
        if state_id and state_id.isdigit():
            self.fields['pickup_district'].queryset = District.objects.filter(state_id=state_id).order_by('name')
        if district_id and district_id.isdigit():
            self.fields['pickup_locality'].queryset = Locality.objects.filter(district_id=district_id).order_by('name')

    def _init_destination_hierarchy(self):
        if self.instance and self.instance.pk:
            if self.instance.destination_country_id:
                self.fields['destination_state'].queryset = State.objects.filter(country_id=self.instance.destination_country_id).order_by('name')
            if self.instance.destination_state_id:
                self.fields['destination_district'].queryset = District.objects.filter(state_id=self.instance.destination_state_id).order_by('name')
            if self.instance.destination_district_id:
                self.fields['destination_locality'].queryset = Locality.objects.filter(district_id=self.instance.destination_district_id).order_by('name')
            return
        country_id = self.data.get('destination_country')
        state_id = self.data.get('destination_state')
        district_id = self.data.get('destination_district')
        if country_id and country_id.isdigit():
            self.fields['destination_state'].queryset = State.objects.filter(country_id=country_id).order_by('name')
        if state_id and state_id.isdigit():
            self.fields['destination_district'].queryset = District.objects.filter(state_id=state_id).order_by('name')
        if district_id and district_id.isdigit():
            self.fields['destination_locality'].queryset = Locality.objects.filter(district_id=district_id).order_by('name')

    def clean(self):
        cleaned_data = super().clean()
        required_fields = [
            'pickup_country',
            'pickup_state',
            'pickup_district',
            'pickup_locality',
            'destination_country',
            'destination_state',
            'destination_district',
            'destination_locality',
        ]
        for field_name in required_fields:
            if not cleaned_data.get(field_name):
                self.add_error(field_name, 'This field is required.')
        if not cleaned_data.get('ride_category'):
            self.add_error('ride_category', 'This field is required.')

        pickup_country = cleaned_data.get('pickup_country')
        pickup_state = cleaned_data.get('pickup_state')
        pickup_district = cleaned_data.get('pickup_district')
        pickup_locality = cleaned_data.get('pickup_locality')
        destination_country = cleaned_data.get('destination_country')
        destination_state = cleaned_data.get('destination_state')
        destination_district = cleaned_data.get('destination_district')
        destination_locality = cleaned_data.get('destination_locality')

        if pickup_state and pickup_country and pickup_state.country_id != pickup_country.id:
            self.add_error('pickup_state', 'Selected pickup state does not belong to the pickup country.')
        if pickup_district and pickup_state and pickup_district.state_id != pickup_state.id:
            self.add_error('pickup_district', 'Selected pickup district does not belong to the pickup state.')
        if pickup_locality and pickup_district and pickup_locality.district_id != pickup_district.id:
            self.add_error('pickup_locality', 'Selected pickup locality does not belong to the pickup district.')

        if destination_state and destination_country and destination_state.country_id != destination_country.id:
            self.add_error('destination_state', 'Selected destination state does not belong to the destination country.')
        if destination_district and destination_state and destination_district.state_id != destination_state.id:
            self.add_error('destination_district', 'Selected destination district does not belong to the destination state.')
        if destination_locality and destination_district and destination_locality.district_id != destination_district.id:
            self.add_error('destination_locality', 'Selected destination locality does not belong to the destination district.')

        ride_category = cleaned_data.get('ride_category')
        driver_profile = cleaned_data.get('driver_profile')
        driver_scope = cleaned_data.get('driver_scope') or self.DRIVER_SCOPE_DISTRICT
        if ride_category and driver_profile:
            valid_driver_exists = get_prioritized_driver_queryset(
                ride_category_id=ride_category.id,
                pickup_state_id=pickup_state.id if pickup_state else None,
                pickup_district_id=pickup_district.id if pickup_district else None,
                pickup_locality_id=pickup_locality.id if pickup_locality else None,
                district_only=driver_scope == self.DRIVER_SCOPE_DISTRICT,
            ).filter(id=driver_profile.id, user_id=driver_profile.user_id).exists()
            if not valid_driver_exists:
                self.add_error('driver_profile', 'Selected driver is invalid for the chosen category/location.')
        return cleaned_data


class RideChatMessageForm(forms.ModelForm):
    class Meta:
        model = RideChatMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Type your message...'}),
        }


class RideRatingForm(forms.ModelForm):
    class Meta:
        model = RideRating
        fields = ['stars']
        widgets = {
            'stars': forms.Select(choices=[(i, f'{i} Star') for i in range(1, 6)]),
        }


class RideCategoryRequestForm(forms.ModelForm):
    class Meta:
        model = RideCategoryRequest
        fields = ['category_name', 'description']

    def clean_category_name(self):
        category_name = self.cleaned_data['category_name'].strip()
        if RideCategory.objects.filter(name__iexact=category_name, is_active=True).exists():
            raise forms.ValidationError('This ride category already exists.')

        if RideCategoryRequest.objects.filter(
            requested_by=self.initial.get('requested_by'),
            status=CategoryRequestStatus.PENDING,
            category_name__iexact=category_name,
        ).exists():
            raise forms.ValidationError('You already have a pending request for this category.')
        return category_name


class LocationRequestForm(forms.ModelForm):
    class Meta:
        model = LocationRequest
        fields = ['country_name', 'state_name', 'district_name', 'locality_name']

    def _clean_name(self, key):
        value = (self.cleaned_data.get(key) or '').strip()
        if not value:
            raise forms.ValidationError('This field is required.')
        return value

    def clean_country_name(self):
        return self._clean_name('country_name')

    def clean_state_name(self):
        return self._clean_name('state_name')

    def clean_district_name(self):
        return self._clean_name('district_name')

    def clean_locality_name(self):
        return self._clean_name('locality_name')

    def clean(self):
        cleaned_data = super().clean()
        requested_by = self.initial.get('requested_by')
        if not requested_by:
            return cleaned_data

        country_name = cleaned_data.get('country_name')
        state_name = cleaned_data.get('state_name')
        district_name = cleaned_data.get('district_name')
        locality_name = cleaned_data.get('locality_name')
        if not all([country_name, state_name, district_name, locality_name]):
            return cleaned_data

        duplicate_exists = LocationRequest.objects.filter(
            requested_by=requested_by,
            status=LocationRequestStatus.PENDING,
            country_name__iexact=country_name,
            state_name__iexact=state_name,
            district_name__iexact=district_name,
            locality_name__iexact=locality_name,
        ).exists()
        if duplicate_exists:
            raise forms.ValidationError('You already have a pending request for this location.')
        return cleaned_data
