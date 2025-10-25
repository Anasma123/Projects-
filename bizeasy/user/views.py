"""
Main views module for the Bizeasy application.
Handles all business logic for user requests.
"""

# Standard library imports
import json
import datetime
from decimal import Decimal
from datetime import timedelta

# Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, F, Q, Case, When, Value, DecimalField, IntegerField, ExpressionWrapper, FloatField
from django.db.models.functions import Coalesce
import html
import re

from django.utils import timezone
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test

# Local imports
from .models import CustomUser, Category, SubCategory, Purchase, Product, Invoice, InvoiceItem, Discount
from .forms import CategoryForm, SubCategoryForm, PurchaseForm, PurchaseEditForm, InvoiceForm, InvoiceItemForm, StaffForm, sanitize_input



# ==============================================================================
# Authentication Views
# ==============================================================================

def login_view(request):
    """Handle user login requests."""
    if request.user.is_authenticated:
        user = request.user
        if hasattr(user, 'role'):
            role = getattr(user, 'role', 'staff')
        else:
            role = 'staff'  # default role
        return redirect_to_dashboard(role)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if hasattr(user, 'role'):
                role = getattr(user, 'role', 'staff')
            else:
                role = 'staff'  # default role
            return redirect_to_dashboard(role)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


def redirect_to_dashboard(role):
    """Redirect users to their appropriate dashboard based on role."""
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'staff':
        return redirect('staff_dashboard')
    elif role == 'owner':
        return redirect('owner_dashboard')
    else:
        return redirect('login')  # fallback


# ==============================================================================
# Dashboard Views
# ==============================================================================

@login_required
@user_passes_test(lambda u: hasattr(u, 'role') and getattr(u, 'role', '') == 'admin')
def admin_dashboard(request):
    """Render the admin dashboard."""
    return render(request, 'admin_dashboard.html')


@login_required
@user_passes_test(lambda u: hasattr(u, 'role') and getattr(u, 'role', '') != 'admin')
def staff_dashboard(request):
    """Render the staff dashboard."""
    return render(request, 'staff_dashboard.html')


@login_required
@user_passes_test(lambda u: hasattr(u, 'role') and getattr(u, 'role', '') == 'owner')
def owner_dashboard(request):
    """Render the owner dashboard with comprehensive business metrics."""
    # Calculate totals
    total_income = Invoice._default_manager.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    total_expenses = Purchase._default_manager.aggregate(Sum('total_rate'))['total_rate__sum'] or Decimal('0.00')
    
    # Ensure both are Decimal
    total_income = Decimal(str(total_income)) if total_income is not None else Decimal('0.00')
    total_expenses = Decimal(str(total_expenses)) if total_expenses is not None else Decimal('0.00')
    
    # Calculate net profit
    net_profit = total_income - total_expenses

    # Calculate percentage changes (previous period: same duration before current period)
    today = timezone.now().date()
    six_months_ago = today - timedelta(days=180)
    prev_income = Invoice._default_manager.filter(date__lt=six_months_ago).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    prev_expenses = Purchase._default_manager.filter(date__lt=six_months_ago).aggregate(Sum('total_rate'))['total_rate__sum'] or Decimal('0.00')
    
    # Ensure Decimal for previous period
    prev_income = Decimal(str(prev_income)) if prev_income is not None else Decimal('0.00')
    prev_expenses = Decimal(str(prev_expenses)) if prev_expenses is not None else Decimal('0.00')
    
    prev_profit = prev_income - prev_expenses

    # Calculate percentage changes
    income_change = (
        ((total_income - prev_income) / prev_income * Decimal('100.00'))
        if prev_income != Decimal('0.00') else Decimal('0.00')
    )
    expense_change = (
        ((total_expenses - prev_expenses) / prev_expenses * Decimal('100.00'))
        if prev_expenses != Decimal('0.00') else Decimal('0.00')
    )
    profit_change = (
        ((net_profit - prev_profit) / prev_profit * Decimal('100.00'))
        if prev_profit != Decimal('0.00') else Decimal('0.00')
    )

    # Chart data for last 6 months
    chart_labels = []
    income_data = []
    expense_data = []
    for i in range(5, -1, -1):
        month_start = (today - timedelta(days=30 * i)).replace(day=1)
        month_end = month_start + timedelta(days=30)
        chart_labels.append(month_start.strftime('%b %Y'))
        month_income = Invoice._default_manager.filter(date__range=(month_start, month_end)).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
        month_expense = Purchase._default_manager.filter(date__range=(month_start, month_end)).aggregate(Sum('total_rate'))['total_rate__sum'] or Decimal('0.00')
        income_data.append(float(Decimal(str(month_income))))
        expense_data.append(float(Decimal(str(month_expense))))

    # Category sales data
    category_labels = []
    category_data = []
    for category in Category._default_manager.all():
        category_labels.append(category.name)
        category_total = InvoiceItem._default_manager.filter(purchase__category=category).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
        category_data.append(float(Decimal(str(category_total))))

    # Recent transactions and purchases
    recent_transactions = Invoice._default_manager.order_by('-date')[:5]
    recent_purchases = Purchase._default_manager.order_by('-date')[:5]

    context = {
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'net_profit': float(net_profit),
        'income_change': float(income_change),
        'expense_change': float(expense_change),
        'profit_change': float(profit_change),
        'chart_labels': json.dumps(chart_labels),
        'income_data': json.dumps(income_data),
        'expense_data': json.dumps(expense_data),
        'category_labels': json.dumps(category_labels),
        'category_data': json.dumps(category_data),
        'recent_transactions': recent_transactions,
        'recent_purchases': recent_purchases,
    }

    return render(request, 'owner_dashboard.html', context)


# ==============================================================================
# Category Management Views
# ==============================================================================

def add_category(request):
    """Add a new category."""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_category')
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})


def edit_category(request, pk):
    """Edit an existing category."""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('list_category')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'edit_category.html', {'form': form})


def delete_category(request, pk):
    """Delete a category."""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('list_category')
    return render(request, 'delete_category.html', {'category': category})


# ==============================================================================
# Subcategory Management Views
# ==============================================================================

def add_subcategory(request):
    """Add a new subcategory."""
    if request.method == 'POST':
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_subcategory')
    else:
        form = SubCategoryForm()
    return render(request, 'add_subcategory.html', {'form': form})


def list_category(request):
    """List all categories with optional search."""
    query = request.GET.get('q')
    if query:
        categories = Category._default_manager.filter(name__icontains=query)
    else:
        categories = Category._default_manager.all()

    return render(request, 'list_category.html', {'categories': categories})


def list_subcategory(request):
    """List all subcategories with optional search."""
    query = request.GET.get('q')
    if query:
        subcategories = SubCategory._default_manager.filter(name__icontains=query)
    else:
        subcategories = SubCategory._default_manager.all()
    return render(request, 'list_subcategory.html', {'subcategories': subcategories})


def list_purchases(request):
    """List all non-deleted purchases with filtering and search capabilities - exclude stock update entries."""
    query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '')

    # Only show non-deleted purchases in the list that are NOT stock update entries
    purchases = Purchase._default_manager.filter(is_deleted=False).exclude(notes__icontains='Stock update entry')

    # Apply category filter
    if category_filter:
        purchases = purchases.filter(category_id=category_filter)

    # Apply search filter
    if query:
        purchases = purchases.filter(
            Q(product_name__icontains=query) |
            Q(notes__icontains=query) |
            Q(category__name__icontains=query) |
            Q(subcategory__name__icontains=query) |
            Q(date__icontains=query) |
            Q(expire_date__icontains=query)
        )

    # Calculate totals
    total_quantity = sum(purchase.quantity for purchase in purchases)
    total_value = sum(purchase.total_rate for purchase in purchases)

    categories = Category._default_manager.all()

    return render(request, 'list_purchase.html', {
        'purchases': purchases,
        'total_quantity': total_quantity,
        'total_value': total_value,
        'categories': categories,
        'query': query,
        'category_filter': category_filter,
    })


def edit_subcategory(request, pk):
    """Edit an existing subcategory."""
    subcategory = get_object_or_404(SubCategory, pk=pk)
    if request.method == 'POST':
        form = SubCategoryForm(request.POST, instance=subcategory)
        if form.is_valid():
            form.save()
            return redirect('list_subcategory')
    else:
        form = SubCategoryForm(instance=subcategory)
    return render(request, 'edit_subcategory.html', {'form': form})


def delete_subcategory(request, pk):
    """Delete a subcategory."""
    subcategory = get_object_or_404(SubCategory, pk=pk)
    if request.method == 'POST':
        subcategory.delete()
        return redirect('list_subcategory')
    return render(request, 'delete_subcategory.html', {'subcategory': subcategory})


def add_purchase(request):
    """Add a new purchase."""
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Purchase added.')
            return redirect('list_purchases')
    else:
        form = PurchaseForm()

    categories = Category._default_manager.all()
    subcategories = SubCategory._default_manager.all()
    subcategories_json = [
        {'id': str(getattr(s, 'id', '')), 'name': getattr(s, 'name', ''), 'category_id': str(getattr(getattr(s, 'category', None), 'id', '') if hasattr(s, 'category') else '')}
        for s in subcategories
    ]

    return render(request, 'add_purchase.html', {
        'form': form,
        'categories': categories,
        'subcategories': subcategories,
        'subcategories_json': subcategories_json
    })


