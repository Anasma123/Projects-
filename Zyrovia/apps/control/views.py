from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.db.models import Q
from django.db.models.functions import TruncDate
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from apps.locations.models import LocationRequest, LocationRequestStatus
from apps.nearride.models import CategoryRequestStatus as RideCategoryRequestStatus, DriverProfile, RideCategory, RideCategoryRequest, RideRequest
from apps.nearservice.models import CategoryRequestStatus, ServiceCategory, ServiceCategoryRequest, ServiceProvider, ServiceRequest
from apps.nearshop.models import CategoryRequestStatus as ShopCategoryRequestStatus, Product, Shop, ShopCategory, ShopCategoryRequest, ShopChat

from .decorators import staff_required
from .forms import CategoryManageForm, PlatformReportForm, RideCategoryManageForm, ShopCategoryManageForm
from .models import PlatformReport, ReportTargetType

User = get_user_model()


def _resolve_target(target_type: str, target_id: int):
    if target_type == ReportTargetType.DRIVER:
        return DriverProfile.objects.filter(id=target_id).first()
    if target_type == ReportTargetType.SHOP:
        return Shop.objects.filter(id=target_id, is_deleted=False).first()
    if target_type == ReportTargetType.SERVICE_PROVIDER:
        return ServiceProvider.objects.filter(id=target_id).first()
    return None


@staff_required
def dashboard(request):
    users_count = User.objects.filter(is_deleted=False).count()
    drivers_count = DriverProfile.objects.count()
    shops_count = Shop.objects.filter(is_deleted=False).count()
    service_providers_count = ServiceProvider.objects.count()
    rides_count = RideRequest.objects.filter(is_deleted=False).count()
    products_count = Product.objects.filter(is_deleted=False).count()
    service_requests_count = ServiceRequest.objects.filter(is_deleted=False).count()

    recent_items = []
    for user in User.objects.filter(is_deleted=False).order_by('-created_at')[:5]:
        recent_items.append({'label': f'New user: {user.full_name}', 'time': user.created_at})
    for ride in RideRequest.objects.filter(is_deleted=False).order_by('-created_at')[:5]:
        recent_items.append({'label': f'Ride request #{ride.id} ({ride.status})', 'time': ride.created_at})
    for req in ServiceRequest.objects.filter(is_deleted=False).order_by('-created_at')[:5]:
        recent_items.append({'label': f'Service request #{req.id} ({req.status})', 'time': req.created_at})
    for creq in ServiceCategoryRequest.objects.order_by('-created_at')[:5]:
        recent_items.append({'label': f'Category request: {creq.category_name} ({creq.status})', 'time': creq.created_at})
    for creq in RideCategoryRequest.objects.order_by('-created_at')[:5]:
        recent_items.append({'label': f'Ride category request: {creq.category_name} ({creq.status})', 'time': creq.created_at})
    for creq in ShopCategoryRequest.objects.order_by('-created_at')[:5]:
        recent_items.append({'label': f'Shop category request: {creq.category_name} ({creq.status})', 'time': creq.created_at})
    for lreq in LocationRequest.objects.order_by('-created_at')[:5]:
        recent_items.append({'label': f'Location request: {lreq.locality_name} ({lreq.status})', 'time': lreq.created_at})
    for report in PlatformReport.objects.order_by('-created_at')[:5]:
        recent_items.append({'label': f'Report #{report.id} on {report.target_type}', 'time': report.created_at})
    recent_items = sorted(recent_items, key=lambda item: item['time'], reverse=True)[:10]

    date_from = timezone.now() - timedelta(days=6)
    daily_new_users = list(
        User.objects.filter(created_at__gte=date_from, is_deleted=False)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )
    rides_per_day = list(
        RideRequest.objects.filter(created_at__gte=date_from, is_deleted=False)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )
    service_per_day = list(
        ServiceRequest.objects.filter(created_at__gte=date_from, is_deleted=False)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(total=Count('id'))
        .order_by('day')
    )
    shop_interactions = ShopChat.objects.count()

    users_map = {item['day']: item['total'] for item in daily_new_users}
    rides_map = {item['day']: item['total'] for item in rides_per_day}
    service_map = {item['day']: item['total'] for item in service_per_day}
    analytics_rows = []
    for offset in range(6, -1, -1):
        day = (timezone.now() - timedelta(days=offset)).date()
        analytics_rows.append(
            {
                'day': day,
                'users': users_map.get(day, 0),
                'rides': rides_map.get(day, 0),
                'services': service_map.get(day, 0),
            }
        )

    return render(
        request,
        'control/dashboard.html',
        {
            'users_count': users_count,
            'drivers_count': drivers_count,
            'shops_count': shops_count,
            'service_providers_count': service_providers_count,
            'rides_count': rides_count,
            'products_count': products_count,
            'service_requests_count': service_requests_count,
            'recent_items': recent_items,
            'analytics_rows': analytics_rows,
            'shop_interactions': shop_interactions,
        },
    )


