from django import forms
from .models import Category, SubCategory, Purchase, Product, Discount, Invoice, InvoiceItem, SellingProduct

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Category Name'}),
        }

# subcategory form

from django import forms
from .models import SubCategory

class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['category', 'name', 'description']


# purchase form

from django import forms
from .models import Purchase

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = [
            'product_name',
            'category',
            'subcategory',
            'quantity',
            'product_rate',
            'total_rate',
            'sale_rate',  # Added for sale rate
            'date',
            'mrp',
            'notes',
            'expire_date' ,
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
            'total_rate': forms.NumberInput(attrs={'readonly': 'readonly'}),
            'expire_date': forms.DateInput(attrs={'type': 'date'}),
            
        }
    def save(self, commit=True):
        inst = super().save(commit=False)
    # Debug output - remove after testing
        print(f"Saving purchase - sale_rate: {self.cleaned_data.get('sale_rate')}")
    
        selling = self.cleaned_data.get('sale_rate')
        if selling is not None:
            inst.sale_rate = selling
        if commit:
            inst.save()
        return inst

    def clean(self):
        cleaned_data = super().clean()
        quantity = cleaned_data.get('quantity')
        rate = cleaned_data.get('product_rate')
        sale_rate = cleaned_data.get('sale_rate')

        if quantity and rate:
            cleaned_data['total_rate'] = quantity * rate
        if sale_rate is None:
            cleaned_data['sale_rate'] = 0  # or some default value  

        return cleaned_data
    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class PurchaseEditForm(PurchaseForm):
    # Extends the same fields, with one additional field: change_price
    change_price = forms.FloatField(required=False, label='Change Price')

    class Meta(PurchaseForm.Meta):
        fields = PurchaseForm.Meta.fields + ['change_price']


# product form

from django import forms
from .models import Product, SellingProduct

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'subcategory', 'mrp', 'purchase_rate']

class SellingProductForm(forms.ModelForm):
    class Meta:
        model = SellingProduct
        fields = ['product', 'selling_price']
        widgets = {
            'product': forms.HiddenInput(),  # hidden if using inline form
        }


# discount form

from django import forms
from .models import Discount

class DiscountForm(forms.ModelForm):
    class Meta:
        model = Discount
        fields = ['product', 'discount_percent', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }



# billing form


# INVOICE FORMS
# ---------------------------
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'bill_number',
            'date',
            'customer_name',
            'customer_phone',
            'customer_address',
            'discount_amount',
            # 'gst_percent',
            'roundoff',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'customer_address': forms.Textarea(attrs={'rows': 2}),
        }


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['purchase', 'quantity', 'rate', 'discount_percent']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['purchase'].queryset = Product.objects.all()
