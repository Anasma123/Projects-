from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models.functions import Lower
from django.utils import timezone

from apps.locations.models import Country, District, Locality, State
from apps.roles.models import RoleChoices, UserRole

from .forms import OfferForm, ProductForm, ShopCategoryRequestForm, ShopChatForm, ShopForm, ShopRatingForm
from .models import CategoryRequestStatus, Offer, Product, Shop, ShopCategory, ShopCategoryRequest, ShopRating


def _int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def nearshop_dashboard(request):
    featured_shops = Shop.objects.select_related('owner', 'category', 'country', 'state', 'district', 'locality').filter(
        is_active=True,
        is_deleted=False,
    )[:6]
    active_offers = Offer.objects.select_related('shop').filter(valid_until__gte=timezone.now(), shop__is_active=True, shop__is_deleted=False)[:8]
    owner_shop = Shop.objects.filter(owner=request.user, is_deleted=False).first() if request.user.is_authenticated else None
    category_requests = (
        ShopCategoryRequest.objects.filter(requested_by=request.user).order_by('-created_at')[:5]
        if request.user.is_authenticated
        else []
    )
    return render(
        request,
        'nearshop/dashboard.html',
        {
            'featured_shops': featured_shops,
            'active_offers': active_offers,
            'owner_shop': owner_shop,
            'category_requests': category_requests,
        },
    )