@staff_required
def user_management(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        user = get_object_or_404(User, id=request.POST.get('user_id'))

        if action == 'toggle_active':
            user.is_active = not user.is_active
            user.save(update_fields=['is_active'])
            messages.success(request, f'User {user.full_name} status updated.')
        elif action == 'delete_user' and not user.is_superuser:
            user.is_active = False
            user.is_deleted = True
            user.save(update_fields=['is_active', 'is_deleted'])
            messages.success(request, 'User soft-deleted successfully.')
        return redirect('control:users')

    query = request.GET.get('q', '').strip()
    users = User.objects.filter(is_deleted=False).prefetch_related('assigned_roles')
    if query:
        users = users.filter(Q(full_name__icontains=query) | Q(phone_number__icontains=query))
    users = users.order_by('-created_at')

    return render(request, 'control/users.html', {'users': users, 'query': query})


@staff_required
def driver_management(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        driver = get_object_or_404(DriverProfile, id=request.POST.get('driver_id'))

        if action == 'toggle_verified':
            driver.is_verified = not driver.is_verified
            driver.save(update_fields=['is_verified'])
        elif action == 'toggle_blocked':
            driver.is_blocked = not driver.is_blocked
            if driver.is_blocked:
                driver.is_online = False
                driver.save(update_fields=['is_blocked', 'is_online'])
            else:
                driver.save(update_fields=['is_blocked'])
        messages.success(request, 'Driver updated successfully.')
        return redirect('control:drivers')

    drivers = DriverProfile.objects.select_related('user').order_by('user__full_name')
    return render(request, 'control/drivers.html', {'drivers': drivers})


@staff_required
def shop_management(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        shop = get_object_or_404(Shop, id=request.POST.get('shop_id'))

        if action == 'toggle_verified':
            shop.is_verified = not shop.is_verified
            shop.save(update_fields=['is_verified'])
        elif action == 'toggle_active':
            shop.is_active = not shop.is_active
            shop.save(update_fields=['is_active'])
        elif action == 'reject':
            shop.is_verified = False
            shop.is_active = False
            shop.save(update_fields=['is_verified', 'is_active'])
        messages.success(request, 'Shop updated successfully.')
        return redirect('control:shops')

    shops = Shop.objects.filter(is_deleted=False).select_related('owner').order_by('-created_at')
    return render(request, 'control/shops.html', {'shops': shops})


@staff_required
def provider_management(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        provider = get_object_or_404(ServiceProvider, id=request.POST.get('provider_id'))

        if action == 'toggle_verified':
            provider.is_verified = not provider.is_verified
            provider.save(update_fields=['is_verified'])
        elif action == 'toggle_active':
            provider.is_active = not provider.is_active
            if not provider.is_active:
                provider.is_available = False
                provider.save(update_fields=['is_active', 'is_available'])
            else:
                provider.save(update_fields=['is_active'])
        messages.success(request, 'Service provider updated successfully.')
        return redirect('control:providers')

    providers = ServiceProvider.objects.select_related('user', 'category').order_by('user__full_name')
    return render(request, 'control/providers.html', {'providers': providers})


@staff_required
def category_management(request):
    form = CategoryManageForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category created successfully.')
        return redirect('control:categories')

    categories = ServiceCategory.objects.all()
    return render(request, 'control/categories.html', {'form': form, 'categories': categories})


@staff_required
def category_edit(request, category_id: int):
    category = get_object_or_404(ServiceCategory, id=category_id)
    form = CategoryManageForm(request.POST or None, instance=category)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category updated successfully.')
        return redirect('control:categories')

    return render(request, 'control/category_edit.html', {'form': form, 'category': category})


@staff_required
def category_delete(request, category_id: int):
    if request.method != 'POST':
        return redirect('control:categories')

    category = get_object_or_404(ServiceCategory, id=category_id)
    has_links = category.providers.exists() or category.service_requests.exists()

    if has_links:
        messages.error(
            request,
            'Cannot delete category with linked providers or service requests. Deactivate it instead.',
        )
        return redirect('control:categories')

    category.delete()
    messages.success(request, 'Category deleted successfully.')
    return redirect('control:categories')


@staff_required
def category_request_management(request):
    if request.method == 'POST':
        category_request = get_object_or_404(ServiceCategoryRequest, id=request.POST.get('request_id'))
        action = request.POST.get('action')
        category_name = request.POST.get('category_name', '').strip()
        description = request.POST.get('description', '').strip()
        admin_note = request.POST.get('admin_note', '').strip()[:255]
        if category_request.status != CategoryRequestStatus.PENDING:
            messages.info(request, 'Request already reviewed.')
            return redirect('control:category-requests')

        if not category_name:
            messages.error(request, 'Category name is required.')
            return redirect('control:category-requests')

        category_request.category_name = category_name
        category_request.description = description

        if action == 'approve':
            existing = ServiceCategory.objects.filter(name__iexact=category_request.category_name).first()
            if existing:
                existing.is_active = True
                existing.description = existing.description or category_request.description
                existing.save(update_fields=['is_active', 'description'])
            else:
                ServiceCategory.objects.create(
                    name=category_request.category_name,
                    description=category_request.description,
                    is_active=True,
                )
            category_request.status = CategoryRequestStatus.APPROVED
            category_request.admin_note = admin_note
            category_request.reviewed_at = timezone.now()
            category_request.save(update_fields=['category_name', 'description', 'status', 'admin_note', 'reviewed_at'])
            messages.success(request, 'Category request approved.')

        elif action == 'reject':
            category_request.status = CategoryRequestStatus.REJECTED
            category_request.admin_note = admin_note
            category_request.reviewed_at = timezone.now()
            category_request.save(update_fields=['category_name', 'description', 'status', 'admin_note', 'reviewed_at'])
            messages.info(request, 'Category request rejected.')

        return redirect('control:category-requests')

    requests_list = ServiceCategoryRequest.objects.select_related('requested_by').order_by('-created_at')
    return render(request, 'control/category_requests.html', {'requests_list': requests_list})


@staff_required
def ride_category_management(request):
    form = RideCategoryManageForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Ride category created successfully.')
        return redirect('control:ride-categories')

    categories = RideCategory.objects.all()
    return render(request, 'control/ride_categories.html', {'form': form, 'categories': categories})


@staff_required
def ride_category_edit(request, category_id: int):
    category = get_object_or_404(RideCategory, id=category_id)
    form = RideCategoryManageForm(request.POST or None, instance=category)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Ride category updated successfully.')
        return redirect('control:ride-categories')

    return render(request, 'control/ride_category_edit.html', {'form': form, 'category': category})


@staff_required
def ride_category_delete(request, category_id: int):
    if request.method != 'POST':
        return redirect('control:ride-categories')

    category = get_object_or_404(RideCategory, id=category_id)
    if category.drivers.exists() or category.ride_requests.exists():
        category.is_active = False
        category.save(update_fields=['is_active'])
        messages.info(request, 'Ride category deactivated because it has linked records.')
    else:
        category.delete()
        messages.success(request, 'Ride category deleted successfully.')
    return redirect('control:ride-categories')


@staff_required
def ride_category_request_management(request):
    if request.method == 'POST':
        category_request = get_object_or_404(RideCategoryRequest, id=request.POST.get('request_id'))
        action = request.POST.get('action')
        category_name = request.POST.get('category_name', '').strip()
        description = request.POST.get('description', '').strip()
        admin_note = request.POST.get('admin_note', '').strip()[:255]
        if category_request.status != RideCategoryRequestStatus.PENDING:
            messages.info(request, 'Request already reviewed.')
            return redirect('control:ride-category-requests')
        if not category_name:
            messages.error(request, 'Category name is required.')
            return redirect('control:ride-category-requests')

        category_request.category_name = category_name
        category_request.description = description
        if action == 'approve':
            existing = RideCategory.objects.filter(name__iexact=category_name).first()
            if existing:
                existing.is_active = True
                existing.description = existing.description or description
                existing.save(update_fields=['is_active', 'description'])
            else:
                RideCategory.objects.create(name=category_name, description=description, is_active=True)
            category_request.status = RideCategoryRequestStatus.APPROVED
            category_request.admin_note = admin_note
            category_request.reviewed_at = timezone.now()
            category_request.save(update_fields=['category_name', 'description', 'status', 'admin_note', 'reviewed_at'])
            messages.success(request, 'Ride category request approved.')
        elif action == 'reject':
            category_request.status = RideCategoryRequestStatus.REJECTED
            category_request.admin_note = admin_note
            category_request.reviewed_at = timezone.now()
            category_request.save(update_fields=['category_name', 'description', 'status', 'admin_note', 'reviewed_at'])
            messages.info(request, 'Ride category request rejected.')
        return redirect('control:ride-category-requests')

    requests_list = RideCategoryRequest.objects.select_related('requested_by').order_by('-created_at')
    return render(request, 'control/ride_category_requests.html', {'requests_list': requests_list})


@staff_required
def shop_category_management(request):
    form = ShopCategoryManageForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Shop category created successfully.')
        return redirect('control:shop-categories')

    categories = ShopCategory.objects.all()
    return render(request, 'control/shop_categories.html', {'form': form, 'categories': categories})


@staff_required
def shop_category_edit(request, category_id: int):
    category = get_object_or_404(ShopCategory, id=category_id)
    form = ShopCategoryManageForm(request.POST or None, instance=category)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Shop category updated successfully.')
        return redirect('control:shop-categories')

    return render(request, 'control/shop_category_edit.html', {'form': form, 'category': category})


@staff_required
def shop_category_delete(request, category_id: int):
    if request.method != 'POST':
        return redirect('control:shop-categories')

    category = get_object_or_404(ShopCategory, id=category_id)
    if category.shops.exists():
        category.is_active = False
        category.save(update_fields=['is_active'])
        messages.info(request, 'Shop category deactivated because it has linked shops.')
    else:
        category.delete()
        messages.success(request, 'Shop category deleted successfully.')
    return redirect('control:shop-categories')


@staff_required
def shop_category_request_management(request):
    if request.method == 'POST':
        category_request = get_object_or_404(ShopCategoryRequest, id=request.POST.get('request_id'))
        action = request.POST.get('action')
        category_name = request.POST.get('category_name', '').strip()
        description = request.POST.get('description', '').strip()
        admin_note = request.POST.get('admin_note', '').strip()[:255]
        if category_request.status != ShopCategoryRequestStatus.PENDING:
            messages.info(request, 'Request already reviewed.')
            return redirect('control:shop-category-requests')
        if not category_name:
            messages.error(request, 'Category name is required.')
            return redirect('control:shop-category-requests')

        category_request.category_name = category_name
        category_request.description = description
        if action == 'approve':
            existing = ShopCategory.objects.filter(name__iexact=category_name).first()
            if existing:
                existing.is_active = True
                existing.description = existing.description or description
                existing.save(update_fields=['is_active', 'description'])
            else:
                ShopCategory.objects.create(name=category_name, description=description, is_active=True)
            category_request.status = ShopCategoryRequestStatus.APPROVED
            category_request.admin_note = admin_note
            category_request.reviewed_at = timezone.now()
            category_request.save(update_fields=['category_name', 'description', 'status', 'admin_note', 'reviewed_at'])
            messages.success(request, 'Shop category request approved.')
        elif action == 'reject':
            category_request.status = ShopCategoryRequestStatus.REJECTED
            category_request.admin_note = admin_note
            category_request.reviewed_at = timezone.now()
            category_request.save(update_fields=['category_name', 'description', 'status', 'admin_note', 'reviewed_at'])
            messages.info(request, 'Shop category request rejected.')
        return redirect('control:shop-category-requests')

    requests_list = ShopCategoryRequest.objects.select_related('requested_by').order_by('-created_at')
    return render(request, 'control/shop_category_requests.html', {'requests_list': requests_list})


@staff_required
def report_management(request):
    if request.method == 'POST':
        report = get_object_or_404(PlatformReport, id=request.POST.get('report_id'))
        report.is_resolved = True
        report.resolved_by = request.user
        report.resolved_at = timezone.now()
        report.resolution_note = request.POST.get('resolution_note', '').strip()[:255]
        report.save(update_fields=['is_resolved', 'resolved_by', 'resolved_at', 'resolution_note'])

        action = request.POST.get('action_taken')
        target = _resolve_target(report.target_type, report.target_id)
        if target:
            if action == 'disable_shop' and report.target_type == ReportTargetType.SHOP:
                target.is_active = False
                target.save(update_fields=['is_active'])
            elif action == 'block_driver' and report.target_type == ReportTargetType.DRIVER:
                target.is_blocked = True
                target.is_online = False
                target.save(update_fields=['is_blocked', 'is_online'])
            elif action == 'disable_provider' and report.target_type == ReportTargetType.SERVICE_PROVIDER:
                target.is_active = False
                target.is_available = False
                target.save(update_fields=['is_active', 'is_available'])

        messages.success(request, 'Report resolved.')
        return redirect('control:reports')

    reports = PlatformReport.objects.select_related('reporter', 'resolved_by').all()
    return render(request, 'control/reports.html', {'reports': reports})


@staff_required
def location_request_management(request):
    if request.method == 'POST':
        location_request = get_object_or_404(LocationRequest, id=request.POST.get('request_id'))
        action = request.POST.get('action')
        admin_note = request.POST.get('admin_note', '').strip()[:255]
        if location_request.status != LocationRequestStatus.PENDING:
            messages.info(request, 'Request already reviewed.')
            return redirect('control:location-requests')

        if action == 'approve':
            location_request.admin_note = admin_note
            location_request.save(update_fields=['admin_note'])
            location_request.apply_approval()
            messages.success(request, 'Location request approved and location hierarchy updated.')
        elif action == 'reject':
            location_request.status = LocationRequestStatus.REJECTED
            location_request.admin_note = admin_note
            location_request.reviewed_at = timezone.now()
            location_request.save(update_fields=['status', 'admin_note', 'reviewed_at'])
            messages.info(request, 'Location request rejected.')
        return redirect('control:location-requests')

    requests_list = LocationRequest.objects.select_related('requested_by').order_by('-created_at')
    return render(request, 'control/location_requests.html', {'requests_list': requests_list})


@login_required
def create_report(request):
    if request.method != 'POST':
        return HttpResponseForbidden('Invalid method.')

    form = PlatformReportForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Invalid report submission.')
        return redirect(request.POST.get('next_url') or 'core:dashboard')

    target_type = form.cleaned_data['target_type']
    target_id = form.cleaned_data['target_id']
    if _resolve_target(target_type, target_id) is None:
        messages.error(request, 'Invalid report target.')
        return redirect(request.POST.get('next_url') or 'core:dashboard')

    report = form.save(commit=False)
    report.reporter = request.user
    report.save()
    messages.success(request, 'Report submitted successfully. Admin will review it.')
    return redirect(request.POST.get('next_url') or 'core:dashboard')
