from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from decimal import Decimal
import re

# Local imports
from .models import Category, SubCategory, Purchase, Product, Discount, Invoice, InvoiceItem, SellingProduct, CustomUser


def sanitize_input(input_str):
    """Sanitize user input to prevent XSS attacks."""
    if input_str is None:
        return None
    # Convert to string and strip whitespace
    input_str = str(input_str).strip()
    # Remove any HTML tags
    sanitized = re.sub(r'<[^>]*>', '', input_str)
    # Remove any script tags (extra protection)
    sanitized = re.sub(r'<script.*?>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    return sanitized


# ==============================================================================
# Category Management Forms
# ==============================================================================

class CategoryForm(forms.ModelForm):
    """Form for creating and editing categories."""
    class Meta:
        model = Category
        fields = ['name','description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Category Name'}),
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError("Category name is required.")
        if len(name) < 2:
            raise ValidationError("Category name must be at least 2 characters long.")
        
        # Check for case-insensitive duplicates
        name_str = str(name).strip()
        # Exclude the current instance when editing
        existing_categories = Category._default_manager.filter(
            name__iexact=name_str
        )
        if self.instance and self.instance.pk:
            existing_categories = existing_categories.exclude(pk=self.instance.pk)
        
        if existing_categories.exists():
            raise ValidationError(f"A category with the name '{name_str}' already exists (case-insensitive).")
        
        return name


class SubCategoryForm(forms.ModelForm):
    """Form for creating and editing subcategories."""
    class Meta:
        model = SubCategory
        fields = ['category', 'name', 'description']
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError("Subcategory name is required.")
        if len(name) < 2:
            raise ValidationError("Subcategory name must be at least 2 characters long.")
        
        # Sanitize input
        name = sanitize_input(name)
        
        # Check for case-insensitive duplicates
        category = self.cleaned_data.get('category')
        if category and name:
            name_str = str(name).strip()
            # Exclude the current instance when editing
            existing_subcategories = SubCategory._default_manager.filter(
                category=category,
                name__iexact=name_str
            )
            if self.instance and self.instance.pk:
                existing_subcategories = existing_subcategories.exclude(pk=self.instance.pk)
            
            if existing_subcategories.exists():
                raise ValidationError(f"A subcategory with the name '{name_str}' already exists in this category (case-insensitive).")
        
        # Convert to title case for consistency
        if name:
            return str(name).strip().title()
        return name


# ==============================================================================
# Purchase Management Forms
# ==============================================================================

class PurchaseForm(forms.ModelForm):
    """Form for creating and editing purchases."""
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
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make sure expire_date field is properly initialized
        if 'expire_date' in self.fields:
            self.fields['expire_date'].required = False

    def clean_product_name(self):
        product_name = self.cleaned_data.get('product_name')
        if not product_name:
            raise ValidationError("Product name is required.")
        if len(product_name) < 2:
            raise ValidationError("Product name must be at least 2 characters long.")
        return product_name

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is None:
            raise ValidationError("Quantity is required.")
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean_product_rate(self):
        product_rate = self.cleaned_data.get('product_rate')
        if product_rate is None:
            raise ValidationError("Product rate is required.")
        if product_rate < 0:
            raise ValidationError("Product rate cannot be negative.")
        return product_rate

    def clean_mrp(self):
        mrp = self.cleaned_data.get('mrp')
        if mrp is None:
            raise ValidationError("MRP is required.")
        if mrp < 0:
            raise ValidationError("MRP cannot be negative.")
        return mrp

    def clean_sale_rate(self):
        sale_rate = self.cleaned_data.get('sale_rate')
        if sale_rate is not None and sale_rate < 0:
            raise ValidationError("Sale rate cannot be negative.")
        return sale_rate

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if not date:
            raise ValidationError("Date is required.")
        return date

    def clean_expire_date(self):
        expire_date = self.cleaned_data.get('expire_date')
        date = self.cleaned_data.get('date')
        if expire_date and date and expire_date < date:
            raise ValidationError("Expire date cannot be before the purchase date.")
        return expire_date

    def save(self, commit=True):
        instance = super().save(commit=False)
    
        # Handle all fields that might need special handling
        selling = self.cleaned_data.get('sale_rate')
        if selling is not None:
            instance.sale_rate = selling
            
        expire_date = self.cleaned_data.get('expire_date')
        # Always set expire_date, even if it's None
        instance.expire_date = expire_date
            
        if commit:
            instance.save()
        return instance

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is not None:
            quantity = cleaned_data.get('quantity')
            rate = cleaned_data.get('product_rate')
            mrp = cleaned_data.get('mrp')
            sale_rate = cleaned_data.get('sale_rate')

            if quantity and rate:
                cleaned_data['total_rate'] = quantity * rate
            
            # Validate that MRP is not less than product rate
            if mrp is not None and rate is not None and mrp < rate:
                raise ValidationError("MRP cannot be less than the product rate.")
            
            # Validate that sale rate is not greater than MRP
            if sale_rate is not None and mrp is not None and sale_rate > mrp:
                raise ValidationError("Sale rate cannot be greater than MRP.")
            
            # Validate that sale rate is not less than product rate
            if sale_rate is not None and rate is not None and sale_rate < rate:
                raise ValidationError("Sale rate cannot be less than the product rate.")
                
        return cleaned_data


