from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.db.models.functions import Lower
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from apps.locations.models import Country, District, Locality, State
from apps.roles.models import RoleChoices, UserRole

from .forms import ServiceCategoryForm, ServiceCategoryRequestForm, ServiceChatForm, ServiceProviderForm, ServiceRatingForm, ServiceRequestForm
from .models import CategoryRequestStatus, ServiceAreaScope, ServiceCategory, ServiceCategoryRequest, ServiceProvider, ServiceRating, ServiceRequest, ServiceRequestStatus


def _is_request_participant(service_request, user):
    provider_user_id = service_request.provider.user_id if service_request.provider_id else None
    return service_request.customer_id == user.id or provider_user_id == user.id


def _provider_for_user(user):
    return ServiceProvider.objects.filter(user=user).select_related('category', 'country', 'state', 'district', 'locality').first()


def _int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def nearservice_dashboard(request):
    categories = ServiceCategory.objects.filter(is_active=True)[:8]
    providers = ServiceProvider.objects.select_related('user', 'category', 'country', 'state', 'district', 'locality').filter(
        is_available=True,
        is_active=True,
        is_verified=True,
        category__is_active=True,
    )[:8]
    provider_profile = _provider_for_user(request.user) if request.user.is_authenticated else None
    category_requests = (
        ServiceCategoryRequest.objects.filter(requested_by=request.user).order_by('-created_at')[:5]
        if request.user.is_authenticated
        else []
    )
    return render(
        request,
        'nearservice/dashboard.html',
        {
            'categories': categories,
            'providers': providers,
            'provider_profile': provider_profile,
            'category_requests': category_requests,
        },
    )


def categories_page(request):
    categories = ServiceCategory.objects.filter(is_active=True)
    return render(request, 'nearservice/categories.html', {'categories': categories})


@login_required
def category_create(request):
    if not request.user.is_staff:
        return HttpResponseForbidden('Only admins can create categories.')

    form = ServiceCategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category created successfully.')
        return redirect('nearservice:categories')

    return render(request, 'nearservice/category_form.html', {'form': form, 'title': 'Create Category'})


@login_required
def category_edit(request, category_id: int):
    if not request.user.is_staff:
        return HttpResponseForbidden('Only admins can edit categories.')

    category = get_object_or_404(ServiceCategory, id=category_id)
    form = ServiceCategoryForm(request.POST or None, instance=category)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category updated.')
        return redirect('nearservice:categories')

    return render(request, 'nearservice/category_form.html', {'form': form, 'title': 'Edit Category'})


@login_required
def request_category(request):
    form = ServiceCategoryRequestForm(request.POST or None, initial={'requested_by': request.user})
    if request.method == 'POST' and form.is_valid():
        category_request = form.save(commit=False)
        category_request.requested_by = request.user
        category_request.status = CategoryRequestStatus.PENDING
        category_request.save()
        messages.success(request, 'Category request submitted successfully.')
        return redirect('nearservice:my-category-requests')

    return render(request, 'nearservice/request_category.html', {'form': form})


@login_required
def my_category_requests(request):
    requests_list = ServiceCategoryRequest.objects.filter(requested_by=request.user).order_by('-created_at')
    return render(request, 'nearservice/my_category_requests.html', {'requests_list': requests_list})


def provider_list(request):
    providers = ServiceProvider.objects.select_related('user', 'category', 'country', 'state', 'district', 'locality').filter(
        category__is_active=True,
        is_active=True,
        is_verified=True,
    )
    category_id = _int_or_none(request.GET.get('category'))
    country_id = _int_or_none(request.GET.get('country'))
    state_id = _int_or_none(request.GET.get('state'))
    district_id = _int_or_none(request.GET.get('district'))
    locality_id = _int_or_none(request.GET.get('locality'))

    if category_id:
        providers = providers.filter(category_id=category_id)
    if country_id:
        providers = providers.filter(Q(service_area_scope=ServiceAreaScope.ALL) | Q(country_id=country_id))
    if state_id:
        providers = providers.filter(Q(service_area_scope=ServiceAreaScope.ALL) | Q(state_id=state_id))
    if district_id:
        providers = providers.filter(Q(service_area_scope=ServiceAreaScope.ALL) | Q(district_id=district_id))
    if locality_id:
        providers = providers.filter(Q(service_area_scope=ServiceAreaScope.ALL) | Q(locality_id=locality_id))

    categories = ServiceCategory.objects.filter(is_active=True)
    countries = Country.objects.order_by(Lower('name'), 'name')
    states = State.objects.filter(country_id=country_id).order_by(Lower('name'), 'name') if country_id else State.objects.none()
    districts = District.objects.filter(state_id=state_id).order_by(Lower('name'), 'name') if state_id else District.objects.none()
    localities = Locality.objects.filter(district_id=district_id).order_by(Lower('name'), 'name') if district_id else Locality.objects.none()

    return render(
        request,
        'nearservice/provider_list.html',
        {
            'providers': providers,
            'categories': categories,
            'countries': countries,
            'states': states,
            'districts': districts,
            'localities': localities,
            'selected_country': country_id,
            'selected_state': state_id,
            'selected_district': district_id,
            'selected_locality': locality_id,
        },
    )


