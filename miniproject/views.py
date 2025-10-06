from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import CustomUser  # Ensure this is your custom user model

def login_view(request):
    if request.user.is_authenticated:
        role = request.user.role
        return redirect_to_dashboard(role)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            role = user.role
            return redirect_to_dashboard(role)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


def redirect_to_dashboard(role):
    if role == 'admin':
        return redirect('admin_dashboard')
    elif role == 'staff':
        return redirect('staff_dashboard')
    elif role == 'owner':
        return redirect('owner_dashboard')
    else:
        return redirect('login')  # fallback

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')


@login_required
@user_passes_test(lambda u: not u.is_superuser)
def staff_dashboard(request):
    return render(request, 'staff_dashboard.html')


# catagory management views

from .models import Category
from .forms import CategoryForm

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_category')  # Replace with your desired redirect
    else:
        form = CategoryForm()
    return render(request, 'add_category.html', {'form': form})

def list_category(request):
    query = request.GET.get('q')
    if query:
        categories = Category.objects.filter(name__icontains=query)
    else:
        categories = Category.objects.all()

    return render(request, 'list_category.html', {'categories': categories})

# edit catagory view

from django.shortcuts import render, get_object_or_404, redirect
from .models import Category
from .forms import CategoryForm  # assuming you're using a form

def edit_category(request, pk):
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
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('list_category')
    return render(request, 'delete_category.html', {'category': category})



# subcategory management views

from django.shortcuts import render, redirect, get_object_or_404
from .models import SubCategory
from .forms import SubCategoryForm

def add_subcategory(request):
    if request.method == 'POST':
        form = SubCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_subcategory')
    else:
        form = SubCategoryForm()
    return render(request, 'add_subcategory.html', {'form': form})

def list_subcategory(request):
    query = request.GET.get('q')
    if query:
        subcategories = SubCategory.objects.filter(name__icontains=query)
    else:
        subcategories = SubCategory.objects.all()
    return render(request, 'list_subcategory.html', {'subcategories': subcategories})

def edit_subcategory(request, pk):
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
    subcategory = get_object_or_404(SubCategory, pk=pk)
    if request.method == 'POST':
        subcategory.delete()
        return redirect('list_subcategory')
    return render(request, 'delete_subcategory.html', {'subcategory': subcategory})


# purchase management 

from django.shortcuts import render, redirect, get_object_or_404
from .models import Purchase, Category, Product
from .forms import PurchaseForm, PurchaseEditForm
from django.db.models import Q
from django.contrib import messages
from django.db.models import Q

def list_purchases(request):
    query = request.GET.get('q', '').strip()
    category_filter = request.GET.get('category', '')

    purchases = Purchase.objects.all()

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

    categories = Category.objects.all()

    return render(request, 'list_purchase.html', {
        'purchases': purchases,
        'categories': categories,
        'query': query,
        'category_filter': category_filter,
    })

from django.core.serializers import serialize
from django.http import JsonResponse
from .models import Category, SubCategory
def add_purchase(request):
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Purchase added.')
            return redirect('list_purchases')
    else:
        form = PurchaseForm()

    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    subcategories_json = [
        {'id': s.id, 'name': s.name, 'category_id': s.category.id}
        for s in subcategories
    ]

    return render(request, 'add_purchase.html', {
        'form': form,
        'categories': categories,
        'subcategories': subcategories,  # Pass the queryset for template use
        'subcategories_json': subcategories_json
    })
from django.http import JsonResponse

def get_subcategories_by_category(request):
    category_id = request.GET.get('category_id')
    subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(subcategories), safe=False)


# def edit_purchase(request, pk):
#     purchase = get_object_or_404(Purchase, id=pk)
    
#     if request.method == 'POST':
#         form = PurchaseForm(request.POST, instance=purchase)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Purchase updated successfully!')
#             return redirect('list_purchases')
#     else:
#         form = PurchaseForm(instance=purchase)
    