def shop_list(request):
    shops = Shop.objects.select_related('owner', 'category', 'country', 'state', 'district', 'locality').filter(
        is_active=True,
        is_deleted=False,
    )
    category_id = _int_or_none(request.GET.get('category'))
    country_id = _int_or_none(request.GET.get('country'))
    state_id = _int_or_none(request.GET.get('state'))
    district_id = _int_or_none(request.GET.get('district'))
    locality_id = _int_or_none(request.GET.get('locality'))

    if category_id:
        shops = shops.filter(category_id=category_id)
    if country_id:
        shops = shops.filter(country_id=country_id)
    if state_id:
        shops = shops.filter(state_id=state_id)
    if district_id:
        shops = shops.filter(district_id=district_id)
    if locality_id:
        shops = shops.filter(locality_id=locality_id)

    countries = Country.objects.order_by(Lower('name'), 'name')
    category_options = ShopCategory.objects.filter(is_active=True).order_by('name')
    states = State.objects.filter(country_id=country_id).order_by(Lower('name'), 'name') if country_id else State.objects.none()
    districts = District.objects.filter(state_id=state_id).order_by(Lower('name'), 'name') if state_id else District.objects.none()
    localities = Locality.objects.filter(district_id=district_id).order_by(Lower('name'), 'name') if district_id else Locality.objects.none()
    return render(
        request,
        'nearshop/shop_list.html',
        {
            'shops': shops,
            'category_options': category_options,
            'selected_category': category_id,
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


def shop_detail(request, shop_id: int):
    shop = get_object_or_404(
        Shop.objects.select_related('owner', 'category', 'country', 'state', 'district', 'locality'),
        id=shop_id,
        is_deleted=False,
    )
    if not shop.is_active and (not request.user.is_authenticated or request.user.id != shop.owner_id):
        return HttpResponseForbidden('This shop is currently unavailable.')
    products = shop.products.filter(is_available=True, is_deleted=False)
    offers = shop.offers.filter(valid_until__gte=timezone.now())
    messages_history = shop.messages.select_related('sender').all()
    can_contact = request.user.is_authenticated and request.user != shop.owner

    chat_form = ShopChatForm(request.POST or None, prefix='chat')
    rating_form = ShopRatingForm(request.POST or None, prefix='rating')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'send_message':
            if not can_contact:
                return HttpResponseForbidden('Login required to contact shop owner.')
            if chat_form.is_valid():
                chat = chat_form.save(commit=False)
                chat.shop = shop
                chat.sender = request.user
                chat.save()
                messages.success(request, 'Message sent.')
                return redirect('nearshop:shop-detail', shop_id=shop.id)

        if action == 'submit_rating':
            if not can_contact:
                return HttpResponseForbidden('Login required to rate shops.')
            if rating_form.is_valid():
                rating_obj, _ = ShopRating.objects.update_or_create(
                    shop=shop,
                    user=request.user,
                    defaults={
                        'rating': rating_form.cleaned_data['rating'],
                        'review_text': rating_form.cleaned_data['review_text'],
                    },
                )
                shop.refresh_average_rating()
                messages.success(request, 'Rating submitted successfully.')
                return redirect('nearshop:shop-detail', shop_id=shop.id)

    user_rating = None
    if request.user.is_authenticated:
        user_rating = ShopRating.objects.filter(shop=shop, user=request.user).first()

    return render(
        request,
        'nearshop/shop_detail.html',
        {
            'shop': shop,
            'products': products,
            'offers': offers,
            'chat_form': chat_form,
            'rating_form': rating_form,
            'messages_history': messages_history,
            'can_contact': can_contact,
            'user_rating': user_rating,
        },
    )


@login_required
def register_shop(request):
    if Shop.objects.filter(owner=request.user, is_deleted=False).exists():
        messages.info(request, 'You already have a registered shop.')
        return redirect('nearshop:owner-dashboard')

    form = ShopForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        shop = form.save(commit=False)
        shop.owner = request.user
        if shop.category and not shop.shop_category:
            shop.shop_category = shop.category.name
        shop.save()
        UserRole.assign_role(request.user, RoleChoices.SHOP_OWNER)
        messages.success(request, 'Shop registered successfully.')
        return redirect('nearshop:owner-dashboard')

    return render(request, 'nearshop/register_shop.html', {'form': form})


@login_required
def owner_dashboard(request):
    shop = Shop.objects.filter(owner=request.user, is_deleted=False).first()
    if not shop:
        messages.info(request, 'Register a shop to access owner dashboard.')
        return redirect('nearshop:register-shop')

    products = shop.products.filter(is_deleted=False)
    offers = shop.offers.all()
    return render(
        request,
        'nearshop/owner_dashboard.html',
        {
            'shop': shop,
            'products': products,
            'offers': offers,
        },
    )


@login_required
def edit_shop(request):
    shop = Shop.objects.filter(owner=request.user, is_deleted=False).first()
    if not shop:
        return HttpResponseForbidden('Only shop owners can edit shop details.')

    form = ShopForm(request.POST or None, instance=shop)
    if request.method == 'POST' and form.is_valid():
        shop = form.save(commit=False)
        if shop.category:
            shop.shop_category = shop.category.name
        shop.save()
        messages.success(request, 'Shop details updated.')
        return redirect('nearshop:owner-dashboard')

    return render(request, 'nearshop/edit_shop.html', {'form': form, 'shop': shop})


@login_required
def product_management(request):
    shop = Shop.objects.filter(owner=request.user, is_deleted=False).first()
    if not shop:
        return HttpResponseForbidden('Only shop owners can manage products.')

    product_form = ProductForm(request.POST or None, prefix='product')
    offer_form = OfferForm(request.POST or None, prefix='offer')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add_product' and product_form.is_valid():
            product = product_form.save(commit=False)
            product.shop = shop
            product.save()
            messages.success(request, 'Product added successfully.')
            return redirect('nearshop:product-management')

        if action == 'add_offer' and offer_form.is_valid():
            offer = offer_form.save(commit=False)
            offer.shop = shop
            offer.save()
            messages.success(request, 'Offer created successfully.')
            return redirect('nearshop:product-management')

    products = shop.products.filter(is_deleted=False)
    offers = shop.offers.all()
    return render(
        request,
        'nearshop/product_management.html',
        {
            'shop': shop,
            'product_form': product_form,
            'offer_form': offer_form,
            'products': products,
            'offers': offers,
        },
    )


@login_required
def edit_product(request, product_id: int):
    product = get_object_or_404(Product.objects.select_related('shop'), id=product_id, is_deleted=False)
    if product.shop.owner_id != request.user.id:
        return HttpResponseForbidden('Unauthorized product edit.')

    form = ProductForm(request.POST or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Product updated successfully.')
        return redirect('nearshop:product-management')

    return render(request, 'nearshop/edit_product.html', {'form': form, 'product': product})


@login_required
def delete_product(request, product_id: int):
    if request.method != 'POST':
        return redirect('nearshop:product-management')

    product = get_object_or_404(Product.objects.select_related('shop'), id=product_id, is_deleted=False)
    if product.shop.owner_id != request.user.id:
        return HttpResponseForbidden('Unauthorized product deletion.')

    product.is_deleted = True
    product.deleted_at = timezone.now()
    product.is_available = False
    product.save(update_fields=['is_deleted', 'deleted_at', 'is_available'])
    messages.success(request, 'Product archived successfully.')
    return redirect('nearshop:product-management')


@login_required
def delete_offer(request, offer_id: int):
    if request.method != 'POST':
        return redirect('nearshop:product-management')

    offer = get_object_or_404(Offer.objects.select_related('shop'), id=offer_id)
    if offer.shop.owner_id != request.user.id:
        return HttpResponseForbidden('Unauthorized offer deletion.')

    offer.delete()
    messages.success(request, 'Offer deleted successfully.')
    return redirect('nearshop:product-management')


@login_required
def request_shop_category(request):
    form = ShopCategoryRequestForm(request.POST or None, initial={'requested_by': request.user})
    if request.method == 'POST' and form.is_valid():
        category_request = form.save(commit=False)
        category_request.requested_by = request.user
        category_request.status = CategoryRequestStatus.PENDING
        category_request.save()
        messages.success(request, 'Shop category request submitted successfully.')
        return redirect('nearshop:my-shop-category-requests')

    return render(request, 'nearshop/request_category.html', {'form': form})


@login_required
def my_shop_category_requests(request):
    requests_list = ShopCategoryRequest.objects.filter(requested_by=request.user).order_by('-created_at')
    return render(request, 'nearshop/my_category_requests.html', {'requests_list': requests_list})