class PurchaseEditForm(PurchaseForm):
    """Form for editing purchases with additional change_price field."""
    # Extends the same fields, with one additional field: change_price
    change_price = forms.FloatField(required=False, label='Change Price')

    class Meta(PurchaseForm.Meta):
        fields = PurchaseForm.Meta.fields + ['change_price']
    
    def clean_change_price(self):
        change_price = self.cleaned_data.get('change_price')
        if change_price is not None and change_price < 0:
            raise ValidationError("Change price cannot be negative.")
        return change_price


# ==============================================================================
# Product Management Forms
# ==============================================================================

class ProductForm(forms.ModelForm):
    """Form for creating and editing products."""
    class Meta:
        model = Product
        fields = ['name', 'category', 'subcategory', 'mrp', 'purchase_rate']
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError("Product name is required.")
        if len(name) < 2:
            raise ValidationError("Product name must be at least 2 characters long.")
        return name

    def clean_mrp(self):
        mrp = self.cleaned_data.get('mrp')
        if mrp is None:
            raise ValidationError("MRP is required.")
        if mrp <= 0:
            raise ValidationError("MRP must be greater than zero.")
        return mrp

    def clean_purchase_rate(self):
        purchase_rate = self.cleaned_data.get('purchase_rate')
        if purchase_rate is None:
            raise ValidationError("Purchase rate is required.")
        if purchase_rate <= 0:
            raise ValidationError("Purchase rate must be greater than zero.")
        return purchase_rate

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is not None:
            mrp = cleaned_data.get('mrp')
            purchase_rate = cleaned_data.get('purchase_rate')
            
            if mrp is not None and purchase_rate is not None and mrp < purchase_rate:
                raise ValidationError("MRP cannot be less than the purchase rate.")
        return cleaned_data


class SellingProductForm(forms.ModelForm):
    """Form for creating and editing selling products."""
    class Meta:
        model = SellingProduct
        fields = ['product', 'selling_price']
        widgets = {
            'product': forms.HiddenInput(),  # hidden if using inline form
        }
    
    def clean_selling_price(self):
        selling_price = self.cleaned_data.get('selling_price')
        if selling_price is None:
            raise ValidationError("Selling price is required.")
        if selling_price <= 0:
            raise ValidationError("Selling price must be greater than zero.")
        return selling_price


# ==============================================================================
# Discount Management Forms
# ==============================================================================

