from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg

from apps.locations.models import Country, District, Locality, State


class ServiceRequestStatus(models.TextChoices):
    REQUESTED = 'requested', 'Requested'
    ACCEPTED = 'accepted', 'Accepted'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class ServiceAreaScope(models.TextChoices):
    SPECIFIC = 'specific', 'Given Location'
    ALL = 'all', 'All Locations'


class ServiceCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CategoryRequestStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class ServiceCategoryRequest(models.Model):
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_category_requests')
    category_name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=CategoryRequestStatus.choices, default=CategoryRequestStatus.PENDING)
    admin_note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.category_name} ({self.status})'


class ServiceProvider(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_provider_profile')
    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, related_name='providers')
    experience_years = models.PositiveIntegerField(default=0)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='service_providers', null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='service_providers', null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.PROTECT, related_name='service_providers', null=True, blank=True)
    locality = models.ForeignKey(Locality, on_delete=models.PROTECT, related_name='service_providers', null=True, blank=True)
    service_area_scope = models.CharField(max_length=16, choices=ServiceAreaScope.choices, default=ServiceAreaScope.SPECIFIC)
    location_text = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=16)
    description = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=0)

    class Meta:
        ordering = ['-rating_average', 'user__full_name']

    def __str__(self):
        return f'{self.user.full_name} - {self.category.name}'

    def clean(self):
        if self.service_area_scope == ServiceAreaScope.SPECIFIC and not all(
            [self.country_id, self.state_id, self.district_id, self.locality_id]
        ):
            raise ValidationError('Country, state, district, and locality are required for given-location scope.')
        if self.state_id and self.country_id and self.state.country_id != self.country_id:
            raise ValidationError('State does not belong to selected country.')
        if self.district_id and self.state_id and self.district.state_id != self.state_id:
            raise ValidationError('District does not belong to selected state.')
        if self.locality_id and self.district_id and self.locality.district_id != self.district_id:
            raise ValidationError('Locality does not belong to selected district.')

    def refresh_rating(self):
        value = self.ratings_received.aggregate(avg=Avg('rating'))['avg']
        self.rating_average = round(value or 0, 2)
        self.save(update_fields=['rating_average'])


class ServiceRequest(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_requests')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.SET_NULL, null=True, blank=True, related_name='requests')
    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, related_name='service_requests')
    problem_description = models.TextField()
    status = models.CharField(max_length=16, choices=ServiceRequestStatus.choices, default=ServiceRequestStatus.REQUESTED)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class ServiceChat(models.Model):
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_messages')
    message = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']


class ServiceRating(models.Model):
    request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='rating')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_ratings_given')
    provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='ratings_received')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
