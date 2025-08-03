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

@login_required
@user_passes_test(lambda u: not u.is_superuser)
def owner_dashboard(request):
    return render(request, 'owner_dashboard.html')


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

def list_purchases(request):
    query = request.GET.get('q')
    if query:
        purchases = Purchase.objects.filter(
            Q(product_name__icontains=query) | Q(date__icontains=query)
        )
    else:
        purchases = Purchase.objects.all().order_by('-date')
    return render(request, 'list_purchase.html', {'purchases': purchases})


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








# product management views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Purchase
from django.db.models import Case, When, Value, FloatField, F, ExpressionWrapper, Q
from django.contrib.auth.decorators import login_required

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











# billing management views.py

from django.http import JsonResponse
from .models import Category, SubCategory, Product
from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.contrib import messages
from .models import Billing, BillingItem
from .forms import BillingForm, BillingItemForm
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Billing, BillingItem, Product
from .forms import BillingForm, BillingItemForm
from django.forms import inlineformset_factory
# views.py
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from django.contrib import messages
from .models import Category, SubCategory, Product, Billing, BillingItem
from .forms import BillingForm, BillingItemForm

from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.contrib import messages
from .models import Billing, BillingItem, Product, Purchase, Category, SubCategory
from .forms import BillingForm, BillingItemForm
from django.http import JsonResponse

def ajax_load_subcategories(request):
    category_id = request.GET.get('category_id')
    subcategories = SubCategory.objects.filter(category_id=category_id).values('id', 'name')
    return JsonResponse(list(subcategories), safe=False)


from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Billing, BillingItem, Product, Purchase, Category, SubCategory
from .forms import BillingForm, BillingItemForm

def list_billing(request):
    # Get query parameters
    query = request.GET.get('q', '').strip()  # Search term
    sort_by = request.GET.get('sort', 'created_at')  # Default sort by created_at
    category_id = request.GET.get('category', '')
    subcategory_id = request.GET.get('subcategory', '')

    # Base queryset with related objects
    bills = Billing.objects.prefetch_related('items__product__purchase').order_by('-created_at')

    # Apply search filter
    if query:
        bills = bills.filter(
            Q(id__icontains=query) |
            Q(items__product__purchase__product_name__icontains=query) |
            Q(items__product__category__name__icontains=query) |
            Q(items__product__subcategory__name__icontains=query)
        ).distinct()

    # Apply category filter
    if category_id:
        bills = bills.filter(items__product__category_id=category_id).distinct()

    # Apply subcategory filter
    if subcategory_id:
        bills = bills.filter(items__product__subcategory_id=subcategory_id).distinct()

    # Apply sorting
    if sort_by == 'product_name':
        bills = bills.order_by('items__product__purchase__product_name')
    elif sort_by == 'category':
        bills = bills.order_by('items__product__category__name')
    elif sort_by == 'subcategory':
        bills = bills.order_by('items__product__subcategory__name')
    elif sort_by == 'created_at':
        bills = bills.order_by('-created_at')
    else:
        bills = bills.order_by('-created_at')  # Fallback

    # Get categories and subcategories for filter dropdowns
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()

    context = {
        'bills': bills,
        'search_query': query,
        'categories': categories,
        'subcategories': subcategories,
        'selected_category': category_id,
        'selected_subcategory': subcategory_id,
        'sort_by': sort_by,
    }
    return render(request, 'list_billing.html', context)

def edit_billing(request, pk):
    billing = get_object_or_404(Billing, pk=pk)
    BillingItemFormSet = inlineformset_factory(Billing, BillingItem, form=BillingItemForm, extra=0, can_delete=True)
    if request.method == 'POST':
        form = BillingForm(request.POST, instance=billing)
        formset = BillingItemFormSet(request.POST, instance=billing)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Billing updated.')
            return redirect('list_billing')
    else:
        form = BillingForm(instance=billing)
        formset = BillingItemFormSet(instance=billing)
    return render(request, 'edit_billing.html', {'form': form, 'formset': formset, 'billing': billing})

def delete_billing(request, pk):
    billing = get_object_or_404(Billing, pk=pk)
    if request.method == 'POST':
        billing.status = 'cancelled'
        billing.save()
        messages.success(request, 'Billing cancelled.')
        return redirect('list_billing')
    return render(request, 'delete_billing.html', {'billing': billing})


def add_billing(request):
    BillingItemFormSet = inlineformset_factory(
        Billing, BillingItem, form=BillingItemForm, extra=1, can_delete=True
    )
    
    if request.method == 'POST':
        form = BillingForm(request.POST)
        formset = BillingItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            billing = form.save(commit=False)
            billing.status = 'final'
            billing.save()
            formset.instance = billing
            instances = formset.save(commit=False)
            for instance in instances:
                product = instance.product
                if instance.quantity > product.stock_quantity:
                    messages.error(request, f'Not enough stock for {product.purchase.product_name}')
                    return redirect('add_billing')
                product.stock_quantity -= instance.quantity
                product.save()
                instance.save()
            for deleted_item in formset.deleted_objects:
                deleted_item.delete()
            messages.success(request, 'Billing saved successfully.')
            return redirect('list_billing')
    else:
        form = BillingForm()
        formset = BillingItemFormSet()
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all()
    products = Product.objects.select_related('purchase', 'category', 'subcategory').order_by('purchase__product_name')
    return render(request, 'add_billing.html', {
        'form': form,
        'formset': formset,
        'categories': categories,
        'subcategories': subcategories,
        'products': products,
    })

def ajax_load_products(request):
    subcategory_id = request.GET.get('subcategory_id')
    category_id = request.GET.get('category_id')
    search_term = request.GET.get('search', '').strip()
    
    products = Product.objects.select_related('purchase', 'category', 'subcategory')
    if category_id:
        products = products.filter(category_id=category_id)
    if subcategory_id:
        products = products.filter(subcategory_id=subcategory_id)
    if search_term:
        products = products.filter(purchase__product_name__icontains=search_term)
    products = products.order_by('purchase__product_name')
    
    data = []
    for product in products:
        final_price = product.get_final_price()
        data.append({
            'id': product.id,
            'name': product.purchase.product_name,
            'mrp': str(product.mrp),
            'product_rate': str(product.purchase_rate),
            'final_price': str(final_price) if final_price is not None else "0.00",
            'stock': product.stock_quantity,
        })
    return JsonResponse(data, safe=False)