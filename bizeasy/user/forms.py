from django import forms
from .models import Category

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
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
            'total_rate': forms.NumberInput(attrs={'readonly': 'readonly'}),
            
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
from django import forms
from .models import Billing, BillingItem, Product

from django import forms
from .models import Billing

class BillingForm(forms.ModelForm):
    customer_name = forms.CharField(max_length=100, required=True, label="Customer Name")
    customer_number = forms.CharField(max_length=15, required=True, label="Customer Number", widget=forms.TextInput(attrs={'type': 'tel'}))

    class Meta:
        model = Billing
        fields = ['gst_percent', 'roundoff', 'customer_name', 'customer_number']

class BillingItemForm(forms.ModelForm):
    class Meta:
        model = BillingItem
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'product-select'}),
            'quantity': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the product field to show product_name from Purchase
        self.fields['product'].queryset = Product.objects.select_related('purchase').order_by('purchase__product_name')
        self.fields['product'].label_from_instance = lambda obj: obj.purchase.product_name

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')
        
        if product and quantity:
            if quantity > product.stock_quantity:
                raise forms.ValidationError(
                    f"Only {product.stock_quantity} available in stock for {product.purchase.product_name}"
                )
        return cleaned_data