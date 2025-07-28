from django import forms
from django.contrib.auth.models import User
from .models import ProductCategory

from .models import UserProfile, Product, Transaction, Invoice, ProductCategory


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    business_name = forms.CharField(max_length=100)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # This hashes the password
        if commit:
            user.save()
        return user


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = '__all__'

class ProductCategoryForm(forms.ModelForm):
    class Meta:
        model = ProductCategory
        fields = ['name']





                # from django import forms
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User
# from .models import UserProfile, ProductCategory, ProductSubcategory, Product, Transaction, Invoice
#
# class UserRegisterForm(UserCreationForm):
#     email = forms.EmailField()
#     business_name = forms.CharField(max_length=100)
#
#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password1', 'password2', 'business_name']
#
# class ProductCategoryForm(forms.ModelForm):
#     class Meta:
#         model = ProductCategory
#         fields = ['name']
#
# class ProductSubcategoryForm(forms.ModelForm):
#     class Meta:
#         model = ProductSubcategory
#         fields = ['category', 'name']
#
# class ProductForm(forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['name', 'category', 'subcategory', 'price', 'quantity', 'description']
#
# class TransactionForm(forms.ModelForm):
#     class Meta:
#         model = Transaction
#         fields = ['type', 'product', 'amount', 'date', 'note']
#         widgets = {'date': forms.DateInput(attrs={'type': 'date'})}
#
# class InvoiceForm(forms.ModelForm):
#     class Meta:
#         model = Invoice
#         fields = ['customer_name', 'items', 'tax_percent', 'date']
#         widgets = {'date': forms.DateInput(attrs={'type': 'date'}), 'items': forms.Textarea()}