def provider_profile(request, provider_id: int):
    provider = get_object_or_404(
        ServiceProvider.objects.select_related('user', 'category', 'country', 'state', 'district', 'locality'),
        id=provider_id,
    )
    if not provider.is_active and (not request.user.is_authenticated or request.user.id != provider.user_id):
        return HttpResponseForbidden('Provider profile is not currently available.')
    requests_as_provider = ServiceRequest.objects.filter(provider=provider, is_deleted=False)[:10]
    return render(
        request,
        'nearservice/provider_profile.html',
        {
            'provider': provider,
            'requests_as_provider': requests_as_provider,
        },
    )


@login_required
def become_provider(request):
    profile = _provider_for_user(request.user)
    if profile:
        messages.info(request, 'You are already a service provider.')
        return redirect('nearservice:provider-manage')

    form = ServiceProviderForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        provider = form.save(commit=False)
        provider.user = request.user
        provider.save()
        UserRole.assign_role(request.user, RoleChoices.SERVICE_PROVIDER)
        messages.success(request, 'Service provider profile created.')
        return redirect('nearservice:provider-manage')

    return render(request, 'nearservice/become_provider.html', {'form': form})


@login_required
def provider_profile_manage(request):
    profile = _provider_for_user(request.user)
    if not profile:
        return redirect('nearservice:become-provider')

    form = ServiceProviderForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Provider profile updated.')
        return redirect('nearservice:provider-manage')

    return render(request, 'nearservice/provider_manage.html', {'form': form, 'profile': profile})


@login_required
def toggle_availability(request):
    if request.method != 'POST':
        return redirect('nearservice:provider-dashboard')

    profile = _provider_for_user(request.user)
    if not profile:
        return HttpResponseForbidden('Only providers can update availability.')

    profile.is_available = not profile.is_available
    profile.save(update_fields=['is_available'])
    messages.success(request, f"You are now {'available' if profile.is_available else 'unavailable'} for new requests.")
    return redirect('nearservice:provider-dashboard')


@login_required
def request_service(request):
    country_id = _int_or_none(request.POST.get('country_id') if request.method == 'POST' else request.GET.get('country_id'))
    state_id = _int_or_none(request.POST.get('state_id') if request.method == 'POST' else request.GET.get('state_id'))
    district_id = _int_or_none(request.POST.get('district_id') if request.method == 'POST' else request.GET.get('district_id'))
    locality_id = _int_or_none(request.POST.get('locality_id') if request.method == 'POST' else request.GET.get('locality_id'))

    form = ServiceRequestForm(
        request.POST or None,
        initial={
            'country_id': country_id,
            'state_id': state_id,
            'district_id': district_id,
            'locality_id': locality_id,
        },
    )
    if request.method == 'POST' and form.is_valid():
        provider = form.cleaned_data['provider']
        category = form.cleaned_data['category']
        if provider.category_id != category.id:
            form.add_error('provider', 'Selected provider does not belong to selected category.')
        elif not provider.is_available:
            form.add_error('provider', 'Selected provider is not available right now.')
        elif provider.service_area_scope != ServiceAreaScope.ALL and country_id and provider.country_id != country_id:
            form.add_error('provider', 'Selected provider does not match selected country.')
        elif provider.service_area_scope != ServiceAreaScope.ALL and state_id and provider.state_id != state_id:
            form.add_error('provider', 'Selected provider does not match selected state.')
        elif provider.service_area_scope != ServiceAreaScope.ALL and district_id and provider.district_id != district_id:
            form.add_error('provider', 'Selected provider does not match selected district.')
        elif provider.service_area_scope != ServiceAreaScope.ALL and locality_id and provider.locality_id != locality_id:
            form.add_error('provider', 'Selected provider does not match selected locality.')
        else:
            service_request = form.save(commit=False)
            service_request.customer = request.user
            service_request.status = ServiceRequestStatus.REQUESTED
            service_request.save()
            messages.success(request, 'Service request created successfully.')
            return redirect('nearservice:request-detail', request_id=service_request.id)

    countries = Country.objects.order_by(Lower('name'), 'name')
    states = State.objects.filter(country_id=country_id).order_by(Lower('name'), 'name') if country_id else State.objects.none()
    districts = District.objects.filter(state_id=state_id).order_by(Lower('name'), 'name') if state_id else District.objects.none()
    localities = Locality.objects.filter(district_id=district_id).order_by(Lower('name'), 'name') if district_id else Locality.objects.none()
    return render(
        request,
        'nearservice/request_service.html',
        {
            'form': form,
            'countries': countries,
            'states': states,
            'districts': districts,
            'localities': localities,
            'selected_country': country_id,
            'selected_state': state_id,
            'selected_district': district_id,
            'selected_locality': locality_id,
        },
    )