def get_subcategories_by_category(request):
    """AJAX endpoint to get subcategories for a given category."""
    category_id = request.GET.get('category_id')
    subcategories = SubCategory._default_manager.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(subcategories), safe=False)


def edit_purchase(request, pk):
    """Edit an existing purchase."""
    purchase = get_object_or_404(Purchase, id=pk)
    
    if request.method == 'POST':
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            form.save()
            messages.success(request, 'Purchase updated successfully!')
            return redirect('list_purchases')
    else:
        form = PurchaseForm(instance=purchase)
    
    categories = Category._default_manager.all()
    subcategories = SubCategory._default_manager.all()
    subcategories_json = [
        {'id': str(getattr(s, 'id', '')), 'name': getattr(s, 'name', ''), 'category_id': str(getattr(getattr(s, 'category', None), 'id', '') if hasattr(s, 'category') else '')}
        for s in subcategories
    ]
    
    return render(request, 'edit_purchase.html', {
        'form': form,
        'purchase': purchase,
        'categories': categories,
        'subcategories': subcategories,
        'subcategories_json': subcategories_json
    })


def delete_purchase(request, pk):
    """Delete a purchase (soft delete or hard delete based on references)."""
    purchase = get_object_or_404(Purchase, pk=pk)
    
    # Check if the purchase is referenced by any invoice items
    if InvoiceItem._default_manager.filter(purchase=purchase).exists():
        # If referenced in invoices, we can only soft delete
        if request.method == 'POST':
            purchase_name = purchase.product_name
            purchase.delete()  # This will soft delete
            messages.success(request, f'Purchase "{purchase_name}" has been removed from active lists but preserved in history.')
            # Check where the user came from to determine redirect
            referer = request.META.get('HTTP_REFERER', '')
            if 'list_purchases' in referer:
                return redirect('list_purchases')
            else:
                return redirect('purchase_history')
        return render(request, 'delete_purchase.html', {'purchase': purchase})
    else:
        # If not referenced, we can hard delete
        if request.method == 'POST':
            purchase_name = purchase.product_name
            purchase.hard_delete()  # This will actually delete from database
            messages.success(request, f'Purchase "{purchase_name}" deleted permanently.')
            # Check where the user came from to determine redirect
            referer = request.META.get('HTTP_REFERER', '')
            if 'list_purchases' in referer:
                return redirect('list_purchases')
            else:
                return redirect('purchase_history')
        return render(request, 'delete_purchase.html', {'purchase': purchase})


# ==============================================================================
# Product Management Views
# ==============================================================================

def list_products_staff(request):
    """List products for staff users."""
    # Base queryset with related objects to avoid N+1 queries
    # Only show non-deleted purchases that are NOT stock update entries
    purchases = Purchase._default_manager.select_related('category', 'subcategory').filter(is_deleted=False).exclude(notes__icontains='Stock update entry')

    # Search filter
    q = request.GET.get('q', '').strip()
    if q:
        purchases = purchases.filter(
            Q(product_name__icontains=q) |
            Q(category__name__icontains=q) |
            Q(subcategory__name__icontains=q)
        )

    # Annotate final_price and discount_percentage
    purchases = purchases.annotate(
        final_price=Case(
            When(sale_rate__isnull=False, then='sale_rate'),
            default='mrp',
            output_field=FloatField()
        ),
        discount_percentage=Case(
            When(sale_rate__isnull=False, mrp__gt=0, then=ExpressionWrapper(
                ((F('mrp') - F('sale_rate')) / F('mrp')) * 100,
                output_field=FloatField()
            )),
            default=Value(0),
            output_field=FloatField()
        )
    ).order_by('-date')

    context = {
        'purchases': purchases,
        'search_query': q,
    }
    return render(request, 'list_products_staff.html', context)


@login_required
def list_products(request):
    """List products for authenticated users."""
    # Base queryset with related objects to avoid N+1 queries
    # Only show non-deleted purchases that are NOT stock update entries
    purchases = Purchase._default_manager.select_related('category', 'subcategory').filter(is_deleted=False).exclude(notes__icontains='Stock update entry')

    # Search filter
    q = request.GET.get('q', '').strip()
    if q:
        purchases = purchases.filter(
            Q(product_name__icontains=q) |
            Q(category__name__icontains=q) |
            Q(subcategory__name__icontains=q)
        )

    # Annotate final_price and discount_percentage
    purchases = purchases.annotate(
        final_price=Case(
            When(sale_rate__isnull=False, then='sale_rate'),
            default='mrp',
            output_field=FloatField()
        ),
        discount_percentage=Case(
            When(sale_rate__isnull=False, mrp__gt=0, then=ExpressionWrapper(
                ((F('mrp') - F('sale_rate')) / F('mrp')) * 100,
                output_field=FloatField()
            )),
            default=Value(0),
            output_field=FloatField()
        )
    ).order_by('-date')

    context = {
        'purchases': purchases,
        'search_query': q,
    }
    return render(request, 'list_products.html', context)