class DiscountForm(forms.ModelForm):
    """Form for creating and editing discounts."""
    class Meta:
        model = Discount
        fields = ['product', 'discount_percent', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean_discount_percent(self):
        discount_percent = self.cleaned_data.get('discount_percent')
        if discount_percent is None:
            raise ValidationError("Discount percentage is required.")
        if discount_percent < 0 or discount_percent > 100:
            raise ValidationError("Discount percentage must be between 0 and 100.")
        return discount_percent

    def clean_start_date(self):
        start_date = self.cleaned_data.get('start_date')
        if not start_date:
            raise ValidationError("Start date is required.")
        return start_date

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        start_date = self.cleaned_data.get('start_date')
        if not end_date:
            raise ValidationError("End date is required.")
        if start_date and end_date and end_date < start_date:
            raise ValidationError("End date cannot be before the start date.")
        return end_date

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is not None:
            product = cleaned_data.get('product')
            start_date = cleaned_data.get('start_date')
            end_date = cleaned_data.get('end_date')
            
            # Check for overlapping discounts for the same product
            if product and start_date and end_date:
                from django.db.models import Q
                # Use the model's _default_manager to avoid linter issues
                overlapping_discounts = Discount._default_manager.filter(
                    product=product,
                    start_date__lte=end_date,
                    end_date__gte=start_date
                ).exclude(pk=self.instance.pk if self.instance else None)
                
                if overlapping_discounts.exists():
                    raise ValidationError("There is already an active discount for this product during the selected period.")
        return cleaned_data


# ==============================================================================
# Billing/Invoice Forms
# ==============================================================================

class InvoiceForm(forms.ModelForm):
    """Form for creating and editing invoices."""
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
    
    def clean_customer_name(self):
        customer_name = self.cleaned_data.get('customer_name')
        if not customer_name:
            raise ValidationError("Customer name is required.")
        if len(customer_name) < 2:
            raise ValidationError("Customer name must be at least 2 characters long.")
        return customer_name

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if not date:
            raise ValidationError("Date is required.")
        return date

    def clean_discount_amount(self):
        discount_amount = self.cleaned_data.get('discount_amount')
        if discount_amount is None:
            discount_amount = Decimal('0.00')
        if discount_amount < 0:
            raise ValidationError("Discount amount cannot be negative.")
        return discount_amount

    def clean_roundoff(self):
        roundoff = self.cleaned_data.get('roundoff')
        if roundoff is None:
            roundoff = Decimal('0.00')
        return roundoff

    def clean_customer_phone(self):
        customer_phone = self.cleaned_data.get('customer_phone')
        if not customer_phone:
            raise ValidationError("Customer phone number is required.")
        
        # Remove any non-digit characters for validation
        digits_only = re.sub(r'\D', '', str(customer_phone))
        
        # Check if it's exactly 10 digits
        if len(digits_only) != 10:
            raise ValidationError("Phone number must be exactly 10 digits.")
        
        # Format the phone number as XXX-XXX-XXXX for storage
        formatted_phone = f"{digits_only[:3]}-{digits_only[3:6]}-{digits_only[6:]}"
        return formatted_phone


class InvoiceItemForm(forms.ModelForm):
    """Form for creating and editing invoice items."""
    class Meta:
        model = InvoiceItem
        fields = ['purchase', 'quantity', 'rate', 'discount_percent']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only set queryset if the field exists
        if 'purchase' in self.fields:
            # Use type checking to help linter understand this is a ModelChoiceField
            # This is a common Django pattern that linters sometimes don't recognize
            self.fields['purchase'].queryset = Purchase.objects.filter(is_deleted=False)  # type: ignore
    
    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity is None:
            raise ValidationError("Quantity is required.")
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean_rate(self):
        rate = self.cleaned_data.get('rate')
        if rate is None:
            raise ValidationError("Rate is required.")
        if rate < 0:
            raise ValidationError("Rate cannot be negative.")
        return rate

    def clean_discount_percent(self):
        discount_percent = self.cleaned_data.get('discount_percent')
        if discount_percent is not None and (discount_percent < 0 or discount_percent > 100):
            raise ValidationError("Discount percentage must be between 0 and 100.")
        return discount_percent

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is not None:
            purchase = cleaned_data.get('purchase')
            quantity = cleaned_data.get('quantity')
            
            # Check if there's enough stock
            if purchase and quantity and purchase.quantity < quantity:
                raise ValidationError(f"Not enough stock for {purchase.product_name}. Available: {purchase.quantity}, Requested: {quantity}")
        return cleaned_data


# ==============================================================================
# Staff Management Forms
# ==============================================================================

class StaffForm(forms.ModelForm):
    """Form for creating and editing staff members."""
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    
    class Meta:
        model = CustomUser
        fields = ['full_name', 'username', 'email', 'password', 'session_number', 'phone_number', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.instance_pk = kwargs.get('instance', None)
        if self.instance_pk:
            self.instance_pk = self.instance_pk.pk
        super().__init__(*args, **kwargs)
        # If this is an edit form, make password fields optional
        if self.instance_pk:
            self.fields['password'].required = False
            self.fields['confirm_password'].required = False
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            raise ValidationError("Username is required.")
        if len(username) < 2:
            raise ValidationError("Username must be at least 2 characters long.")
        
        # Sanitize input
        username = sanitize_input(username)
        
        # Check for case-insensitive duplicates (exclude current instance when editing)
        # This ensures "a" and "A" are treated as the same username
        if self.instance_pk:
            if CustomUser.objects.filter(username__iexact=username).exclude(pk=self.instance_pk).exists():
                raise ValidationError("A user with this username already exists. Username must be unique (case-insensitive).")
        else:
            if CustomUser.objects.filter(username__iexact=username).exists():
                raise ValidationError("A user with this username already exists. Username must be unique (case-insensitive).")
                
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email is required.")
        
        # Sanitize input
        email = sanitize_input(email)
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("Invalid email format.")
        
        # Check for duplicates (exclude current instance when editing)
        if self.instance_pk:
            if CustomUser.objects.filter(email=email).exclude(pk=self.instance_pk).exists():
                raise ValidationError("A user with this email already exists.")
        else:
            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError("A user with this email already exists.")
                
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Sanitize input
            phone_number = sanitize_input(phone_number)
            
            # Remove any non-digit characters for validation
            digits_only = re.sub(r'\D', '', str(phone_number))
            
            # Check if it's exactly 10 digits
            if len(digits_only) != 10:
                raise ValidationError("Phone number must be exactly 10 digits.")
            
            # Format the phone number as XXX-XXX-XXXX for storage
            formatted_phone = f"{digits_only[:3]}-{digits_only[3:6]}-{digits_only[6:]}"
            
            # Check for duplicates (exclude current instance when editing)
            if self.instance_pk:
                if CustomUser.objects.filter(phone_number=formatted_phone).exclude(pk=self.instance_pk).exists():
                    raise ValidationError("A user with this phone number already exists.")
            else:
                if CustomUser.objects.filter(phone_number=formatted_phone).exists():
                    raise ValidationError("A user with this phone number already exists.")
            
            return formatted_phone
        
        return phone_number
    
    def clean_password(self):
        password = self.cleaned_data.get('password')
        # Only validate password if it's provided (for edit form) or required (for add form)
        if password or not self.instance_pk:
            if not password and not self.instance_pk:
                raise ValidationError("Password is required.")
            if password and len(password) < 6:
                raise ValidationError("Password must be at least 6 characters long.")
        return password
    
    def clean_confirm_password(self):
        confirm_password = self.cleaned_data.get('confirm_password')
        password = self.cleaned_data.get('password')
        
        # Only validate if password is provided
        if password or confirm_password:
            if password != confirm_password:
                raise ValidationError("Passwords do not match.")
        return confirm_password
    
    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'staff'
        
        # Only set password if it's provided
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
            
        if commit:
            user.save()
        return user
