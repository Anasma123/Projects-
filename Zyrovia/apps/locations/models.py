from django.conf import settings
from django.db import models
from django.utils import timezone


class Country(models.Model):
    name = models.CharField(max_length=120, unique=True)
    code = models.CharField(max_length=8, unique=True, null=True, blank=True)
    external_id = models.CharField(max_length=64, unique=True, null=True, blank=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]

    def __str__(self):
        return self.name


class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='states')
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=16, null=True, blank=True)
    external_id = models.CharField(max_length=64, unique=True, null=True, blank=True)

    class Meta:
        ordering = ['name']
        constraints = [models.UniqueConstraint(fields=['country', 'name'], name='unique_state_per_country')]
        indexes = [models.Index(fields=['country', 'name']), models.Index(fields=['name'])]

    def __str__(self):
        return f'{self.name}, {self.country.name}'


class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='districts')
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=16, null=True, blank=True)
    external_id = models.CharField(max_length=64, unique=True, null=True, blank=True)

    class Meta:
        ordering = ['name']
        constraints = [models.UniqueConstraint(fields=['state', 'name'], name='unique_district_per_state')]
        indexes = [models.Index(fields=['state', 'name']), models.Index(fields=['name'])]

    def __str__(self):
        return f'{self.name}, {self.state.name}'


class Locality(models.Model):
    district = models.ForeignKey(District, on_delete=models.PROTECT, related_name='localities')
    name = models.CharField(max_length=160)
    pincode = models.CharField(max_length=12, blank=True)
    external_id = models.CharField(max_length=64, unique=True, null=True, blank=True)

    class Meta:
        ordering = ['name']
        indexes = [models.Index(fields=['district', 'name']), models.Index(fields=['name']), models.Index(fields=['pincode'])]

    def __str__(self):
        return f'{self.name}, {self.district.name}'


class LocationRequestStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class LocationRequest(models.Model):
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='location_requests')
    country_name = models.CharField(max_length=120)
    state_name = models.CharField(max_length=120)
    district_name = models.CharField(max_length=120)
    locality_name = models.CharField(max_length=160)
    status = models.CharField(max_length=16, choices=LocationRequestStatus.choices, default=LocationRequestStatus.PENDING)
    admin_note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['requested_by', 'status']),
        ]

    def __str__(self):
        return f'{self.locality_name}, {self.district_name} ({self.status})'

    @staticmethod
    def _clean_part(value):
        return (value or '').strip()

    def apply_approval(self):
        country_name = self._clean_part(self.country_name)
        state_name = self._clean_part(self.state_name)
        district_name = self._clean_part(self.district_name)
        locality_name = self._clean_part(self.locality_name)
        if not all([country_name, state_name, district_name, locality_name]):
            return

        country = Country.objects.filter(name__iexact=country_name).first()
        if not country:
            country = Country.objects.create(name=country_name)

        state = State.objects.filter(country_id=country.id, name__iexact=state_name).first()
        if not state:
            state = State.objects.create(country=country, name=state_name)

        district = District.objects.filter(state_id=state.id, name__iexact=district_name).first()
        if not district:
            district = District.objects.create(state=state, name=district_name)

        if not Locality.objects.filter(district_id=district.id, name__iexact=locality_name).exists():
            Locality.objects.create(district=district, name=locality_name)

        self.status = LocationRequestStatus.APPROVED
        self.reviewed_at = timezone.now()
        self.save(update_fields=['status', 'reviewed_at'])