@login_required
def view_discount(request):
    """View all purchases with discounts. Accessible by both owner and staff, with different permissions."""
    # Get filter parameters from request
    status_filter = request.GET.get('status', '')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    
    # Get all purchases that have associated products with discounts
    # This includes both current discounts and upcoming discounts
    # First get all purchases with MRP
    all_purchases = Purchase._default_manager.select_related('category', 'subcategory').filter(
        mrp__isnull=False,
        mrp__gt=0
    ).order_by('-date')
    
    # Filter to only show products with discounts (either existing sale_rate discounts or discount records)
    purchases = []
    for purchase in all_purchases:
        # Check if this purchase has an associated product with a discount record
        try:
            product = Product._default_manager.get(purchase=purchase)
            # If product has any discount records, include this purchase
            if Discount._default_manager.filter(product=product).exists():
                purchases.append(purchase)
                continue
        except Exception:
            # If no product exists, check for sale_rate based discounts
            pass
        
        # Also include purchases with existing sale_rate discounts
        if (purchase.sale_rate is not None and 
            purchase.mrp is not None and 
            abs(float(purchase.sale_rate or 0) - float(purchase.mrp or 0)) > 0.01):
            purchases.append(purchase)
    
    # For further processing, we need to work with the original queryset
    # So we'll process the filtering in Python rather than in the database
    discounted_purchases = []
    total_discount = 0
    count = 0
    
    print(f"Found {len(purchases)} purchases with discounts")
    
    # Get today's date for filtering
    today = timezone.now().date()
    
    for purchase in purchases:
        # Initialize default values for all purchases
        if not hasattr(purchase, 'discount_percent'):
            purchase.discount_percent = 0
        if not hasattr(purchase, 'discount_percentage'):
            purchase.discount_percentage = 0
        if not hasattr(purchase, 'start_date'):
            purchase.start_date = None
        if not hasattr(purchase, 'end_date'):
            purchase.end_date = None
        if not hasattr(purchase, 'is_active'):
            purchase.is_active = False
        if not hasattr(purchase, 'final_price'):
            purchase.final_price = purchase.mrp
        if not hasattr(purchase, 'status'):
            purchase.status = None
        
        # Get the Product associated with this Purchase
        try:
            product = Product._default_manager.get(purchase=purchase)
            print(f"Found product: {product.name} for purchase: {purchase.product_name}")
            
            # Get discount info for that product
            discount_info = product.get_discount_info()
            print(f"Discount info for {product.name}: {discount_info}")
            
            # Also get the actual discount object to access status
            try:
                discount_obj = Discount._default_manager.get(product=product)
                # Add discount info to purchase object for template use
                purchase.discount_percent = discount_info['percent']
                purchase.discount_percentage = discount_info['percent']  # For template compatibility
                purchase.start_date = discount_info['start_date']
                purchase.end_date = discount_info['end_date']
                purchase.is_active = discount_info['is_active']
                purchase.final_price = product.get_final_price() or purchase.mrp
                purchase.status = discount_obj.status  # Add status to purchase object
                print(f"Set purchase start_date: {purchase.start_date}, end_date: {purchase.end_date}, status: {purchase.status}")
                
                # Apply status filter if specified
                if status_filter:
                    # Determine actual status based on dates if needed
                    today = timezone.now().date()
                    actual_status = discount_obj.status
                    
                    # If status is not explicitly set or we need to override based on dates
                    if discount_obj.start_date and discount_obj.end_date:
                        if today < discount_obj.start_date:
                            actual_status = 'pending'
                        elif today > discount_obj.end_date:
                            actual_status = 'rejected'  # Finished/expired
                        else:
                            actual_status = 'active'
                    
                    # Handle the "finished" filter specifically
                    if status_filter == 'finished':
                        # For finished, we check if status is 'rejected' or if end_date has passed
                        if not (actual_status == 'rejected' or (discount_obj.end_date and discount_obj.end_date < today)):
                            continue  # Skip this purchase if it doesn't match the finished criteria
                    elif actual_status != status_filter:
                        continue  # Skip this purchase if it doesn't match the status filter
                else:
                    # If no status filter is specified, only show active and pending discounts by default
                    today = timezone.now().date()
                    actual_status = discount_obj.status
                    
                    # If status is not explicitly set or we need to override based on dates
                    if discount_obj.start_date and discount_obj.end_date:
                        if today < discount_obj.start_date:
                            actual_status = 'pending'
                        elif today > discount_obj.end_date:
                            actual_status = 'rejected'  # Finished/expired
                        else:
                            actual_status = 'active'
                    
                    # Only show active and pending discounts
                    if actual_status not in ['active', 'pending']:
                        continue
                
                # Apply date filters if specified
                if from_date and to_date:
                    try:
                        from_date_obj = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
                        to_date_obj = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()
                        # Check if either start or end date falls within the range
                        start_in_range = discount_obj.start_date and from_date_obj <= discount_obj.start_date <= to_date_obj
                        end_in_range = discount_obj.end_date and from_date_obj <= discount_obj.end_date <= to_date_obj
                        if not (start_in_range or end_in_range):
                            continue  # Skip if neither start nor end date falls within range
                    except ValueError:
                        pass  # Invalid date format, ignore date filter
                elif from_date:
                    try:
                        from_date_obj = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
                        # Check if both dates are before the from_date
                        if (discount_obj.start_date and discount_obj.start_date < from_date_obj and 
                            discount_obj.end_date and discount_obj.end_date < from_date_obj):
                            continue  # Skip if both dates are before the from_date
                    except ValueError:
                        pass  # Invalid date format, ignore date filter
                elif to_date:
                    try:
                        to_date_obj = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()
                        # Check if both dates are after the to_date
                        if (discount_obj.start_date and discount_obj.start_date > to_date_obj and 
                            discount_obj.end_date and discount_obj.end_date > to_date_obj):
                            continue  # Skip if both dates are after the to_date
                    except ValueError:
                        pass  # Invalid date format, ignore date filter
                
                discounted_purchases.append(purchase)
                total_discount += discount_info['percent']
                count += 1
                print(f"Added discounted purchase: {purchase.product_name} with {discount_info['percent']}% discount, status: {purchase.status}")
            except Exception as e:
                print(f"Exception getting discount object: {e}")
                # No discount object exists, but there might be a sale_rate discount
                if discount_info['percent'] > 0:
                    # Add discount info to purchase object for template use
                    purchase.discount_percent = discount_info['percent']
                    purchase.discount_percentage = discount_info['percent']  # For template compatibility
                    purchase.start_date = discount_info['start_date']
                    purchase.end_date = discount_info['end_date']
                    purchase.is_active = discount_info['is_active']
                    purchase.final_price = product.get_final_price() or purchase.mrp
                    # Set status based on dates for discounts without Discount object
                    if purchase.start_date and purchase.end_date:
                        today = timezone.now().date()
                        if today < purchase.start_date:
                            purchase.status = 'pending'
                        elif today > purchase.end_date:
                            purchase.status = 'finished'
                        else:
                            purchase.status = 'active'
                    else:
                        purchase.status = 'active' if discount_info['is_active'] else 'pending'
                    print(f"Set purchase start_date: {purchase.start_date}, end_date: {purchase.end_date}, status: {purchase.status}")
                    
                    # Apply status filter if specified
                    if status_filter:
                        # For products without Discount object, we determine status based on dates
                        today = timezone.now().date()
                        product_status = 'pending'  # Default
                        
                        if purchase.start_date and purchase.end_date:
                            if today < purchase.start_date:
                                product_status = 'pending'
                            elif today > purchase.end_date:
                                product_status = 'finished'
                            else:
                                product_status = 'active'
                        
                        # Handle the "finished" filter specifically
                        if status_filter == 'finished':
                            if product_status != 'finished':
                                continue  # Skip if not finished
                        elif product_status != status_filter:
                            continue  # Skip if status doesn't match
                    else:
                        # If no status filter is specified, only show active and pending discounts by default
                        today = timezone.now().date()
                        product_status = 'pending'  # Default
                        
                        if purchase.start_date and purchase.end_date:
                            if today < purchase.start_date:
                                product_status = 'pending'
                            elif today > purchase.end_date:
                                product_status = 'finished'
                            else:
                                product_status = 'active'
                        
                        # Only show active and pending discounts
                        if product_status not in ['active', 'pending']:
                            continue
                    
                    # Apply date filters if specified
                    if from_date and to_date:
                        try:
                            from_date_obj = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
                            to_date_obj = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()
                            # Check if either start or end date falls within the range
                            start_in_range = purchase.start_date and from_date_obj <= purchase.start_date <= to_date_obj
                            end_in_range = purchase.end_date and from_date_obj <= purchase.end_date <= to_date_obj
                            if not (start_in_range or end_in_range):
                                continue  # Skip if neither start nor end date falls within range
                        except ValueError:
                            pass  # Invalid date format, ignore date filter
                    elif from_date:
                        try:
                            from_date_obj = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
                            # Check if both dates are before the from_date
                            if (purchase.start_date and purchase.start_date < from_date_obj and 
                                purchase.end_date and purchase.end_date < from_date_obj):
                                continue  # Skip if both dates are before the from_date
                        except ValueError:
                            pass  # Invalid date format, ignore date filter
                    elif to_date:
                        try:
                            to_date_obj = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()
                            # Check if both dates are after the to_date
                            if (purchase.start_date and purchase.start_date > to_date_obj and 
                                purchase.end_date and purchase.end_date > to_date_obj):
                                continue  # Skip if both dates are after the to_date
                        except ValueError:
                            pass  # Invalid date format, ignore date filter
                    
                    discounted_purchases.append(purchase)
                    total_discount += discount_info['percent']
                    count += 1
                    print(f"Added discounted purchase: {purchase.product_name} with {discount_info['percent']}% discount")
                # If there's no discount, we don't add the purchase to the list
        except Exception as e:
            # Handle any exceptions
            if "Product matching query does not exist" in str(e):
                # This is expected for some purchases, just log it at a lower level
                print(f"Info: Purchase {purchase.product_name} does not have an associated Product object.")
            else:
                print(f"Error processing purchase {purchase.product_name}: {e}")
            # Don't add purchases without products to the list

    # Calculate average discount (only for purchases with discounts)
    discounted_count = sum(1 for p in discounted_purchases if getattr(p, 'discount_percentage', 0) > 0)
    discounted_total = sum(getattr(p, 'discount_percentage', 0) for p in discounted_purchases)
    average_discount = discounted_total / discounted_count if discounted_count > 0 else 0
    print(f"Total discounted purchases: {discounted_count}, Average discount: {average_discount}")

    # Determine user role for template
    user_role = getattr(request.user, 'role', 'staff')
    can_edit = user_role == 'owner'

    context = {
        'purchases': discounted_purchases,
        'average_discount': average_discount,
        'can_edit': can_edit,
        'user_role': user_role,
        'status_filter': status_filter,
        'from_date': from_date,
        'to_date': to_date
    }
    return render(request, 'view_discount.html', context)


@login_required
def delete_discount(request, purchase_id):
    """Remove discount from a purchase item."""
    purchase = get_object_or_404(Purchase, id=purchase_id)
    
    # Verify that the purchase actually has a discount
    has_discount = (purchase.sale_rate is not None and 
                   purchase.mrp is not None and 
                   purchase.mrp > 0 and 
                   abs(float(purchase.sale_rate or 0) - float(purchase.mrp or 0)) > 0.01)
    
    if not has_discount:
        messages.error(request, f'Product "{purchase.product_name}" does not have an active discount.')
        return redirect('view_discount')
    
    if request.method == 'POST':
        # Remove the discount by setting sale_rate back to MRP (no discount)
        purchase.sale_rate = float(purchase.mrp)
        purchase.save()
        
        # Also remove the discount record from the Discount model if it exists
        try:
            product = Product._default_manager.get(purchase=purchase)
            # Delete all discounts associated with this product
            Discount._default_manager.filter(product=product).delete()
        except Exception as e:
            # If there's no product or discount record, that's fine
            print(f"Info: No discount record found for product {purchase.product_name}: {e}")
            pass
        
        messages.success(request, f'Discount removed successfully from "{purchase.product_name}". Sale rate reverted to MRP: ₹{purchase.mrp}')
        return redirect('view_discount')
    
    return render(request, 'delete_discount.html', {'purchase': purchase})


# ==============================================================================
# Report Management Views
# ==============================================================================