@login_required
def provider_dashboard(request):
    profile = _provider_for_user(request.user)
    if not profile:
        return HttpResponseForbidden('Only providers can access this dashboard.')
    if not profile.is_active:
        return HttpResponseForbidden('Provider account is disabled.')

    incoming_requests = ServiceRequest.objects.select_related('customer', 'category').filter(provider=profile, is_deleted=False)
    pending_count = incoming_requests.filter(status=ServiceRequestStatus.REQUESTED).count()

    return render(
        request,
        'nearservice/provider_dashboard.html',
        {
            'profile': profile,
            'incoming_requests': incoming_requests,
            'pending_count': pending_count,
        },
    )


@login_required
def accept_request(request, request_id: int):
    if request.method != 'POST':
        return redirect('nearservice:provider-dashboard')

    profile = _provider_for_user(request.user)
    if not profile:
        return HttpResponseForbidden('Only providers can accept requests.')
    if not profile.is_active:
        return HttpResponseForbidden('Provider account is disabled.')

    with transaction.atomic():
        service_request = get_object_or_404(ServiceRequest.objects.select_for_update().select_related('provider'), id=request_id, is_deleted=False)
        if service_request.provider_id != profile.id:
            return HttpResponseForbidden('Unauthorized request access.')
        if service_request.status != ServiceRequestStatus.REQUESTED:
            messages.error(request, 'Request is no longer pending.')
            return redirect('nearservice:provider-dashboard')

        service_request.status = ServiceRequestStatus.ACCEPTED
        service_request.save(update_fields=['status'])

    messages.success(request, 'Request accepted.')
    return redirect('nearservice:request-detail', request_id=request_id)


@login_required
def reject_request(request, request_id: int):
    if request.method != 'POST':
        return redirect('nearservice:provider-dashboard')

    profile = _provider_for_user(request.user)
    if not profile:
        return HttpResponseForbidden('Only providers can reject requests.')

    service_request = get_object_or_404(ServiceRequest, id=request_id, is_deleted=False)
    if service_request.provider_id != profile.id:
        return HttpResponseForbidden('Unauthorized request access.')

    if service_request.status == ServiceRequestStatus.REQUESTED:
        service_request.status = ServiceRequestStatus.CANCELLED
        service_request.save(update_fields=['status'])
        messages.info(request, 'Request rejected.')

    return redirect('nearservice:provider-dashboard')


@login_required
def service_request_detail(request, request_id: int):
    service_request = get_object_or_404(
        ServiceRequest.objects.select_related('customer', 'provider__user', 'category'),
        id=request_id,
        is_deleted=False,
    )
    if not _is_request_participant(service_request, request.user):
        return HttpResponseForbidden('Unauthorized request access.')

    is_customer = service_request.customer_id == request.user.id
    provider_profile = _provider_for_user(request.user)
    is_provider = bool(provider_profile and service_request.provider_id == provider_profile.id)

    chat_form = ServiceChatForm(request.POST or None, prefix='chat')
    rating_form = ServiceRatingForm(request.POST or None, prefix='rating')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'send_message' and chat_form.is_valid():
            message_obj = chat_form.save(commit=False)
            message_obj.request = service_request
            message_obj.sender = request.user
            message_obj.save()
            return redirect('nearservice:request-detail', request_id=service_request.id)

        if action == 'mark_completed' and is_provider and service_request.status == ServiceRequestStatus.ACCEPTED:
            service_request.status = ServiceRequestStatus.COMPLETED
            service_request.save(update_fields=['status'])
            messages.success(request, 'Service marked completed.')
            return redirect('nearservice:request-detail', request_id=service_request.id)

        if action == 'cancel_request' and is_customer and service_request.status in {ServiceRequestStatus.REQUESTED, ServiceRequestStatus.ACCEPTED}:
            service_request.status = ServiceRequestStatus.CANCELLED
            service_request.save(update_fields=['status'])
            messages.success(request, 'Service request cancelled.')
            return redirect('nearservice:request-detail', request_id=service_request.id)

        if action == 'submit_rating' and is_customer and service_request.status == ServiceRequestStatus.COMPLETED:
            if hasattr(service_request, 'rating'):
                messages.info(request, 'Provider already rated for this request.')
            elif rating_form.is_valid() and service_request.provider_id:
                rating_obj = rating_form.save(commit=False)
                rating_obj.request = service_request
                rating_obj.customer = request.user
                rating_obj.provider = service_request.provider
                rating_obj.save()
                service_request.provider.refresh_rating()
                messages.success(request, 'Rating submitted.')
            return redirect('nearservice:request-detail', request_id=service_request.id)

    can_rate = is_customer and service_request.status == ServiceRequestStatus.COMPLETED and not hasattr(service_request, 'rating')
    can_cancel = is_customer and service_request.status in {ServiceRequestStatus.REQUESTED, ServiceRequestStatus.ACCEPTED}

    return render(
        request,
        'nearservice/request_detail.html',
        {
            'service_request': service_request,
            'is_customer': is_customer,
            'is_provider': is_provider,
            'chat_form': chat_form,
            'rating_form': rating_form,
            'can_rate': can_rate,
            'can_cancel': can_cancel,
            'messages_history': service_request.messages.select_related('sender').all(),
        },
    )