#     categories = Category.objects.all()
#     subcategories = SubCategory.objects.all()
#     subcategories_json = [
#         {'id': s.id, 'name': s.name, 'category_id': s.category.id}
#         for s in subcategories
#     ]
    
#     return render(request, 'edit_purchase.html', {
#         'form': form,
#         'purchase': purchase,
#         'categories': categories,
#         'subcategories': subcategories,
#         'subcategories_json': subcategories_json
#     })

def edit_purchase(request, pk):
    purchase = get_object_or_404(Purchase, id=pk)
    
    if request.method == 'POST':
        form = PurchaseForm(request.POST, instance=purchase)
        if form.is_valid():
            form.save()
            messages.success(request, 'Purchase updated successfully!')
            return redirect('list_purchases')
    else:
        form = PurchaseForm(instance=purchase)
    
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    subcategories_json = [
        {'id': s.id, 'name': s.name, 'category_id': s.category.id}
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
    purchase = get_object_or_404(Purchase, pk=pk)
    purchase.delete()
    messages.success(request, 'Purchase deleted successfully.')
    return redirect('list_purchases')



# fixed list purchase
# def edit_purchase_fixed(request, pk):
#     purchase = get_object_or_404(Purchase, id=pk)
    
#     if request.method == 'POST':
#         form = PurchaseForm(request.POST)
#         if form.is_valid():
#             # Update the original purchase (for list_purchases.html)
#             original_form = PurchaseForm(request.POST, instance=purchase)
#             if original_form.is_valid():
#                 original_form.save()
            
#             # Create a new purchase record (for fixed_purchases.html)
#             new_purchase = Purchase(
#                 product_name=form.cleaned_data['product_name'],
#                 category=form.cleaned_data['category'],
#                 subcategory=form.cleaned_data['subcategory'],
#                 quantity=form.cleaned_data['quantity'],
#                 product_rate=form.cleaned_data['product_rate'],
#                 total_rate=form.cleaned_data['total_rate'],
#                 sale_rate=form.cleaned_data['sale_rate'],
#                 mrp=form.cleaned_data['mrp'],
#                 date=form.cleaned_data['date'],
#                 expire_date=form.cleaned_data['expire_date'],
#                 notes=form.cleaned_data['notes'],
#                 change_price=form.cleaned_data['product_rate']  # Store the new product rate in change_price
#             )
#             new_purchase.save()
#             messages.success(request, 'Purchase updated and saved as a new record.')
#             return redirect('fixed_purchases')
#     else:
#         form = PurchaseForm(instance=purchase)
    
#     categories = Category.objects.all()
#     subcategories = SubCategory.objects.all()
#     subcategories_json = [
#         {'id': s.id, 'name': s.name, 'category_id': s.category.id}
#         for s in subcategories
#     ]
    
#     return render(request, 'edit_purchase.html', {
#         'form': form,
#         'purchase': purchase,
#         'categories': categories,
#         'subcategories': subcategories,
#         'subcategories_json': subcategories_json
#     })

# def fixed_purchases(request):
#     purchases = Purchase.objects.all().order_by('-date')
#     categories = Category.objects.all()
#     return render(request, 'fixed_purchases.html', {
#         'purchases': purchases,
#         'categories': categories
#     })





# product management views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Purchase
from django.db.models import Case, When, Value, FloatField, F, ExpressionWrapper, Q
from django.contrib.auth.decorators import login_required
def list_products_staff(request):
    # Base queryset with related objects to avoid N+1 queries
    purchases = Purchase.objects.select_related('category', 'subcategory').all()

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
    # Base queryset with related objects to avoid N+1 queries
    purchases = Purchase.objects.select_related('category', 'subcategory').all()

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

# @login_required
# def add_purchase(request):
#     if request.method == 'POST':
#         product_name = request.POST.get('product_name')
#         category_id = request.POST.get('category')
#         subcategory_id = request.POST.get('subcategory')
#         quantity = request.POST.get('quantity')
#         product_rate = request.POST.get('product_rate')
#         mrp = request.POST.get('mrp')
#         notes = request.POST.get('notes')
#         date = request.POST.get('date')

#         try:
#             quantity = float(quantity)
#             product_rate = float(product_rate)
#             mrp = float(mrp)
#             total_rate = quantity * product_rate
#         except ValueError:
#             messages.error(request, "Invalid numeric input.")
#             return redirect('add_purchase')

#         purchase = Purchase(
#             product_name=product_name,
#             category_id=category_id,
#             subcategory_id=subcategory_id if subcategory_id else None,
#             quantity=quantity,
#             product_rate=product_rate,
#             total_rate=total_rate,
#             mrp=mrp,
#             notes=notes,
#             date=date
#         )
#         purchase.save()
#         messages.success(request, "Purchase added successfully!")
#         return redirect('list_products')

#     return render(request, 'add_purchase.html')

def add_discount(request, purchase_id):
    purchase = get_object_or_404(Purchase, id=purchase_id)
    if request.method == 'POST':
        discount_percentage = request.POST.get('discount_percentage')
        try:
            discount_percentage = float(discount_percentage)
            if not (0 <= discount_percentage <= 100):
                raise ValueError("Discount percentage must be between 0 and 100.")
            purchase.sale_rate = purchase.mrp * (1 - discount_percentage / 100)
            purchase.save()
            messages.success(request, "Discount applied successfully!")
        except ValueError:
            messages.error(request, "Invalid discount percentage.")
        return redirect('list_products')
    return render(request, 'add_discount.html', {'purchase': purchase})

def view_discount(request):
    # Get purchases with discounts (sale_rate is not null)
    purchases = Purchase.objects.select_related('category', 'subcategory').filter(
        sale_rate__isnull=False
    ).annotate(
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
    }
    return render(request, 'view_discount.html', context)



from django.db.models import Sum, F
from django.shortcuts import render
from .models import Purchase

def stock_report(request):
    report = (
        Purchase.objects.annotate(
            total_purchased=F("quantity"),  # purchased stock
            total_sold=Sum("invoiceitem__quantity"),  # sold stock from invoices
        ).annotate(
            balance=F("total_purchased") - (F("total_sold") or 0)  # balance stock
        )
    )
    return render(request, "stock_report.html", {"report": report})





from decimal import Decimal
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.db import transaction
from django import forms
from django.utils import timezone
import datetime
import random
from .models import Invoice, InvoiceItem, Product, SubCategory, Category, Purchase

# --- AJAX endpoints ---

from django.http import JsonResponse

def ajax_load_categories(request):
    categories = Category.objects.values('id', 'name')
    return JsonResponse(list(categories), safe=False)

def ajax_load_subcategories(request):
    category_id = request.GET.get('category_id')
    if not category_id:
        return JsonResponse([], safe=False)
    subcats = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(subcats), safe=False)