def stock_report(request):
    """Generate stock report with filtering capabilities - exclude stock update entries."""
    # Get date range filters from request
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('q', '').strip()
    
    # Base purchase queryset (only non-deleted purchases that are NOT stock update entries)
    purchases = Purchase._default_manager.filter(is_deleted=False).exclude(notes__icontains='Stock update entry')
    
    # Apply date filters
    if from_date:
        purchases = purchases.filter(date__gte=from_date)
    if to_date:
        purchases = purchases.filter(date__lte=to_date)
    
    # Apply category filter
    if category_filter:
        purchases = purchases.filter(category_id=category_filter)
    
    # Apply search filter
    if search_query:
        purchases = purchases.filter(
            Q(product_name__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(subcategory__name__icontains=search_query)
        )
    
    # Annotate with sales data
    report = purchases.annotate(
        total_purchased=F("quantity"),
        total_sold=Coalesce(
            Sum("invoiceitem__quantity", filter=Q(invoiceitem__invoice__date__range=[from_date, to_date]) if from_date and to_date else Q()),
            Value(0),
            output_field=IntegerField()
        ),
    ).annotate(
        balance=F("total_purchased") - F("total_sold")
    ).order_by('-date')
    
    categories = Category._default_manager.all()
    
    context = {
        "report": report,
        "categories": categories,
        "from_date": from_date or '',
        "to_date": to_date or '',
        "category_filter": category_filter,
        "search_query": search_query,
    }
    return render(request, "stock_report.html", context)


def purchase_history(request):
    """View purchase history with filtering and search - show all purchases including deleted ones."""
    # Get filters from request
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('q', '').strip()
    session_filter = request.GET.get('session', 'all')  # 'all', 'active', or 'deleted'
    
    # Base purchase queryset - show all purchases
    if session_filter == 'active':
        purchases = Purchase._default_manager.filter(is_deleted=False).exclude(notes__icontains='Stock update entry').order_by('-date')
    elif session_filter == 'deleted':
        purchases = Purchase._default_manager.filter(is_deleted=True).exclude(notes__icontains='Stock update entry').order_by('-date')
    else:
        purchases = Purchase._default_manager.exclude(notes__icontains='Stock update entry').order_by('-date')
    
    # Apply date filters
    if from_date:
        purchases = purchases.filter(date__gte=from_date)
    if to_date:
        purchases = purchases.filter(date__lte=to_date)
    
    # Apply category filter
    if category_filter:
        purchases = purchases.filter(category_id=category_filter)
    
    # Apply search filter
    if search_query:
        purchases = purchases.filter(
            Q(product_name__icontains=search_query) |
            Q(category__name__icontains=search_query) |
            Q(subcategory__name__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # For each purchase in history, we want to show the original quantity
    # We'll calculate this by adding up all the quantities sold from this purchase
    purchase_data = []
    for purchase in purchases:
        # Calculate total sold for this purchase
        total_sold = InvoiceItem._default_manager.filter(purchase=purchase).aggregate(
            total_sold=Coalesce(Sum('quantity'), Value(0))
        )['total_sold']
        
        # Original quantity is current quantity + total sold
        original_quantity = purchase.quantity + total_sold
        
        # Add to our data list
        purchase_data.append({
            'purchase': purchase,
            'original_quantity': original_quantity
        })
    
    categories = Category._default_manager.all()
    
    context = {
        "purchase_data": purchase_data,
        "categories": categories,
        "from_date": from_date or '',
        "to_date": to_date or '',
        "category_filter": category_filter,
        "search_query": search_query,
        "session_filter": session_filter,
    }
    return render(request, "purchase_history.html", context)


def shop_report(request):
    """Generate comprehensive shop report with date filtering capabilities."""
    today = timezone.now().date()
    
    # Get date range filters from request
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    # Base invoice queryset for filtering
    invoice_qs = Invoice._default_manager.all()
    if from_date and to_date:
        invoice_qs = invoice_qs.filter(date__range=[from_date, to_date])
    elif from_date:
        invoice_qs = invoice_qs.filter(date__gte=from_date)
    elif to_date:
        invoice_qs = invoice_qs.filter(date__lte=to_date)

    # --- Sales Summary ---
    sales_summary = invoice_qs.aggregate(
        total_sales=Coalesce(Sum("total"), Value(Decimal(0)), output_field=DecimalField()),
        total_discount=Coalesce(Sum("discount_amount"), Value(Decimal(0)), output_field=DecimalField()),
    )
    
    # Calculate net revenue
    sales_summary['net_revenue'] = sales_summary['total_sales'] - sales_summary['total_discount']

    # --- Product-wise Sales Report with Profit Calculation ---
    product_sales_query = InvoiceItem._default_manager.filter(purchase__is_deleted=False).values(
        "purchase__product_name", 
        "purchase__category__name",
        "purchase__category__id",
        "purchase__subcategory__name",
        "purchase__subcategory__id",
        "purchase__product_rate",  # Cost price
        "purchase__sale_rate"      # Selling price
    )
    
    # Apply date filter to InvoiceItem via invoice__date
    if from_date and to_date:
        product_sales_query = product_sales_query.filter(invoice__date__range=[from_date, to_date])
    elif from_date:
        product_sales_query = product_sales_query.filter(invoice__date__gte=from_date)
    elif to_date:
        product_sales_query = product_sales_query.filter(invoice__date__lte=to_date)
    
    product_sales = (
        product_sales_query.annotate(
            total_qty=Coalesce(Sum("quantity"), Value(0), output_field=IntegerField()),
            total_amount=Coalesce(Sum("total"), Value(Decimal(0)), output_field=DecimalField()),
            total_cost=Coalesce(Sum(F("quantity") * F("purchase__product_rate")), Value(Decimal(0)), output_field=DecimalField()),
            profit=Coalesce(Sum("total"), Value(Decimal(0)), output_field=DecimalField()) - 
                   Coalesce(Sum(F("quantity") * F("purchase__product_rate")), Value(Decimal(0)), output_field=DecimalField())
        )
        .order_by("-profit")  # Sort by annotated profit field
    )
    
    # Calculate additional metrics for each product
    for product in product_sales:
        if product['total_qty'] > 0:
            product['avg_price'] = product['total_amount'] / product['total_qty']
            product['profit_per_unit'] = product['profit'] / product['total_qty']
        else:
            product['avg_price'] = Decimal(0)
            product['profit_per_unit'] = Decimal(0)

    # --- Category-wise Sales Report with Profit ---
    category_sales_query = InvoiceItem._default_manager.filter(purchase__is_deleted=False).values("purchase__category__name", "purchase__category__id")
    
    # Apply date filter to InvoiceItem via invoice__date
    if from_date and to_date:
        category_sales_query = category_sales_query.filter(invoice__date__range=[from_date, to_date])
    elif from_date:
        category_sales_query = category_sales_query.filter(invoice__date__gte=from_date)
    elif to_date:
        category_sales_query = category_sales_query.filter(invoice__date__lte=to_date)
    
    category_sales = (
        category_sales_query.annotate(
            total_qty=Coalesce(Sum("quantity"), Value(0), output_field=IntegerField()),
            total_amount=Coalesce(Sum("total"), Value(Decimal(0)), output_field=DecimalField()),
            total_cost=Coalesce(Sum(F("quantity") * F("purchase__product_rate")), Value(Decimal(0)), output_field=DecimalField()),
            profit=Coalesce(Sum("total"), Value(Decimal(0)), output_field=DecimalField()) - 
                   Coalesce(Sum(F("quantity") * F("purchase__product_rate")), Value(Decimal(0)), output_field=DecimalField())
        )
        .order_by("-profit")  # Sort by annotated profit field
    )
    
    # Calculate percentage of total sales for each category
    for category in category_sales:
        if sales_summary['total_sales'] > 0:
            category['percentage'] = (category['total_amount'] / sales_summary['total_sales']) * 100
        else:
            category['percentage'] = 0

    # --- Subcategory-wise Sales Report with Profit ---
    subcategory_sales_query = InvoiceItem._default_manager.filter(purchase__is_deleted=False).values(
        "purchase__category__name",
        "purchase__category__id",
        "purchase__subcategory__name",
        "purchase__subcategory__id"
    )
    
    # Apply date filter to InvoiceItem via invoice__date
    if from_date and to_date:
        subcategory_sales_query = subcategory_sales_query.filter(invoice__date__range=[from_date, to_date])
    elif from_date:
        subcategory_sales_query = subcategory_sales_query.filter(invoice__date__gte=from_date)
    elif to_date:
        subcategory_sales_query = subcategory_sales_query.filter(invoice__date__lte=to_date)
    
    subcategory_sales = (
        subcategory_sales_query.annotate(
            total_qty=Coalesce(Sum("quantity"), Value(0), output_field=IntegerField()),
            total_amount=Coalesce(Sum("total"), Value(Decimal(0)), output_field=DecimalField()),
            total_cost=Coalesce(Sum(F("quantity") * F("purchase__product_rate")), Value(Decimal(0)), output_field=DecimalField()),
            profit=Coalesce(Sum("total"), Value(Decimal(0)), output_field=DecimalField()) - 
                   Coalesce(Sum(F("quantity") * F("purchase__product_rate")), Value(Decimal(0)), output_field=DecimalField())
        )
        .order_by("-profit")  # Sort by annotated profit field
    )

    # --- Billing List ---
    invoices = invoice_qs.annotate(
        net_amount=F("total") - F("discount_amount")
    ).order_by("-total")  # Sort by total amount

    # --- Stock Report ---
    # Build filter for InvoiceItem related to Purchase (only non-deleted purchases that are NOT stock update entries)
    if from_date and to_date:
        stock_data = Purchase._default_manager.filter(is_deleted=False).exclude(notes__icontains='Stock update entry').annotate(
            total_purchased=F("quantity"),
            total_sold=Coalesce(
                Sum("invoiceitem__quantity", filter=Q(invoiceitem__invoice__date__range=[from_date, to_date])),
                Value(0),
                output_field=IntegerField()
            ),
        ).annotate(
            balance=F("total_purchased") - F("total_sold")
        ).order_by("balance")
    elif from_date:
        stock_data = Purchase._default_manager.filter(is_deleted=False).exclude(notes__icontains='Stock update entry').annotate(
            total_purchased=F("quantity"),
            total_sold=Coalesce(
                Sum("invoiceitem__quantity", filter=Q(invoiceitem__invoice__date__gte=from_date)),
                Value(0),
                output_field=IntegerField()
            ),
        ).annotate(
            balance=F("total_purchased") - F("total_sold")
        ).order_by("balance")
    elif to_date:
        stock_data = Purchase._default_manager.filter(is_deleted=False).exclude(notes__icontains='Stock update entry').annotate(
            total_purchased=F("quantity"),
            total_sold=Coalesce(
                Sum("invoiceitem__quantity", filter=Q(invoiceitem__invoice__date__lte=to_date)),
                Value(0),
                output_field=IntegerField()
            ),
        ).annotate(
            balance=F("total_purchased") - F("total_sold")
        ).order_by("balance")
    else:
        # No filter - show all non-deleted purchases that are NOT stock update entries
        stock_data = Purchase._default_manager.filter(is_deleted=False).exclude(notes__icontains='Stock update entry').annotate(
            total_purchased=F("quantity"),
            total_sold=Coalesce(Sum("invoiceitem__quantity"), Value(0), output_field=IntegerField()),
        ).annotate(
            balance=F("total_purchased") - F("total_sold")
        ).order_by("balance")

    # --- Expired Purchase Report ---
    # Get all purchases that have an expire_date (regardless of when they expire)
    # Use select_related to optimize database queries
    # Only show non-deleted purchases that are NOT stock update entries
    expired_purchases_raw = Purchase._default_manager.filter(
        expire_date__isnull=False,
        is_deleted=False
    ).exclude(notes__icontains='Stock update entry').select_related('category', 'subcategory').order_by('expire_date')
    
    # Calculate days to expiry for each purchase using current date
    expired_purchases = []
    current_date = timezone.now().date()
    for purchase in expired_purchases_raw:
        purchase_dict = {
            'id': purchase.pk,
            'product_name': purchase.product_name,
            'category': purchase.category,
            'subcategory': purchase.subcategory,
            'date': purchase.date,
            'expire_date': purchase.expire_date,
            'quantity': purchase.quantity,
            'product_rate': purchase.product_rate,
            'total_rate': purchase.total_rate,
            'mrp': purchase.mrp,
            'notes': purchase.notes,
            'change_price': purchase.change_price,
            'sale_rate': purchase.sale_rate,
            'is_deleted': purchase.is_deleted,
        }
        # Calculate days to expiry as difference between expire_date and current_date
        if purchase.expire_date:
            purchase_dict['days_to_expiry'] = (purchase.expire_date - current_date).days
        else:
            purchase_dict['days_to_expiry'] = None
        expired_purchases.append(purchase_dict)

    # --- Staff Status Report ---
    staff_users = CustomUser.objects.filter(role='staff')

    # --- Additional data for enhanced report ---
    # Top selling products (top 5)
    top_selling = list(product_sales[:5])
    
    # Highest profit products (top 5)
    high_profit_products = sorted(
        [p for p in product_sales if p['profit'] > 0], 
        key=lambda x: x['profit'], 
        reverse=True
    )[:5]
    
    # Low profit products (bottom 5)
    low_profit_products = sorted(
        [p for p in product_sales if p['profit'] > 0], 
        key=lambda x: x['profit']
    )[:5]
    
    # Low stock alerts (balance less than 10)
    low_stock = [item for item in stock_data if getattr(item, 'balance', 0) < 10][:5]

    # Calculate overall profit metrics
    total_cost = sum(item['total_cost'] for item in product_sales)
    total_profit = sales_summary['net_revenue'] - total_cost

    context = {
        "today": today,
        "stock_data": stock_data,
        "sales_summary": sales_summary,
        "product_sales": product_sales,
        "category_sales": category_sales,
        "subcategory_sales": subcategory_sales,
        "invoices": invoices,
        "expired_purchases": expired_purchases,
        "staff_users": staff_users,
        "top_selling": top_selling,
        "high_profit_products": high_profit_products,
        "low_profit_products": low_profit_products,
        "low_stock": low_stock,
        "total_cost": total_cost,
        "total_profit": total_profit,
        "from_date": from_date or '',
        "to_date": to_date or '',
    }
    return render(request, "shop_report.html", context)


# ==============================================================================
# Dashboard API Views
# ==============================================================================

@login_required
def dashboard(request):
    """General dashboard that redirects to the appropriate role-specific dashboard."""
    user = request.user
    if hasattr(user, 'role'):
        role = getattr(user, 'role', 'staff')
        return redirect_to_dashboard(role)
    else:
        # If user doesn't have a role, redirect to owner dashboard by default
        return redirect('owner_dashboard')


@login_required
def api_dashboard_data(request):
    """API endpoint to provide dashboard data for charts."""
    # Get date range parameters
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    period = request.GET.get('period', '6months')
    
    # Calculate date ranges
    today = timezone.now().date()
    
    if from_date_str and to_date_str:
        # Use provided date range
        try:
            from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.datetime.strptime(to_date_str, '%Y-%m-%d').date()
        except ValueError:
            # If date parsing fails, fall back to default period
            from_date = today - timedelta(days=180)
            to_date = today
    else:
        # Use period-based calculation (fallback for backward compatibility)
        if period == '7days':
            from_date = today - timedelta(days=7)
            to_date = today
        elif period == '30days':
            from_date = today - timedelta(days=30)
            to_date = today
        elif period == '1year':
            from_date = today - timedelta(days=365)
            to_date = today
        else:  # 6months (default)
            from_date = today - timedelta(days=180)
            to_date = today
    
    # Generate chart data based on date range
    chart_labels = []
    income_data = []
    expense_data = []
    
    # Calculate the number of days in the range
    days_diff = (to_date - from_date).days
    
    if days_diff <= 31:  # Show daily data for up to 1 month
        # Generate labels for each day
        current_date = from_date
        while current_date <= to_date:
            chart_labels.append(current_date.strftime('%b %d'))
            day_income = Invoice._default_manager.filter(date=current_date).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
            day_expense = Purchase._default_manager.filter(date=current_date).aggregate(Sum('total_rate'))['total_rate__sum'] or Decimal('0.00')
            income_data.append(float(Decimal(str(day_income))))
            expense_data.append(float(Decimal(str(day_expense))))
            current_date += timedelta(days=1)
    elif days_diff <= 90:  # Show weekly data for up to 3 months
        # Generate labels for weeks
        current_date = from_date
        week_count = 0
        while current_date <= to_date and week_count < 12:  # Limit to 12 weeks
            week_end = min(current_date + timedelta(days=6), to_date)
            chart_labels.append(f'{current_date.strftime("%b %d")} - {week_end.strftime("%b %d")}')
            week_income = Invoice._default_manager.filter(date__range=(current_date, week_end)).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
            week_expense = Purchase._default_manager.filter(date__range=(current_date, week_end)).aggregate(Sum('total_rate'))['total_rate__sum'] or Decimal('0.00')
            income_data.append(float(Decimal(str(week_income))))
            expense_data.append(float(Decimal(str(week_expense))))
            current_date += timedelta(days=7)
            week_count += 1
    else:  # Show monthly data for longer periods
        # Generate labels for months
        current_date = from_date
        month_count = 0
        while current_date <= to_date and month_count < 12:  # Limit to 12 months
            # Calculate the end of the month
            if current_date.month == 12:
                month_end = current_date.replace(year=current_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                month_end = current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
            
            # Make sure month_end doesn't exceed to_date
            month_end = min(month_end, to_date)
            
            chart_labels.append(current_date.strftime('%b %Y'))
            month_income = Invoice._default_manager.filter(date__range=(current_date, month_end)).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
            month_expense = Purchase._default_manager.filter(date__range=(current_date, month_end)).aggregate(Sum('total_rate'))['total_rate__sum'] or Decimal('0.00')
            income_data.append(float(Decimal(str(month_income))))
            expense_data.append(float(Decimal(str(month_expense))))
            
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1, day=1)
            month_count += 1
    
    # Calculate totals for the selected period
    period_invoices = Invoice._default_manager.filter(date__range=(from_date, to_date))
    period_purchases = Purchase._default_manager.filter(date__range=(from_date, to_date))
    
    total_income = period_invoices.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    total_expenses = period_purchases.aggregate(Sum('total_rate'))['total_rate__sum'] or Decimal('0.00')
    net_profit = Decimal(str(total_income)) - Decimal(str(total_expenses))
    
    # Category sales data for the selected period
    category_labels = []
    category_data = []
    for category in Category._default_manager.all():
        category_labels.append(category.name)
        category_total = InvoiceItem._default_manager.filter(
            purchase__category=category,
            invoice__date__range=(from_date, to_date)
        ).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
        category_data.append(float(Decimal(str(category_total))))
    
    # Calculate percentage changes (previous period of same duration)
    prev_period_days = (to_date - from_date).days
    prev_end = from_date - timedelta(days=1)
    prev_start = prev_end - timedelta(days=prev_period_days)
    
    prev_invoices = Invoice._default_manager.filter(date__range=(prev_start, prev_end))
    prev_purchases = Purchase._default_manager.filter(date__range=(prev_start, prev_end))
    
    prev_income = prev_invoices.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    prev_expenses = prev_purchases.aggregate(Sum('total_rate'))['total_rate__sum'] or Decimal('0.00')
    prev_profit = Decimal(str(prev_income)) - Decimal(str(prev_expenses))
    
    # Calculate percentage changes
    income_change = (
        ((Decimal(str(total_income)) - Decimal(str(prev_income))) / Decimal(str(prev_income)) * Decimal('100.00'))
        if prev_income != Decimal('0.00') else Decimal('0.00')
    )
    expense_change = (
        ((Decimal(str(total_expenses)) - Decimal(str(prev_expenses))) / Decimal(str(prev_expenses)) * Decimal('100.00'))
        if prev_expenses != Decimal('0.00') else Decimal('0.00')
    )
    profit_change = (
        ((Decimal(str(net_profit)) - Decimal(str(prev_profit))) / Decimal(str(prev_profit)) * Decimal('100.00'))
        if prev_profit != Decimal('0.00') else Decimal('0.00')
    )
    
    data = {
        'chartLabels': chart_labels,
        'incomeData': income_data,
        'expenseData': expense_data,
        'categoryLabels': category_labels,
        'categoryData': category_data,
        'totalIncome': float(total_income),
        'totalExpenses': float(total_expenses),
        'netProfit': float(net_profit),
        'incomeChange': float(income_change),
        'expenseChange': float(expense_change),
        'profitChange': float(profit_change),
    }
    
    return JsonResponse(data)


# ==============================================================================
# Billing/Invoice Views
# ==============================================================================

@login_required
def invoice_list(request):
    """List all invoices."""
    # For staff, only show invoices they created
    # For owner, show all invoices
    user = request.user
    if user.role == 'staff':
        invoices = Invoice._default_manager.filter(created_by=user).order_by('-date')
    else:
        invoices = Invoice._default_manager.all().order_by('-date')
    
    return render(request, 'invoice_list.html', {
        'invoices': invoices,
        'user_role': user.role
    })


@login_required
def add_billing(request):
    """Create a new invoice."""
    if request.method == 'POST':
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                # Parse form data
                customer_name = request.POST.get('customer_name')
                customer_phone = request.POST.get('customer_phone')
                customer_address = request.POST.get('customer_address', '')
                date = request.POST.get('date', timezone.now().date())
                discount_amount = request.POST.get('discount_amount', 0)
                
                # Generate bill number
                bill_number = f'INV-{timezone.now().strftime("%Y%m%d%H%M%S")}'
                
                # Create invoice
                invoice = Invoice._default_manager.create(
                    bill_number=bill_number,
                    customer_name=customer_name,
                    customer_phone=customer_phone,
                    customer_address=customer_address,
                    date=date,
                    discount_amount=Decimal(str(discount_amount)) if discount_amount else Decimal('0.00'),
                    created_by=request.user
                )
                
                # Process invoice items
                total_forms = int(request.POST.get('items-TOTAL_FORMS', 0))
                
                for i in range(total_forms):
                    category_id = request.POST.get(f'items-{i}-category')
                    subcategory_id = request.POST.get(f'items-{i}-subcategory')
                    product_id = request.POST.get(f'items-{i}-product')
                    quantity = request.POST.get(f'items-{i}-quantity')
                    price = request.POST.get(f'items-{i}-price')
                    
                    # Only process if product is selected
                    if product_id and quantity and price:
                        # Get the purchase object (only non-deleted purchases)
                        purchase = Purchase._default_manager.filter(id=product_id, is_deleted=False).first()
                        
                        # Check if purchase exists and is available
                        if not purchase:
                            raise ValueError(f"Selected product is not available")
                        
                        # Check if there's enough quantity
                        if purchase.quantity < int(quantity):
                            raise ValueError(f"Not enough stock for {purchase.product_name}. Available: {purchase.quantity}, Requested: {quantity}")
                        
                        # Create invoice item
                        InvoiceItem._default_manager.create(
                            invoice=invoice,
                            purchase=purchase,
                            quantity=int(quantity),
                            rate=Decimal(str(price)),
                            total=Decimal(str(price)) * int(quantity)
                        )
                        
                        # Update purchase stock only for non-deleted purchases
                        purchase.quantity -= int(quantity)
                        purchase.save()
                
                # Calculate totals
                invoice.calculate_totals()
                invoice.save()
                
                return JsonResponse({
                    'success': True,
                    'bill_number': invoice.bill_number,
                    'redirect_url': reverse('invoice_view', args=[invoice.pk])
                })
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)
        else:
            # Handle regular form submission
            invoice_form = InvoiceForm(request.POST)
            if invoice_form.is_valid():
                invoice = invoice_form.save(commit=False)
                invoice.created_by = request.user
                invoice.save()
                return redirect('invoice_view', invoice_id=invoice.id)
    else:
        invoice_form = InvoiceForm()
    
    # Get categories for the dropdown (only non-deleted purchases)
    categories = Category._default_manager.all()
    
    return render(request, 'add_invoice.html', {
        'invoice_form': invoice_form,
        'categories': categories
    })


@login_required
def invoice_view(request, invoice_id):
    """View a specific invoice."""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'invoice_view.html', {
        'invoice': invoice
    })


# ==============================================================================
# Staff-wise Report View
# ==============================================================================

# ==============================================================================
# Purchase Removal View
# ==============================================================================

@login_required
@user_passes_test(lambda u: hasattr(u, 'role') and getattr(u, 'role', '') == 'owner')
def remove_purchase(request, pk):
    """Completely remove a purchase record from the database."""
    purchase = get_object_or_404(Purchase, pk=pk)
    
    if request.method == 'POST':
        purchase_name = purchase.product_name
        # Check if the purchase is referenced by any invoice items
        if InvoiceItem._default_manager.filter(purchase=purchase).exists():
            # If referenced, we cannot remove it completely
            messages.error(request, f'Cannot remove purchase "{purchase_name}" as it is referenced in invoices.')
            return redirect('purchase_history')
        else:
            # If not referenced, we can completely remove it
            purchase.hard_delete()  # This will actually delete from database
            messages.success(request, f'Purchase "{purchase_name}" removed completely from the system.')
            return redirect('purchase_history')
    
    return render(request, 'delete_purchase.html', {'purchase': purchase, 'remove_action': True})

@login_required
@user_passes_test(lambda u: hasattr(u, 'role') and getattr(u, 'role', '') == 'owner')
def remove_expired_discounts_view(request):
    """View to manually remove expired discounts."""
    if request.method == 'POST':
        try:
            # Remove expired discounts
            removed_count = Discount.remove_expired_discounts()
            
            if removed_count > 0:
                messages.success(request, f'Successfully removed {removed_count} expired discounts.')
            else:
                messages.info(request, 'No expired discounts found.')
                
        except Exception as e:
            messages.error(request, f'Error removing expired discounts: {str(e)}')
            
        return redirect('view_discount')
    
    # For GET requests, show confirmation page
    expired_discounts = Discount._default_manager.filter(
        end_date__lt=timezone.now().date()
    )
    
    return render(request, 'delete_discount.html', {
        'expired_discounts': expired_discounts,
        'removing_expired': True
    })

@login_required
def print_invoice(request, invoice_id):
    """Print a specific invoice with a professional layout."""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, 'print_invoice.html', {
        'invoice': invoice
    })


