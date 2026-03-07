from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_GET

from apps.locations.models import Country, District, Locality, LocationRequest, LocationRequestStatus, State
from apps.roles.models import RoleChoices, UserRole

from .forms import DriverProfileForm, LocationRequestForm, RideCategoryRequestForm, RideChatMessageForm, RideRatingForm, RideRequestForm
from .models import CategoryRequestStatus, DriverProfile, LocationScope, RideCategory, RideCategoryRequest, RideNotification, RideRequest, RideStatus, RideRating, VehicleType
from .services import get_prioritized_driver_queryset, vehicle_type_for_ride_category


def _get_driver_profile(user, driver_id=None):
    queryset = DriverProfile.objects.filter(user=user)
    if driver_id:
        queryset = queryset.filter(id=driver_id)
    return queryset.order_by('-created_at').first()


def _is_ride_participant(ride, user):
    return ride.customer_id == user.id or ride.driver_id == user.id


def _int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _vehicle_type_from_category(category):
    vehicle_type = vehicle_type_for_ride_category(category)
    return vehicle_type or VehicleType.CAR


def _notify_user(recipient, ride, action, message):
    if not recipient or not ride:
        return
    RideNotification.objects.create(
        recipient=recipient,
        ride=ride,
        action=action[:32],
        message=message[:255],
    )


def _notify_other_participant(ride, actor, action, message):
    recipients = []
    if ride.customer_id and ride.customer_id != getattr(actor, 'id', None):
        recipients.append(ride.customer)
    if ride.driver_id and ride.driver_id != getattr(actor, 'id', None):
        recipients.append(ride.driver)
    for recipient in recipients:
        _notify_user(recipient, ride, action, message)


def nearride_dashboard(request):
    selected_category = _int_or_none(request.GET.get('category'))
    category_options = RideCategory.objects.filter(is_active=True).order_by('name')
    if not request.user.is_authenticated:
        return render(
            request,
            'nearride/dashboard.html',
            {
                'driver_profile': None,
                'customer_rides': [],
                'driver_rides': [],
                'pending_for_driver': 0,
                'is_guest': True,
                'category_options': category_options,
                'selected_category': selected_category,
                'recent_notifications': [],
                'unread_notifications_count': 0,
            },
        )

    driver_profiles = DriverProfile.objects.filter(user=request.user).order_by('-created_at')
    driver_profile = driver_profiles.first()
    customer_rides = RideRequest.objects.select_related('pickup_locality', 'destination_locality', 'ride_category').filter(
        customer=request.user,
        is_deleted=False,
    )
    driver_rides = (
        RideRequest.objects.select_related('pickup_locality', 'destination_locality', 'ride_category').filter(driver=request.user, is_deleted=False)
        if driver_profile
        else []
    )

    if selected_category:
        customer_rides = customer_rides.filter(ride_category_id=selected_category)
        if driver_profile:
            driver_rides = driver_rides.filter(ride_category_id=selected_category)

    customer_rides = customer_rides[:8]
    driver_rides = driver_rides[:8] if driver_profile else []
    pending_for_driver = 0

    if driver_profiles.filter(is_online=True).exists():
        vehicle_types = list(driver_profiles.values_list('vehicle_type', flat=True).distinct())
        pending_query = RideRequest.objects.filter(
            status=RideStatus.REQUESTED,
            ride_type__in=vehicle_types,
            is_deleted=False,
        ).exclude(customer=request.user).count()
        pending_for_driver = pending_query

    recent_notifications = RideNotification.objects.filter(recipient=request.user).select_related('ride')[:8]
    unread_notifications_count = RideNotification.objects.filter(recipient=request.user, is_read=False).count()

    return render(
        request,
        'nearride/dashboard.html',
        {
            'driver_profile': driver_profile,
            'driver_profiles': driver_profiles[:5],
            'customer_rides': customer_rides,
            'driver_rides': driver_rides,
            'pending_for_driver': pending_for_driver,
            'is_guest': False,
            'category_options': category_options,
            'selected_category': selected_category,
            'recent_notifications': recent_notifications,
            'unread_notifications_count': unread_notifications_count,
        },
    )


