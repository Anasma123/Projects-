from django.contrib import admin

from .models import UserRole


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role', 'created_at')
    list_filter = ('role',)
    search_fields = ('user__phone_number', 'user__full_name')