@login_required
def delete_invoice(request, invoice_id):
    """Delete a specific invoice and restore stock quantities."""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.method == 'POST':
        try:
            # Restore stock quantities for all items in the invoice
            for item in invoice.items.all():
                purchase = item.purchase
                purchase.quantity += item.quantity
                purchase.save()
            
            # Store bill number before deleting for the response
            bill_number = invoice.bill_number
            
            # Delete the invoice (which will also delete related items due to CASCADE)
            invoice.delete()
            
            # Return success response for AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': f'Invoice #{bill_number} deleted successfully.'})
            else:
                messages.success(request, f'Invoice #{bill_number} deleted successfully.')
                return redirect('invoice_list')
                
        except Exception as e:
            error_message = f'Error deleting invoice: {str(e)}'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_message}, status=500)
            else:
                messages.error(request, error_message)
                return redirect('invoice_list')
    else:
        # For GET requests, we could show a confirmation page, but we're handling this in JavaScript
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
        else:
            # For regular browser requests, redirect to invoice list
            return redirect('invoice_list')


@login_required
def billing_list(request):
    """List billing records (alias for invoice_list)."""
    return invoice_list(request)


@login_required
def list_billing(request):
    """List billing records (alias for invoice_list)."""
    return invoice_list(request)
import traceback