def ajax_load_products(request):
    subcategory_id = request.GET.get('subcategory_id')
    if not subcategory_id:
        return JsonResponse([], safe=False)
    purchases = Purchase.objects.filter(subcategory_id=subcategory_id).values('id', 'product_name')
    return JsonResponse(list(purchases), safe=False)

from django.http import JsonResponse

def ajax_get_product_details(request):
    purchase_id = request.GET.get('purchase_id')
    if not purchase_id:
        return JsonResponse({'error': 'purchase_id required'}, status=400)
    
    try:
        purchase = Purchase.objects.get(id=purchase_id)
        data = {
            'id': purchase.id,
            'name': purchase.product_name,
            'sale_rate': float(purchase.sale_rate) if purchase.sale_rate is not None else 0.0,
            'quantity': purchase.quantity,
        }
        return JsonResponse(data)
    except Purchase.DoesNotExist:
        return JsonResponse({'error': 'Purchase not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
# --- Billing save (handles POST form-data like items-0-product, items-0-quantity, etc.) ---
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal
import datetime
import random
from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal
import datetime
import random
from django.shortcuts import render

from django.http import JsonResponse
from django.db import transaction
from decimal import Decimal
import datetime
import random
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import random
from .models import Invoice, Purchase, InvoiceItem, Category

from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import random
import logging

from .models import Invoice, InvoiceItem, Purchase, Category

logger = logging.getLogger(__name__)

@login_required
def add_billing(request):
    if request.method == "POST" and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        logger.debug(f"Received POST data: {request.POST}")

        try:
            total_forms = int(request.POST.get('items-TOTAL_FORMS', 0))
        except ValueError:
            logger.error("Invalid TOTAL_FORMS value")
            return JsonResponse({'success': False, 'error': 'Invalid form data: TOTAL_FORMS is not a valid integer'}, status=400)

        if total_forms == 0:
            logger.error("No items provided in form")
            return JsonResponse({'success': False, 'error': 'No items provided'}, status=400)

        customer_name = request.POST.get('customer_name', '').strip()
        customer_phone = request.POST.get('customer_phone', '').strip()
        customer_address = request.POST.get('customer_address', '')

        date_str = request.POST.get('date', '')
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            logger.warning(f"Invalid date format: {date_str}, using current date")
            date = timezone.now().date()

        try:
            # gst_percent = Decimal(request.POST.get('gst_percent', '0'))
            roundoff = Decimal(request.POST.get('roundoff', '0'))
            overall_discount = Decimal(request.POST.get('discount_amount', '0'))
        except (ValueError, TypeError) as e:
            logger.error(f"Invalid numeric values: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Invalid numeric values for GST, discount, or round-off'}, status=400)

        if not customer_name or not customer_phone:
            logger.error("Missing customer name or phone")
            return JsonResponse({'success': False, 'error': 'Customer name and phone are required'}, status=400)

        while True:
            bill_number = f"BILL-{timezone.now().date().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
            if not Invoice.objects.filter(bill_number=bill_number).exists():
                break

        items = []
        for i in range(total_forms):
            purchase_id = request.POST.get(f'items-{i}-product')
            qty = request.POST.get(f'items-{i}-quantity')
            rate = request.POST.get(f'items-{i}-price')
            discount = request.POST.get(f'items-{i}-discount')

            if not purchase_id:
                continue

            try:
                purchase = Purchase.objects.get(id=int(purchase_id))
            except (Purchase.DoesNotExist, ValueError):
                logger.error(f"Purchase ID {purchase_id} not found")
                return JsonResponse({'success': False, 'error': f'Purchase ID {purchase_id} not found'}, status=400)

            try:
                qty = int(qty)
                rate = Decimal(str(rate or purchase.sale_rate or '0.00'))
                discount = Decimal(str(discount or '0.00'))
            except (ValueError, TypeError) as e:
                logger.error(f"Invalid data for product {purchase.product_name}: {str(e)}")
                return JsonResponse({'success': False, 'error': f'Invalid quantity, price, or discount for product {purchase.product_name}'}, status=400)

            if qty <= 0:
                logger.error(f"Non-positive quantity for product {purchase.product_name}")
                return JsonResponse({'success': False, 'error': f'Quantity must be positive for product {purchase.product_name}'}, status=400)

            items.append({
                'purchase': purchase,
                'quantity': qty,
                'rate': rate,
                'discount': discount
            })

        if not items:
            logger.error("No valid products provided")
            return JsonResponse({'success': False, 'error': 'At least one valid product is required'}, status=400)

        # Check stock availability
        for item in items:
            if item['quantity'] > item['purchase'].quantity:
                logger.error(f"Insufficient stock for {item['purchase'].product_name}")
                return JsonResponse(
                    {'success': False, 'error': f"Insufficient stock for {item['purchase'].product_name}. Available: {item['purchase'].quantity}"},
                    status=400
                )

        try:
            with transaction.atomic():
                # Create invoice
                invoice = Invoice.objects.create(
                    bill_number=bill_number,
                    customer_name=customer_name,
                    customer_phone=customer_phone,
                    customer_address=customer_address,
                    date=date,
                    # gst_percent=gst_percent,
                    roundoff=roundoff,
                    discount_amount=overall_discount,
                    created_by=request.user
                )

                subtotal = Decimal('0.00')
                for item in items:
                    invoice_item = InvoiceItem(
                        invoice=invoice,
                        purchase=item['purchase'],
                        quantity=item['quantity'],
                        rate=item['rate'],
                        discount_amount=item['discount']
                    )
                    invoice_item.total = (item['rate'] * item['quantity'] - item['discount']).quantize(Decimal('0.01'))
                    invoice_item.save()

                    # Update stock
                    purchase = item['purchase']
                    purchase.quantity = max(0, purchase.quantity - item['quantity'])
                    purchase.save(update_fields=['quantity'])

                    subtotal += invoice_item.total

                invoice.subtotal = subtotal.quantize(Decimal('0.01'))
                # invoice.gst_amount = (subtotal * (gst_percent / Decimal('100.00'))).quantize(Decimal('0.01'))
                invoice.total = (subtotal - roundoff).quantize(Decimal('0.01'))
                invoice.save()

                logger.info(f"Invoice {invoice.bill_number} created successfully")
                return JsonResponse({
                    'success': True,
                    'invoice_id': invoice.id,
                    'bill_number': invoice.bill_number,
                    'redirect_url': f'/billing/view/{invoice.id}/'
                })

        except Exception as e:
            logger.error(f"Database error in add_billing: {str(e)}", exc_info=True)
            return JsonResponse({'success': False, 'error': f'Database error: {str(e)}'}, status=500)

    categories = Category.objects.all()
    return render(request, "add_invoice.html", {"categories": categories})

def invoice_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    return render(request, "invoice_view.html", {"invoice": invoice})

from django.shortcuts import render

def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-date')
    return render(request, "invoice_list.html", {"invoices": invoices})



from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Invoice, InvoiceItem, Purchase

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Invoice, InvoiceItem, Purchase

@require_POST
def delete_invoice(request, invoice_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            with transaction.atomic():
                invoice = get_object_or_404(Invoice, id=invoice_id)
                bill_number = invoice.bill_number
                
                # Restore stock quantities
                for item in invoice.items.all():
                    purchase = item.purchase
                    purchase.quantity += item.quantity
                    purchase.save(update_fields=['quantity'])
                
                # Delete invoice and its items
                invoice.delete()
                
                return JsonResponse({
                    'success': True,
                    'bill_number': bill_number
                })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'Failed to delete invoice: {str(e)}'
            }, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400) 



from django.shortcuts import render
from django.db.models import Sum, F, Value, DecimalField
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from decimal import Decimal
from .models import Purchase, Product, Invoice, InvoiceItem, Category, SubCategory

from django.db.models import F, Sum, Value, DecimalField, IntegerField, ExpressionWrapper
from django.db.models.functions import Coalesce
from django.utils.timezone import now
from datetime import timedelta
from decimal import Decimal
from django.shortcuts import render
from .models import Purchase, Invoice, InvoiceItem  # Adjust import based on your models' location

def shop_report(request):
    today = now().date()

    # --- Stock Report ---
    stock_data = (
        Purchase.objects.annotate(
            total_purchased=F("quantity"),
            total_sold=Coalesce(Sum("invoiceitem__quantity"), Value(0), output_field=IntegerField()),
        ).annotate(
            balance=F("total_purchased") - F("total_sold")  # Balance = Purchased - Sold
        ).order_by("balance")  # Sort by balance for stock report
    )

    # --- Sales Summary ---
    sales_summary = Invoice.objects.aggregate(
        total_sales=Coalesce(Sum("total"), Value(Decimal(0)), output_field=DecimalField()),
        total_discount=Coalesce(Sum("discount_amount"), Value(Decimal(0)), output_field=DecimalField()),
    )
    
    # Calculate net revenue
    sales_summary['net_revenue'] = sales_summary['total_sales'] - sales_summary['total_discount']

    # --- Product-wise Sales Report with Profit Calculation ---
    product_sales = (
        InvoiceItem.objects.values(
            "purchase__product_name", 
            "purchase__category__name",
            "purchase__subcategory__name",
            "purchase__product_rate",  # Cost price
            "purchase__sale_rate"      # Selling price
        )
        .annotate(
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
    category_sales = (
        InvoiceItem.objects.values("purchase__category__name")
        .annotate(
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
    subcategory_sales = (
        InvoiceItem.objects.values(
            "purchase__category__name",
            "purchase__subcategory__name"
        )
        .annotate(
            total_qty=Coalesce(Sum("quantity"), Value(0), output_field=IntegerField()),
            total_amount=Coalesce(Sum("total"), Value(Decimal(0)), output_field=DecimalField()),
            total_cost=Coalesce(Sum(F("quantity") * F("purchase__product_rate")), Value(Decimal(0)), output_field=DecimalField()),
            profit=Coalesce(Sum("total"), Value(Decimal(0)), output_field=DecimalField()) - 
                   Coalesce(Sum(F("quantity") * F("purchase__product_rate")), Value(Decimal(0)), output_field=DecimalField())
        )
        .order_by("-profit")  # Sort by annotated profit field
    )

    # --- Billing List ---
    invoices = Invoice.objects.annotate(
        net_amount=F("total") - F("discount_amount")
    ).order_by("-total")  # Sort by total amount

    # --- Expired Purchase Report ---
    expired_purchases = Purchase.objects.filter(
        expire_date__lte=now().date() + timedelta(days=2)
    ).annotate(
        days_to_expiry=ExpressionWrapper(
            (F('expire_date') - now().date()) / timedelta(days=1),
            output_field=IntegerField()
        ),
        total_days=ExpressionWrapper(
            (F('expire_date') - F('date')) / timedelta(days=1),
            output_field=IntegerField()
        )
    ).order_by('days_to_expiry')

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
    low_stock = [item for item in stock_data if item.balance < 10][:5]

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
        "top_selling": top_selling,
        "high_profit_products": high_profit_products,
        "low_profit_products": low_profit_products,
        "low_stock": low_stock,
        "total_cost": total_cost,
        "total_profit": total_profit,
    }
    return render(request, "shop_report.html", context)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.db.models import Sum
from datetime import datetime, timedelta
from decimal import Decimal
import json
from .models import Invoice, Purchase, Category

@login_required
@user_passes_test(lambda u: not u.is_superuser)
def owner_dashboard(request):
    # Calculate totals
    total_income = Invoice.objects.aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    total_expenses = Purchase.objects.aggregate(Sum('total_rate'))['total_rate__sum'] or Decimal('0.00')
    
    # Ensure both are Decimal
    total_income = Decimal(str(total_income)) if total_income is not None else Decimal('0.00')
    total_expenses = Decimal(str(total_expenses)) if total_expenses is not None else Decimal('0.00')
    
    # Calculate net profit
    net_profit = total_income - total_expenses

    # Calculate percentage changes (previous period: same duration before current period)
    today = datetime.now().date()
    six_months_ago = today - timedelta(days=180)
    prev_income = Invoice.objects.filter(date__lt=six_months_ago).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    prev_expenses = Purchase.objects.filter(date__lt=six_months_ago).aggregate(Sum('total_rate'))['total_rate__sum'] or Decimal('0.00')
    
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
        month_income = Invoice.objects.filter(date__range=(month_start, month_end)).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
        month_expense = Purchase.objects.filter(date__range=(month_start, month_end)).aggregate(Sum('total_rate'))['total_rate__sum'] or Decimal('0.00')
        income_data.append(float(Decimal(str(month_income))))
        expense_data.append(float(Decimal(str(month_expense))))

    # Category sales data
    category_labels = []
    category_data = []
    for category in Category.objects.all():
        category_labels.append(category.name)
        category_total = InvoiceItem.objects.filter(purchase__category=category).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
        category_data.append(float(Decimal(str(category_total))))

    # Recent transactions and purchases
    recent_transactions = Invoice.objects.order_by('-date')[:5]
    recent_purchases = Purchase.objects.order_by('-date')[:5]

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

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import datetime, timedelta
from decimal import Decimal
import json
from .models import Invoice, Purchase, Category

@login_required
@user_passes_test(lambda u: not u.is_superuser)
def dashboard_data(request):
    period = request.GET.get('period', '6months')
    today = datetime.now().date()

    if period == '7days':
        days = 7
    elif period == '30days':
        days = 30
    elif period == '1year':
        days = 365
    else:  # 6months
        days = 180

    start_date = today - timedelta(days=days)
    prev_start_date = start_date - timedelta(days=days)

    # Calculate totals
    total_income = Invoice.objects.filter(date__gte=start_date).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    total_expenses = Purchase.objects.filter(date__gte=start_date).aggregate(Sum('total_rate'))['total_rate__sum'] or Decimal('0.00')
    
    total_income = Decimal(str(total_income)) if total_income is not None else Decimal('0.00')
    total_expenses = Decimal(str(total_expenses)) if total_expenses is not None else Decimal('0.00')
    
    net_profit = total_income - total_expenses

    prev_income = Invoice.objects.filter(date__range=(prev_start_date, start_date)).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
    prev_expenses = Purchase.objects.filter(date__range=(prev_start_date, start_date)).aggregate(Sum('total_rate'))['total_rate__sum'] or Decimal('0.00')
    
    prev_income = Decimal(str(prev_income)) if prev_income is not None else Decimal('0.00')
    prev_expenses = Decimal(str(prev_expenses)) if prev_expenses is not None else Decimal('0.00')
    
    prev_profit = prev_income - prev_expenses

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

    # Chart data
    chart_labels = []
    income_data = []
    expense_data = []
    if period == '7days':
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            chart_labels.append(day.strftime('%d %b'))
            day_income = Invoice.objects.filter(date=day).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
            day_expense = Purchase.objects.filter(date=day).aggregate(Sum('total_rate'))['total_rate__sum'] or Decimal('0.00')
            income_data.append(float(Decimal(str(day_income))))
            expense_data.append(float(Decimal(str(day_expense))))
    else:
        months = days // 30
        for i in range(months - 1, -1, -1):
            month_start = (today - timedelta(days=30 * i)).replace(day=1)
            month_end = month_start + timedelta(days=30)
            chart_labels.append(month_start.strftime('%b %Y'))
            month_income = Invoice.objects.filter(date__range=(month_start, month_end)).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
            month_expense = Purchase.objects.filter(date__range=(month_start, month_end)).aggregate(Sum('total_rate'))['total_rate__sum'] or Decimal('0.00')
            income_data.append(float(Decimal(str(month_income))))
            expense_data.append(float(Decimal(str(month_expense))))

    # Category sales data
    category_labels = []
    category_data = []
    for category in Category.objects.all():
        category_labels.append(category.name)
        category_total = InvoiceItem.objects.filter(purchase__category=category, invoice__date__gte=start_date).aggregate(Sum('total'))['total__sum'] or Decimal('0.00')
        category_data.append(float(Decimal(str(category_total))))

    data = {
        'totalIncome': float(total_income),
        'totalExpenses': float(total_expenses),
        'netProfit': float(net_profit),
        'incomeChange': float(income_change),
        'expenseChange': float(expense_change),
        'profitChange': float(profit_change),
        'chartLabels': chart_labels,
        'incomeData': income_data,
        'expenseData': expense_data,
        'categoryLabels': category_labels,
        'categoryData': category_data,
    }

    return JsonResponse(data)