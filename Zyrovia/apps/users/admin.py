from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    list_display = ('id', 'phone_number', 'full_name', 'email', 'is_staff', 'created_at')
    ordering = ('-created_at',)
    search_fields = ('phone_number', 'full_name', 'email')

    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal', {'fields': ('full_name', 'email', 'profile_image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at', 'last_login')
    add_fieldsets = ((None, {'classes': ('wide',), 'fields': ('phone_number', 'full_name', 'email', 'profile_image', 'password1', 'password2', 'is_staff', 'is_active')}),)