from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import StaffForm
from .models import Category, CustomUser, Discount, Invoice, InvoiceItem, Product, Purchase, SubCategory


# ==============================================================================
# Staff Management Views
# ==============================================================================

@login_required
@user_passes_test(lambda u: hasattr(u, 'role') and getattr(u, 'role', '') == 'owner')
def staff_list(request):
    """List all staff members."""
    staff_users = CustomUser.objects.filter(role='staff')
    return render(request, 'staff_list.html', {'staff_users': staff_users})


@login_required
@user_passes_test(lambda u: hasattr(u, 'role') and getattr(u, 'role', '') == 'owner')
def add_staff(request):
    """Add a new staff member."""
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f"Staff member '{user.username}' added successfully!")
                return redirect('staff_list')
            except Exception as e:
                messages.error(request, f"Error creating staff member: {str(e)}")
        else:
            # Add form errors to messages
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
    else:
        form = StaffForm()
    
    return render(request, 'add_staff.html', {'form': form})


@login_required
@user_passes_test(lambda u: hasattr(u, 'role') and getattr(u, 'role', '') == 'owner')
def edit_staff(request, staff_id):
    """Edit a staff member."""
    staff = get_object_or_404(CustomUser, id=staff_id, role='staff')
    
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, f"Staff member '{user.username}' updated successfully!")
                return redirect('staff_list')
            except Exception as e:
                messages.error(request, f"Error updating staff member: {str(e)}")
        else:
            # Add form errors to messages
            if form.errors:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
    else:
        form = StaffForm(instance=staff)
    
    return render(request, 'edit_staff.html', {'form': form, 'staff': staff})


