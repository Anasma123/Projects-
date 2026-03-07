from django.contrib import admin

from .models import PlatformReport


@admin.register(PlatformReport)
class PlatformReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'target_type', 'target_id', 'reporter', 'is_resolved', 'created_at')
    list_filter = ('target_type', 'is_resolved')
    search_fields = ('reporter__phone_number', 'reason')
