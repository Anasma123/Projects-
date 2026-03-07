from django.contrib import admin

from django.utils import timezone

from .models import Country, District, Locality, LocationRequest, LocationRequestStatus, State


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'code')
    search_fields = ('name', 'code')


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country', 'code')
    list_filter = ('country',)
    search_fields = ('name', 'code', 'country__name')


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'state', 'code')
    list_filter = ('state', 'state__country')
    search_fields = ('name', 'code', 'state__name')


@admin.register(Locality)
class LocalityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'district', 'pincode')
    list_filter = ('district', 'district__state', 'district__state__country')
    search_fields = ('name', 'pincode', 'district__name')


@admin.register(LocationRequest)
class LocationRequestAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'requested_by',
        'country_name',
        'state_name',
        'district_name',
        'locality_name',
        'status',
        'created_at',
        'reviewed_at',
    )
    list_filter = ('status',)
    search_fields = (
        'requested_by__full_name',
        'requested_by__phone_number',
        'country_name',
        'state_name',
        'district_name',
        'locality_name',
    )
    readonly_fields = ('created_at',)
    actions = ('approve_selected', 'reject_selected')

    @admin.action(description='Approve selected location requests')
    def approve_selected(self, request, queryset):
        for location_request in queryset:
            location_request.apply_approval()

    @admin.action(description='Reject selected location requests')
    def reject_selected(self, request, queryset):
        queryset.update(status=LocationRequestStatus.REJECTED, reviewed_at=timezone.now())

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change:
            previous_status = LocationRequest.objects.filter(pk=obj.pk).values_list('status', flat=True).first()
        super().save_model(request, obj, form, change)
        if obj.status == LocationRequestStatus.APPROVED and previous_status != LocationRequestStatus.APPROVED:
            obj.apply_approval()
        elif obj.status == LocationRequestStatus.REJECTED and not obj.reviewed_at:
            obj.reviewed_at = timezone.now()
            obj.save(update_fields=['reviewed_at'])