@login_required
@user_passes_test(lambda u: hasattr(u, 'role') and getattr(u, 'role', '') == 'owner')
def delete_staff(request, staff_id):
    """Delete a staff member."""
    staff = get_object_or_404(CustomUser, id=staff_id, role='staff')
    
    if request.method == 'POST':
        staff.delete()
        return redirect('staff_list')
    
    return render(request, 'delete_staff.html', {'staff': staff})


@login_required
def add_discount(request, purchase_id):
    """Add or edit a discount for a purchase."""
    purchase = get_object_or_404(Purchase, id=purchase_id)
    
    # Get the Product associated with this Purchase (if any)
    product = None
    existing_discount = None
    
    # Try to get existing product and discount
    try:
        product = Product._default_manager.get(purchase=purchase)
        # Try to get existing discount
        try:
            existing_discount = Discount._default_manager.get(product=product)
        except Exception:
            existing_discount = None
    except Exception:
        product = None
        existing_discount = None
    
    if request.method == 'POST':
        print("POST request received")
        try:
            # Get discount percentage from POST data
            discount_percentage_str = request.POST.get('discount_percentage')
            print(f"Discount percentage string: {discount_percentage_str}")
            
            # Validate that discount percentage is provided
            if not discount_percentage_str or not discount_percentage_str.strip():
                messages.error(request, "Discount percentage is required.")
                return render(request, 'add_discount.html', {
                    'purchase': purchase,
                    'existing_discount': existing_discount
                })
            
            # Convert to float without sanitization that might corrupt the value
            try:
                discount_percentage = float(discount_percentage_str)
                print(f"Discount percentage float: {discount_percentage}")
            except (ValueError, TypeError):
                messages.error(request, "Invalid discount percentage value.")
                return render(request, 'add_discount.html', {
                    'purchase': purchase,
                    'existing_discount': existing_discount
                })
            
            # Validate range
            if not (0 <= discount_percentage <= 100):
                messages.error(request, "Discount percentage must be between 0 and 100.")
                return render(request, 'add_discount.html', {
                    'purchase': purchase,
                    'existing_discount': existing_discount
                })

            # Additional validation to ensure MRP exists
            if purchase.mrp is None or float(purchase.mrp) <= 0:
                messages.error(request, "Product MRP is not set or invalid.")
                return render(request, 'add_discount.html', {
                    'purchase': purchase,
                    'existing_discount': existing_discount
                })
                
            # Get start and end dates
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')
            
            # Validate dates
            if not start_date_str or not start_date_str.strip() or not end_date_str or not end_date_str.strip():
                messages.error(request, "Both start date and end date are required.")
                return render(request, 'add_discount.html', {
                    'purchase': purchase,
                    'existing_discount': existing_discount
                })
            
            try:
                from datetime import datetime
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
                return render(request, 'add_discount.html', {
                    'purchase': purchase,
                    'existing_discount': existing_discount
                })
            
            # Validate that end date is after or equal to start date
            if end_date < start_date:
                messages.error(request, "End date must be on or after start date.")
                return render(request, 'add_discount.html', {
                    'purchase': purchase,
                    'existing_discount': existing_discount
                })
            
            # NEW VALIDATION: Prevent previous days from being selected
            today = timezone.now().date()
            if start_date < today:
                messages.error(request, "Start date cannot be in the past.")
                return render(request, 'add_discount.html', {
                    'purchase': purchase,
                    'existing_discount': existing_discount
                })
            
            # NEW VALIDATION: Check for overlapping discounts for the same product
            if product:
                # Check for overlapping discounts for the same product with same dates and percentage
                # This implements the rule: same start date and ending date with the same product in same discount is not allowed
                overlapping_discounts = Discount._default_manager.filter(
                    product=product,
                    start_date=start_date,
                    end_date=end_date,
                    discount_percent=discount_percentage
                )
                
                # If we're editing an existing discount, exclude it from the overlap check
                if existing_discount:
                    overlapping_discounts = overlapping_discounts.exclude(id=existing_discount.id)
                
                if overlapping_discounts.exists():
                    messages.error(request, "A discount with the same percentage, start date, and end date already exists for this product.")
                    return render(request, 'add_discount.html', {
                        'purchase': purchase,
                        'existing_discount': existing_discount
                    })
            
            # Calculate the final price based on the discount
            final_price = Decimal(str(purchase.mrp)) * (1 - Decimal(str(discount_percentage)) / 100)
            
            # If no product exists for this purchase, create one
            if not product:
                print(f"Creating product for purchase: {purchase.product_name}")
                product = Product._default_manager.create(
                    name=purchase.product_name,
                    purchase=purchase,
                    category=purchase.category,
                    subcategory=purchase.subcategory,
                    mrp=Decimal(str(purchase.mrp)),
                    purchase_rate=Decimal(str(purchase.product_rate)),
                    selling_price=Decimal(str(purchase.mrp)),
                    stock_quantity=purchase.quantity,
                    final_price=final_price  # Add the final_price value here
                )
                print(f"Created product: {product.name}")
            
            # Also update the purchase's sale_rate to reflect the MRP initially
            if purchase.sale_rate is None:
                purchase.sale_rate = float(purchase.mrp)
                purchase.save()
            
            # Create or update discount
            if existing_discount:
                print(f"Updating existing discount for product: {product.name}")
                existing_discount.discount_percent = discount_percentage
                existing_discount.start_date = start_date
                existing_discount.end_date = end_date
                # Set status to active if current date is within the discount period
                today = timezone.now().date()
                if start_date <= today <= end_date:
                    existing_discount.status = 'active'
                elif today < start_date:
                    existing_discount.status = 'pending'
                else:
                    existing_discount.status = 'rejected'  # Expired discounts are rejected
                existing_discount.save()
                print(f"Updated discount: percent={existing_discount.discount_percent}, start={existing_discount.start_date}, end={existing_discount.end_date}, status={existing_discount.status}")
                messages.success(request, "Discount updated successfully!")
            else:
                print(f"Creating discount for product: {product.name}")
                # Set initial status based on dates
                today = timezone.now().date()
                status = 'pending'
                if start_date <= today <= end_date:
                    status = 'active'
                elif today > end_date:
                    status = 'rejected'
                
                discount = Discount._default_manager.create(
                    product=product,
                    discount_percent=discount_percentage,
                    start_date=start_date,
                    end_date=end_date,
                    status=status
                )
                print(f"Created discount: id={discount.id}, percent={discount.discount_percent}, start={discount.start_date}, end={discount.end_date}, status={discount.status}")
                messages.success(request, "Discount applied successfully!")
            
            # Update the purchase's sale_rate to reflect the discount
            if discount_percentage > 0:
                discounted_price = float(purchase.mrp) * (1 - discount_percentage / 100)
                purchase.sale_rate = discounted_price
                purchase.save()
                print(f"Updated purchase sale_rate to: {purchase.sale_rate}")
            
            # Update the product's final_price
            product.final_price = final_price
            product.save()
            print(f"Updated product final_price to: {product.final_price}")
            
            # Debug: Print a message to see if we reach this point
            print("Redirecting to view_discount")
            response = redirect('view_discount')
            print(f"Redirect response: {response}")
            return response
        except Exception as e:
            print(f"Exception in add_discount: {e}")
            import traceback
            traceback.print_exc()
            messages.error(request, f"Error applying discount: {str(e)}")
            return render(request, 'add_discount.html', {
                'purchase': purchase,
                'existing_discount': existing_discount
            })
    
    # GET request - show the form
    return render(request, 'add_discount.html', {
        'purchase': purchase,
        'existing_discount': existing_discount
    })


def load_subcategories(request):
    """AJAX view to load subcategories for a given category."""
    category_id = request.GET.get('category_id')
    if not category_id:
        return JsonResponse({'error': 'Category ID is required'}, status=400)
    
    # Validate that category_id is a valid integer
    try:
        category_id = int(category_id)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid category ID'}, status=400)
    
    try:
        # Check if category exists
        if not Category._default_manager.filter(id=category_id).exists():
            return JsonResponse({'error': 'Category not found'}, status=404)
            
        subcategories = SubCategory._default_manager.filter(category_id=category_id).values('id', 'name')
        return JsonResponse(list(subcategories), safe=False)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred while fetching subcategories'}, status=500)


