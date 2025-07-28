from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django import forms
from django.contrib.auth.models import User

from .forms import UserRegisterForm  # ✅ correct
from .models import UserProfile, Product, Transaction, Invoice, ProductCategory, ProductSubcategory


# Logout view
@login_required
def custom_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

# User Registration View
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Add any additional logic here
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    business_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        business_name = cleaned_data.get('business_name')
        if not business_name:
            self.add_error('business_name', 'Business name is required.')
        return cleaned_data


# User Login View
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

# User Logout View
def logout_user(request):
    logout(request)
    return redirect('login')

# Dashboard View
@login_required
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expense = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = income - expense
    return render(request, 'dashboard.html', {
        'transactions': transactions[:5],
        'income': income,
        'expense': expense,
        'balance': balance,
    })

# Add Transaction View
@login_required
def add_transaction(request):
    if request.method == 'POST':
        type = request.POST['type']
        category = request.POST['category']
        amount = float(request.POST['amount'])
        date = request.POST['date']
        note = request.POST['note']
        transaction = Transaction.objects.create(
            user=request.user,
            type=type,
            category=category,
            amount=amount,
            date=date,
            note=note
        )
        # Handle product items if present
        product_ids = request.POST.getlist('product')
        quantities = request.POST.getlist('quantity')
        for i in range(len(product_ids)):
            product = Product.objects.get(id=product_ids[i])
            qty = int(quantities[i])
            total = product.price * qty
            TransactionItem.objects.create(
                transaction=transaction,
                product=product,
                quantity=qty,
                total_price=total
            )
        messages.success(request, 'Transaction added successfully')
        return redirect('dashboard')

    products = Product.objects.filter(user=request.user)
    return render(request, 'add_transaction.html', {
        'products': products
    })

# View All Transactions
@login_required
def view_transactions(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'view_transactions.html', {'transactions': transactions})

# Delete Transaction
@login_required
def delete_transaction(request, id):
    transaction = get_object_or_404(Transaction, id=id, user=request.user)
    transaction.delete()
    messages.success(request, 'Transaction deleted')
    return redirect('view_transactions')

# Product List and Add View
@login_required
def manage_products(request):
    products = Product.objects.filter(user=request.user)
    categories = ProductCategory.objects.filter(user=request.user)
    if request.method == 'POST':
        name = request.POST['name']
        price = request.POST['price']
        category_id = request.POST['category']
        category = ProductCategory.objects.get(id=category_id)
        Product.objects.create(name=name, price=price, category=category, user=request.user)
        messages.success(request, 'Product added')
        return redirect('manage_products')
    return render(request, 'manage_products.html', {'products': products, 'categories': categories})

# Add Category
@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST['name']
        ProductCategory.objects.create(name=name, user=request.user)
        messages.success(request, 'Category added')
        return redirect('manage_products')
    return render(request, 'add_category.html')


class CustomLoginView(LoginView):
    template_name = 'login.html'  # This matches your template file

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password')
        return super().form_invalid(form)