@login_required
def become_driver(request):
    form = DriverProfileForm(
        request.POST or None,
        initial={'name': request.user.full_name, 'phone_number': request.user.phone_number},
    )
    if request.method == 'POST' and form.is_valid():
        profile = form.save(commit=False)
        profile.user = request.user
        if not profile.name:
            profile.name = request.user.full_name
        if not profile.phone_number:
            profile.phone_number = request.user.phone_number
        profile.save()
        UserRole.assign_role(request.user, RoleChoices.DRIVER)
        messages.success(request, 'Driver profile created successfully.')
        return redirect('nearride:driver-dashboard')

    return render(request, 'nearride/become_driver.html', {'form': form})


@login_required
def driver_dashboard(request):
    drivers = DriverProfile.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'nearride/driver_dashboard.html', {'drivers': drivers})


@login_required
def edit_driver(request, driver_id: int):
    profile = get_object_or_404(DriverProfile, id=driver_id, user=request.user)
    form = DriverProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Driver profile updated successfully.')
        return redirect('nearride:driver-dashboard')
    return render(request, 'nearride/edit_driver.html', {'form': form, 'driver_profile': profile})


@login_required
def delete_driver(request, driver_id: int):
    profile = get_object_or_404(DriverProfile, id=driver_id, user=request.user)
    if request.method == 'POST':
        profile.delete()
        messages.success(request, 'Driver profile deleted successfully.')
        return redirect('nearride:driver-dashboard')
    return render(request, 'nearride/delete_driver_confirm.html', {'driver_profile': profile})


@login_required
def toggle_driver_status(request, driver_id: int = None):
    if request.method != 'POST':
        return redirect('nearride:driver-dashboard')

    profile = _get_driver_profile(request.user, driver_id=driver_id)
    if not profile:
        return HttpResponseForbidden('Driver profile required.')

    profile.is_online = not profile.is_online
    profile.save(update_fields=['is_online'])
    messages.success(request, f"You are now {'online' if profile.is_online else 'offline'}.")
    return redirect('nearride:driver-dashboard')


@login_required
def create_ride_request(request):
    form = RideRequestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ride = form.save(commit=False)
        selected_driver_profile = form.cleaned_data.get('driver_profile')
        ride.customer = request.user
        ride.driver_profile = selected_driver_profile
        ride.driver = selected_driver_profile.user if selected_driver_profile else None
        ride.status = RideStatus.REQUESTED
        ride.ride_type = _vehicle_type_from_category(ride.ride_category)
        ride.save()
        if ride.driver_id:
            _notify_user(
                ride.driver,
                ride,
                'requested',
                f'New ride request #{ride.id} from {request.user.full_name}.',
            )
        messages.success(request, 'Ride request submitted. Waiting for driver acceptance.')
        return render(
            request,
            'nearride/ride_request_submitted.html',
            {
                'ride': ride,
                'driver_phone': selected_driver_profile.phone_number if selected_driver_profile else '',
            },
        )

    return render(request, 'nearride/create_ride.html', {'form': form})


def _driver_option_payload(profile):
    display_name = profile.name or (profile.user.full_name if profile.user_id else '') or profile.phone_number
    district_name = profile.district.name if profile.district_id else 'N/A'
    locality_name = profile.locality.name if profile.locality_id else 'N/A'
    vehicle_name = profile.get_vehicle_type_display()
    is_online = bool(profile.is_online)
    status_label = 'Active' if is_online else 'Offline'
    label = (
        f'{display_name} - {vehicle_name} - '
        f'{district_name} - {locality_name} - {status_label} - {profile.phone_number}'
    )
    return {
        'id': profile.id,
        'name': display_name,
        'vehicle_type': vehicle_name,
        'district': district_name,
        'locality': locality_name,
        'phone_number': profile.phone_number,
        'is_online': is_online,
        'status': status_label,
        'label': label,
    }


@login_required
@require_GET
def available_drivers_api(request):
    ride_category_id = _int_or_none(request.GET.get('ride_category_id'))
    pickup_state_id = _int_or_none(request.GET.get('pickup_state_id'))
    pickup_district_id = _int_or_none(request.GET.get('pickup_district_id'))
    pickup_locality_id = _int_or_none(request.GET.get('pickup_locality_id'))
    scope = (request.GET.get('scope') or 'district').strip().lower()
    district_only = scope == 'district'
    if not ride_category_id:
        return JsonResponse({'items': []})

    drivers = get_prioritized_driver_queryset(
        ride_category_id=ride_category_id,
        pickup_state_id=pickup_state_id,
        pickup_district_id=pickup_district_id,
        pickup_locality_id=pickup_locality_id,
        district_only=district_only,
    )
    items = [_driver_option_payload(driver) for driver in drivers]
    return JsonResponse({'items': items})