@login_required
def load_products(request):
    """AJAX view to load products for a given subcategory."""
    subcategory_id = request.GET.get('subcategory_id')
    if not subcategory_id:
        return JsonResponse({'error': 'Subcategory ID is required'}, status=400)
    
    # Validate that subcategory_id is a valid integer
    try:
        subcategory_id = int(subcategory_id)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid subcategory ID'}, status=400)
    
    try:
        # Check if subcategory exists
        if not SubCategory._default_manager.filter(id=subcategory_id).exists():
            return JsonResponse({'error': 'Subcategory not found'}, status=404)
        
        # Get purchases that have this subcategory, are not deleted, are still in stock, and are NOT stock update entries
        purchases = Purchase._default_manager.filter(
            subcategory_id=subcategory_id,
            is_deleted=False,
            quantity__gt=0
        ).exclude(notes__icontains='Stock update entry').values('id', 'product_name', 'quantity', 'sale_rate', 'product_rate')
        return JsonResponse(list(purchases), safe=False)
    except Exception as e:
        return JsonResponse({'error': 'An error occurred while fetching products'}, status=500)


@login_required
def get_product_details(request):
    """AJAX view to get product details for a given purchase."""
    purchase_id = request.GET.get('purchase_id')
    if not purchase_id:
        return JsonResponse({'error': 'Purchase ID is required'}, status=400)
    
    # Validate that purchase_id is a valid integer
    try:
        purchase_id = int(purchase_id)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid purchase ID'}, status=400)
    
    try:
        purchase = Purchase._default_manager.exclude(notes__icontains='Stock update entry').get(id=purchase_id)
        data = {
            'quantity': purchase.quantity,
            'sale_rate': purchase.sale_rate,
            'product_rate': purchase.product_rate
        }
        return JsonResponse(data)
    except Exception:
        return JsonResponse({'error': 'An error occurred while fetching product details'}, status=500)


# ==============================================================================
# Stock Management Views
# ==============================================================================

@login_required
def update_stock(request, purchase_id):
    """Update existing stock quantity by adding to existing stock without creating new records."""
    original_purchase = get_object_or_404(Purchase, id=purchase_id)
    
    if request.method == 'POST':
        try:
            additional_quantity_str = sanitize_input(request.POST.get('additional_quantity', ''))
            
            # Validate input
            if not additional_quantity_str:
                messages.error(request, 'Additional quantity is required.')
                return redirect('list_purchases')
                
            additional_quantity = int(additional_quantity_str)
            
            if additional_quantity <= 0:
                messages.error(request, 'Additional quantity must be greater than zero.')
                return redirect('list_purchases')
            
            # Update the original purchase quantity (add additional stock to existing stock)
            old_quantity = original_purchase.quantity
            original_purchase.quantity = old_quantity + additional_quantity
            original_purchase.notes = f"{original_purchase.notes or ''} | Stock updated on {timezone.now().date()}. Added {additional_quantity} units."
            original_purchase.save()
            
            # REMOVED: Creating a new purchase entry for the purchase history (stock update record)
            # This ensures we only update the existing stock quantity directly without creating new fields
            
            messages.success(request, f'Stock for "{original_purchase.product_name}" updated successfully. Added {additional_quantity} units. New total: {original_purchase.quantity} units.')
            return redirect('list_purchases')
            
        except ValueError:
            messages.error(request, 'Invalid quantity value. Please enter a valid number.')
            return redirect('list_purchases')
        except Exception as e:
            messages.error(request, f'Error updating stock: {str(e)}')
            return redirect('list_purchases')
    
    # GET request - show update form
    return render(request, 'update_stock.html', {
        'purchase': original_purchase
    })


# ==============================================================================
# Staff-wise Report Views
# ==============================================================================

@login_required
def staff_wise_report(request, staff_id):
    """Generate report for a specific staff member."""
    # Get the staff user
    staff = get_object_or_404(CustomUser, id=staff_id, role='staff')
    
    # Get date range filters from request
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    
    # Base invoice queryset for this staff member
    invoice_qs = Invoice._default_manager.filter(created_by=staff)
    
    # Apply date filters
    if from_date and to_date:
        invoice_qs = invoice_qs.filter(date__range=[from_date, to_date])
    elif from_date:
        invoice_qs = invoice_qs.filter(date__gte=from_date)
    elif to_date:
        invoice_qs = invoice_qs.filter(date__lte=to_date)
    
    # --- Sales Summary for this staff ---
    sales_summary = invoice_qs.aggregate(
        total_sales=Coalesce(Sum("total"), Value(Decimal(0)), output_field=DecimalField()),
        total_discount=Coalesce(Sum("discount_amount"), Value(Decimal(0)), output_field=DecimalField()),
    )
    
    # Calculate net revenue
    sales_summary['net_revenue'] = sales_summary['total_sales'] - sales_summary['total_discount']
    
    # --- Product-wise Sales Report with Profit Calculation for this staff ---
    product_sales_query = InvoiceItem._default_manager.filter(
        invoice__created_by=staff,
        purchase__is_deleted=False
    ).values(
        "purchase__product_name", 
        "purchase__category__name",
        "purchase__category__id",
        "purchase__subcategory__name",
        "purchase__subcategory__id",
        "purchase__product_rate",  # Cost price
        "purchase__sale_rate"      # Selling price
    )
    
    # Apply date filter to InvoiceItem via invoice__date
    if from_date and to_date:
        product_sales_query = product_sales_query.filter(invoice__date__range=[from_date, to_date])
    elif from_date:
        product_sales_query = product_sales_query.filter(invoice__date__gte=from_date)
    elif to_date:
        product_sales_query = product_sales_query.filter(invoice__date__lte=to_date)
    
    product_sales = (
        product_sales_query.annotate(
            total_qty=Coalesce(Sum("quantity"), Value(0), output_field=IntegerField()),
            total_amount=Coalesce(Sum("total"), Value(Decimal(0)), output_field=DecimalField()),
            total_cost=Coalesce(Sum(F("quantity") * F("purchase__product_rate")), Value(Decimal(0)), output_field=DecimalField()),
            profit=Coalesce(Sum("total"), Value(Decimal(0)), output_field=DecimalField()) - 
                   Coalesce(Sum(F("quantity") * F("purchase__product_rate")), Value(Decimal(0)), output_field=DecimalField())
        )
        .order_by("-profit")  # Sort by annotated profit field
    )
    
    # Calculate additional metrics for each product
    for product in product_sales:
        if product['total_qty'] > 0:
            product['avg_price'] = product['total_amount'] / product['total_qty']
            product['profit_per_unit'] = product['profit'] / product['total_qty']
        else:
            product['avg_price'] = Decimal(0)
            product['profit_per_unit'] = Decimal(0)
    
    # --- Category-wise Sales Report with Profit for this staff ---
    category_sales_query = InvoiceItem._default_manager.filter(
        invoice__created_by=staff,
        purchase__is_deleted=False
    ).values("purchase__category__name", "purchase__category__id")
    
    # Apply date filter to InvoiceItem via invoice__date
    if from_date and to_date:
        category_sales_query = category_sales_query.filter(invoice__date__range=[from_date, to_date])
    elif from_date:
        category_sales_query = category_sales_query.filter(invoice__date__gte=from_date)
    elif to_date:
        category_sales_query = category_sales_query.filter(invoice__date__lte=to_date)
    
    category_sales = (
        category_sales_query.annotate(
            total_qty=Coalesce(Sum("quantity"), Value(0), output_field=IntegerField()),
            total_amount=Coalesce(Sum("total"), Value(Decimal(0)), output_field=DecimalField()),
            total_cost=Coalesce(Sum(F("quantity") * F("purchase__product_rate")), Value(Decimal(0)), output_field=DecimalField()),
            profit=Coalesce(Sum("total"), Value(Decimal(0)), output_field=DecimalField()) - 
                   Coalesce(Sum(F("quantity") * F("purchase__product_rate")), Value(Decimal(0)), output_field=DecimalField())
        )
        .order_by("-profit")  # Sort by annotated profit field
    )
    
    # Calculate percentage of total sales for each category
    for category in category_sales:
        if sales_summary['total_sales'] > 0:
            category['percentage'] = (category['total_amount'] / sales_summary['total_sales']) * 100
        else:
            category['percentage'] = 0
    
    # --- Billing List for this staff ---
    invoices = invoice_qs.annotate(
        net_amount=F("total") - F("discount_amount")
    ).order_by("-total")  # Sort by total amount
    
    # --- Additional data for enhanced report ---
    # Top selling products (top 5)
    top_selling = list(product_sales[:5])
    
    # Highest profit products (top 5)
    high_profit_products = sorted(
        [p for p in product_sales if p['profit'] > 0], 
        key=lambda x: x['profit'], 
        reverse=True
    )[:5]
    
    # Low profit products (bottom 5)
    low_profit_products = sorted(
        [p for p in product_sales if p['profit'] > 0], 
        key=lambda x: x['profit']
    )[:5]
    
    # Calculate overall profit metrics
    total_cost = sum(item['total_cost'] for item in product_sales)
    total_profit = sales_summary['net_revenue'] - total_cost
    
    today = timezone.now().date()
    
    context = {
        "staff": staff,
        "today": today,
        "sales_summary": sales_summary,
        "product_sales": product_sales,
        "category_sales": category_sales,
        "invoices": invoices,
        "top_selling": top_selling,
        "high_profit_products": high_profit_products,
        "low_profit_products": low_profit_products,
        "total_cost": total_cost,
        "total_profit": total_profit,
        "from_date": from_date or '',
        "to_date": to_date or '',
    }
    return render(request, "staff_wise_report.html", context)