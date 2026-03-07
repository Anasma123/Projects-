from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.utils import timezone

from apps.locations.models import Country, District, Locality, State


class CategoryRequestStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'


class ShopCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Shop(models.Model):
    owner = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='owned_shop')
    shop_name = models.CharField(max_length=200)
    shop_category = models.CharField(max_length=120)
    address = models.CharField(max_length=255)
    category = models.ForeignKey(ShopCategory, on_delete=models.PROTECT, related_name='shops', null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='shops', null=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='shops', null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.PROTECT, related_name='shops', null=True, blank=True)
    locality = models.ForeignKey(Locality, on_delete=models.PROTECT, related_name='shops', null=True, blank=True)
    location_text = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=16)
    description = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.shop_name

    def refresh_average_rating(self):
        value = self.ratings.aggregate(avg=Avg('rating'))['avg']
        self.average_rating = round(value or 0, 2)
        self.save(update_fields=['average_rating'])


class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='products')
    product_name = models.CharField(max_length=180)
    category = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['product_name']

    def __str__(self):
        return f'{self.product_name} ({self.shop.shop_name})'


class Offer(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    discount_percent = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(95)])
    valid_until = models.DateTimeField()

    class Meta:
        ordering = ['-valid_until']

    def __str__(self):
        return f'{self.title} - {self.discount_percent}%'

    @property
    def is_active(self):
        return self.valid_until >= timezone.now()


class ShopChat(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shop_messages')
    message = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']


class ShopRating(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shop_ratings')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('shop', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.shop.shop_name}: {self.rating}/5'


class ShopCategoryRequest(models.Model):
    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shop_category_requests')
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