@login_required
def driver_requests(request):
    profile = _get_driver_profile(request.user)
    if not profile:
        return HttpResponseForbidden('Only registered drivers can access this page.')
    if profile.is_blocked:
        return HttpResponseForbidden('Blocked drivers cannot access requests.')

    pending_rides = RideRequest.objects.select_related(
        'customer',
        'pickup_country',
        'pickup_state',
        'pickup_district',
        'pickup_locality',
        'ride_category',
    ).filter(
        status=RideStatus.REQUESTED,
        ride_type=profile.vehicle_type,
        is_deleted=False,
    ).exclude(customer=request.user)

    if profile.service_area_scope == LocationScope.SPECIFIC and profile.locality_id:
        pending_rides = pending_rides.filter(pickup_locality_id=profile.locality_id)

    return render(
        request,
        'nearride/driver_requests.html',
        {
            'driver_profile': profile,
            'pending_rides': pending_rides,
        },
    )


@login_required
def accept_ride_request(request, ride_id: int):
    if request.method != 'POST':
        return redirect('nearride:driver-requests')

    profile = _get_driver_profile(request.user)
    if not profile or not profile.is_online:
        return HttpResponseForbidden('Only online drivers can accept rides.')
    if profile.is_blocked:
        return HttpResponseForbidden('Blocked drivers cannot accept rides.')

    with transaction.atomic():
        ride = get_object_or_404(RideRequest.objects.select_for_update(), id=ride_id, is_deleted=False)
        if ride.status != RideStatus.REQUESTED:
            messages.error(request, 'Ride is no longer available.')
            return redirect('nearride:driver-requests')
        if ride.driver_id and ride.driver_id != request.user.id:
            messages.error(request, 'This ride is assigned to another driver.')
            return redirect('nearride:driver-requests')
        if ride.ride_type != profile.vehicle_type:
            return HttpResponseForbidden('Ride category mismatch for driver.')
        if profile.service_area_scope == LocationScope.SPECIFIC and profile.locality_id and ride.pickup_locality_id != profile.locality_id:
            return HttpResponseForbidden('Ride is outside your configured service location.')

        ride.driver = request.user
        ride.driver_profile = profile
        ride.status = RideStatus.ACCEPTED
        ride.save(update_fields=['driver', 'driver_profile', 'status'])
        _notify_user(
            ride.customer,
            ride,
            'accepted',
            f'Your ride #{ride.id} was accepted by {request.user.full_name}.',
        )

    messages.success(request, 'Ride accepted successfully.')
    return redirect('nearride:ride-detail', ride_id=ride_id)


@login_required
def reject_ride_request(request, ride_id: int):
    if request.method != 'POST':
        return redirect('nearride:driver-requests')

    profile = _get_driver_profile(request.user)
    if not profile:
        return HttpResponseForbidden('Only registered drivers can reject rides.')

    ride = get_object_or_404(RideRequest, id=ride_id, is_deleted=False)
    if ride.status != RideStatus.REQUESTED:
        messages.error(request, 'Ride is no longer pending.')
    else:
        ride.status = RideStatus.REJECTED
        ride.save(update_fields=['status'])
        _notify_user(
            ride.customer,
            ride,
            'rejected',
            f'Your ride #{ride.id} was rejected by {request.user.full_name}.',
        )
        messages.info(request, 'Ride rejected.')
    return redirect('nearride:driver-requests')


