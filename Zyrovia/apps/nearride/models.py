from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.utils import timezone

from apps.locations.models import Country, District, Locality, State


class VehicleType(models.TextChoices):
    AUTO = 'auto', 'Auto'
    BIKE = 'bike', 'Bike'
    CAR = 'car', 'Car'


class RideStatus(models.TextChoices):
    REQUESTED = 'requested', 'Pending'
    ACCEPTED = 'accepted', 'Accepted'
    REJECTED = 'rejected', 'Rejected'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'


class LocationScope(models.TextChoices):
    SPECIFIC = 'specific', 'Given Location'
    ALL = 'all', 'All Locations'


class CategoryRequestStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class RideCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class DriverProfile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='driver_profiles')
    name = models.CharField(max_length=255, default='')
    phone_number = models.CharField(max_length=16, default='')
    vehicle_type = models.CharField(max_length=10, choices=VehicleType.choices)
    ride_category = models.ForeignKey(RideCategory, on_delete=models.PROTECT, related_name='drivers', null=True, blank=True)
    vehicle_number = models.CharField(max_length=32, unique=True)
    is_online = models.BooleanField(default=False)
    service_area_scope = models.CharField(max_length=16, choices=LocationScope.choices, default=LocationScope.SPECIFIC)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='drivers', null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='drivers', null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.PROTECT, related_name='drivers', null=True, blank=True)
    locality = models.ForeignKey(Locality, on_delete=models.PROTECT, related_name='drivers', null=True, blank=True)
    current_location = models.CharField(max_length=255, blank=True)
    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    rating_average = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} - {self.vehicle_type}'

    def refresh_rating(self):
        average = RideRating.objects.filter(driver=self.user).aggregate(avg=Avg('stars'))['avg']
        self.rating_average = round(average or 0, 2)
        self.save(update_fields=['rating_average'])


class RideRequest(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_rides')
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='driver_rides',
    )
    driver_profile = models.ForeignKey(
        DriverProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_rides',
    )
    pickup_location = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    pickup_country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='pickup_rides', null=True, blank=True)
    pickup_state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='pickup_rides', null=True, blank=True)
    pickup_district = models.ForeignKey(District, on_delete=models.PROTECT, related_name='pickup_rides', null=True, blank=True)
    pickup_locality = models.ForeignKey(Locality, on_delete=models.PROTECT, related_name='pickup_rides', null=True, blank=True)
    destination_country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='destination_rides', null=True, blank=True)
    destination_state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='destination_rides', null=True, blank=True)
    destination_district = models.ForeignKey(District, on_delete=models.PROTECT, related_name='destination_rides', null=True, blank=True)
    destination_locality = models.ForeignKey(Locality, on_delete=models.PROTECT, related_name='destination_rides', null=True, blank=True)
    ride_category = models.ForeignKey(RideCategory, on_delete=models.PROTECT, related_name='ride_requests', null=True, blank=True)
    ride_type = models.CharField(max_length=10, choices=VehicleType.choices)
    status = models.CharField(max_length=16, choices=RideStatus.choices, default=RideStatus.REQUESTED)
    cancel_reason = models.CharField(max_length=255, blank=True)
    completion_note = models.CharField(max_length=255, blank=True)
    is_deleted = models.BooleanField(default=False)
    deletion_reason = models.CharField(max_length=255, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Ride #{self.pk} ({self.ride_type})'


class RideNotification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ride_notifications')
    ride = models.ForeignKey(RideRequest, on_delete=models.CASCADE, related_name='notifications')
    action = models.CharField(max_length=32)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['recipient', 'is_read']), models.Index(fields=['created_at'])]

    def __str__(self):
        return f'RideNotification({self.recipient_id}, ride={self.ride_id}, {self.action})'


class RideChatMessage(models.Model):
    ride = models.ForeignKey(RideRequest, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ride_messages')
    message = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']


class RideRating(models.Model):
    ride = models.OneToOneField(RideRequest, on_delete=models.CASCADE, related_name='rating')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_ride_ratings')
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_ride_ratings')
    stars = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Rating {self.stars}/5 for ride {self.ride_id}'


class RideCategoryRequest(models.Model):
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ride_category_requests')
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
