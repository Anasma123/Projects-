from django.contrib import admin

from .models import DriverProfile, RideCategory, RideCategoryRequest, RideChatMessage, RideNotification, RideRating, RideRequest


@admin.register(DriverProfile)
class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'phone_number', 'vehicle_type', 'vehicle_number', 'is_online', 'rating_average')
    list_filter = ('vehicle_type', 'is_online')
    search_fields = ('name', 'phone_number', 'user__full_name', 'user__phone_number', 'vehicle_number')


@admin.register(RideRequest)
class RideRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'driver', 'driver_profile', 'ride_category', 'ride_type', 'status', 'is_deleted', 'created_at')
    list_filter = ('ride_category', 'ride_type', 'status', 'is_deleted')
    search_fields = ('customer__phone_number', 'driver__phone_number', 'pickup_location', 'destination')


@admin.register(RideChatMessage)
class RideChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'ride', 'sender', 'timestamp')
    search_fields = ('sender__phone_number', 'message')


@admin.register(RideRating)
class RideRatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'ride', 'customer', 'driver', 'stars', 'created_at')
    list_filter = ('stars',)


@admin.register(RideCategory)
class RideCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(RideCategoryRequest)
class RideCategoryRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'requested_by', 'category_name', 'status', 'created_at', 'reviewed_at')
    list_filter = ('status',)
    search_fields = ('requested_by__full_name', 'category_name')


@admin.register(RideNotification)
class RideNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'ride', 'action', 'is_read', 'created_at')
    list_filter = ('action', 'is_read')
    search_fields = ('recipient__full_name', 'message')