@login_required
def ride_detail(request, ride_id: int):
    ride = get_object_or_404(
        RideRequest.objects.select_related(
            'customer',
            'driver',
            'pickup_country',
            'pickup_state',
            'pickup_district',
            'pickup_locality',
            'destination_country',
            'destination_state',
            'destination_district',
            'destination_locality',
            'ride_category',
        ),
        id=ride_id,
        is_deleted=False,
    )
    if not _is_ride_participant(ride, request.user):
        return HttpResponseForbidden('Unauthorized ride access.')

    is_customer = ride.customer_id == request.user.id
    is_driver = ride.driver_id == request.user.id
    chat_form = RideChatMessageForm(request.POST or None, prefix='chat')
    rating_form = RideRatingForm(request.POST or None, prefix='rating')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'send_message' and chat_form.is_valid():
            chat = chat_form.save(commit=False)
            chat.ride = ride
            chat.sender = request.user
            chat.save()
            return redirect('nearride:ride-detail', ride_id=ride.id)

        if action == 'accept_ride' and is_driver and ride.status == RideStatus.REQUESTED:
            if ride.driver_id and ride.driver_id != request.user.id:
                messages.error(request, 'This ride is assigned to another driver.')
                return redirect('nearride:ride-detail', ride_id=ride.id)
            profile = DriverProfile.objects.filter(user=request.user, is_blocked=False).first()
            if not profile:
                messages.error(request, 'Driver profile is required to accept this ride.')
                return redirect('nearride:ride-detail', ride_id=ride.id)
            if ride.ride_type != profile.vehicle_type:
                messages.error(request, 'Vehicle type mismatch for this ride.')
                return redirect('nearride:ride-detail', ride_id=ride.id)
            ride.driver = request.user
            ride.driver_profile = profile
            ride.status = RideStatus.ACCEPTED
            ride.save(update_fields=['driver', 'driver_profile', 'status'])
            _notify_user(
                ride.customer,
                ride,
                'accepted',
                f'Your ride #{ride.id} was accepted by {request.user.full_name}.',
            )
            messages.success(request, 'Ride accepted successfully.')
            return redirect('nearride:ride-detail', ride_id=ride.id)

        if action == 'complete_ride' and is_driver and ride.status == RideStatus.ACCEPTED:
            completion_note = (request.POST.get('completion_note') or '').strip()
            ride.status = RideStatus.COMPLETED
            ride.completion_note = completion_note[:255]
            ride.save(update_fields=['status', 'completion_note'])
            _notify_other_participant(
                ride,
                request.user,
                'completed',
                f'Ride #{ride.id} marked completed by {request.user.full_name}.',
            )
            messages.success(request, 'Ride marked as completed.')
            return redirect('nearride:ride-detail', ride_id=ride.id)

        customer_can_cancel = is_customer and ride.status == RideStatus.REQUESTED
        driver_can_cancel = is_driver and ride.status in {RideStatus.REQUESTED, RideStatus.ACCEPTED}
        if action == 'cancel_ride' and (customer_can_cancel or driver_can_cancel):
            cancel_reason = (request.POST.get('cancel_reason') or '').strip()
            if not cancel_reason:
                messages.error(request, 'Cancellation reason is required.')
                return redirect('nearride:ride-detail', ride_id=ride.id)
            ride.status = RideStatus.CANCELLED
            ride.cancel_reason = cancel_reason[:255]
            ride.save(update_fields=['status', 'cancel_reason'])
            _notify_other_participant(
                ride,
                request.user,
                'cancelled',
                f'Ride #{ride.id} was cancelled by {request.user.full_name}. Reason: {ride.cancel_reason}',
            )
            messages.success(request, 'Ride cancelled.')
            return redirect('nearride:ride-detail', ride_id=ride.id)

        if action == 'reject_ride' and is_driver and ride.status == RideStatus.REQUESTED:
            reject_reason = (request.POST.get('cancel_reason') or '').strip()
            if not reject_reason:
                messages.error(request, 'Rejection reason is required.')
                return redirect('nearride:ride-detail', ride_id=ride.id)
            ride.status = RideStatus.REJECTED
            ride.cancel_reason = reject_reason[:255]
            ride.save(update_fields=['status', 'cancel_reason'])
            _notify_user(
                ride.customer,
                ride,
                'rejected',
                f'Ride #{ride.id} was rejected by {request.user.full_name}. Reason: {ride.cancel_reason}',
            )
            messages.success(request, 'Ride rejected.')
            return redirect('nearride:ride-detail', ride_id=ride.id)

        allowed_delete_statuses = {RideStatus.COMPLETED, RideStatus.CANCELLED, RideStatus.REJECTED}
        if action == 'delete_ride' and (is_customer or is_driver):
            if ride.status not in allowed_delete_statuses:
                messages.error(request, 'Only completed/cancelled/rejected rides can be deleted.')
                return redirect('nearride:ride-detail', ride_id=ride.id)
            delete_reason = (request.POST.get('delete_reason') or '').strip()
            if not delete_reason:
                messages.error(request, 'Delete reason is required.')
                return redirect('nearride:ride-detail', ride_id=ride.id)
            ride.is_deleted = True
            ride.deleted_at = timezone.now()
            ride.deletion_reason = delete_reason[:255]
            ride.save(update_fields=['is_deleted', 'deleted_at', 'deletion_reason'])
            _notify_other_participant(
                ride,
                request.user,
                'deleted',
                f'Ride #{ride.id} was deleted by {request.user.full_name}. Reason: {ride.deletion_reason}',
            )
            messages.success(request, 'Ride deleted successfully.')
            return redirect('nearride:dashboard')

        if action == 'rate_driver' and is_customer and ride.status == RideStatus.COMPLETED and ride.driver_id:
            if hasattr(ride, 'rating'):
                messages.info(request, 'Driver has already been rated for this ride.')
            elif rating_form.is_valid():
                rating = rating_form.save(commit=False)
                rating.ride = ride
                rating.customer = request.user
                rating.driver = ride.driver
                rating.save()
                for driver_profile in DriverProfile.objects.filter(user=ride.driver):
                    driver_profile.refresh_rating()
                _notify_user(
                    ride.driver,
                    ride,
                    'rated',
                    f'You received a rating for ride #{ride.id}.',
                )
                messages.success(request, 'Thanks for your rating.')
            return redirect('nearride:ride-detail', ride_id=ride.id)

    context = {
        'ride': ride,
        'is_customer': is_customer,
        'is_driver': is_driver,
        'chat_form': chat_form,
        'rating_form': rating_form,
        'messages_history': ride.messages.select_related('sender').all(),
        'can_rate': is_customer and ride.status == RideStatus.COMPLETED and ride.driver_id and not hasattr(ride, 'rating'),
        'can_complete': is_driver and ride.status == RideStatus.ACCEPTED,
        'can_accept': is_driver and ride.status == RideStatus.REQUESTED,
        'can_reject': is_driver and ride.status == RideStatus.REQUESTED,
        'can_cancel': (is_customer and ride.status == RideStatus.REQUESTED) or (is_driver and ride.status in {RideStatus.REQUESTED, RideStatus.ACCEPTED}),
        'can_delete': (is_customer or is_driver) and ride.status in {RideStatus.COMPLETED, RideStatus.CANCELLED, RideStatus.REJECTED},
        'driver_profile_id': ride.driver_profile_id,
    }
    return render(request, 'nearride/ride_detail.html', context)


