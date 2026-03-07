from django.db.models import Case, IntegerField, Value, When
from django.db.models.functions import Lower

from .models import DriverProfile, RideCategory, VehicleType


def vehicle_type_for_ride_category(ride_category):
    if not ride_category:
        return None
    name = (ride_category.name or "").lower()
    if "bike" in name:
        return VehicleType.BIKE
    if "auto" in name or "rickshaw" in name:
        return VehicleType.AUTO
    return VehicleType.CAR


def get_prioritized_driver_queryset(
    *,
    ride_category_id=None,
    pickup_state_id=None,
    pickup_district_id=None,
    pickup_locality_id=None,
    district_only=False,
):
    if not ride_category_id:
        return DriverProfile.objects.none()

    ride_category = RideCategory.objects.filter(id=ride_category_id, is_active=True).only("id", "name").first()
    vehicle_type = vehicle_type_for_ride_category(ride_category)
    if not vehicle_type:
        return DriverProfile.objects.none()

    location_priority_rules = []
    if pickup_locality_id:
        location_priority_rules.append(When(locality_id=pickup_locality_id, then=Value(1)))
    if pickup_district_id:
        location_priority_rules.append(When(district_id=pickup_district_id, then=Value(2)))
    if pickup_state_id:
        location_priority_rules.append(When(state_id=pickup_state_id, then=Value(3)))

    queryset = (
        DriverProfile.objects.filter(
            is_blocked=False,
            vehicle_type=vehicle_type,
        )
        .select_related(
            "user",
            "state",
            "district",
            "locality",
        )
        .annotate(
            location_priority=Case(
                *location_priority_rules,
                default=Value(4),
                output_field=IntegerField(),
            )
        )
        .order_by("location_priority", "-is_online", Lower("name"), "name")
    )
    if district_only and pickup_district_id:
        queryset = queryset.filter(district_id=pickup_district_id)
    return queryset
