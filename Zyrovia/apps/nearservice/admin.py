from django.contrib import admin

from .models import ServiceCategory, ServiceCategoryRequest, ServiceChat, ServiceProvider, ServiceRating, ServiceRequest


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'category', 'is_available', 'rating_average')
    list_filter = ('category', 'is_available')
    search_fields = ('user__full_name', 'user__phone_number', 'location_text')


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'provider', 'category', 'status', 'created_at')
    list_filter = ('category', 'status')


@admin.register(ServiceCategoryRequest)
class ServiceCategoryRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'category_name', 'requested_by', 'status', 'created_at', 'reviewed_at')
    list_filter = ('status',)
    search_fields = ('category_name', 'requested_by__full_name', 'requested_by__phone_number')


@admin.register(ServiceChat)
class ServiceChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'request', 'sender', 'timestamp')


@admin.register(ServiceRating)
class ServiceRatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'request', 'provider', 'rating', 'created_at')
    list_filter = ('rating',)