@login_required
def request_new_location(request):
    form = LocationRequestForm(request.POST or None, initial={'requested_by': request.user})
    if request.method == 'POST' and form.is_valid():
        location_request = form.save(commit=False)
        location_request.requested_by = request.user
        location_request.status = LocationRequestStatus.PENDING
        location_request.save()
        messages.success(request, 'Location request submitted successfully.')
        return redirect('nearride:my-location-requests')
    return render(request, 'nearride/request_location.html', {'form': form})


@login_required
def my_location_requests(request):
    requests_list = LocationRequest.objects.filter(requested_by=request.user).order_by('-created_at')
    return render(request, 'nearride/my_location_requests.html', {'requests_list': requests_list})


@login_required
def my_ride_notifications(request):
    notifications = RideNotification.objects.filter(recipient=request.user).select_related('ride')
    RideNotification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return render(request, 'nearride/my_notifications.html', {'notifications': notifications})


@login_required
def request_ride_category(request):
    form = RideCategoryRequestForm(request.POST or None, initial={'requested_by': request.user})
    if request.method == 'POST' and form.is_valid():
        category_request = form.save(commit=False)
        category_request.requested_by = request.user
        category_request.status = CategoryRequestStatus.PENDING
        category_request.save()
        messages.success(request, 'Ride category request submitted successfully.')
        return redirect('nearride:my-ride-category-requests')

    return render(request, 'nearride/request_category.html', {'form': form})


@login_required
def my_ride_category_requests(request):
    requests_list = RideCategoryRequest.objects.filter(requested_by=request.user).order_by('-created_at')
    return render(request, 'nearride/my_category_requests.html', {'requests_list': requests_list})
