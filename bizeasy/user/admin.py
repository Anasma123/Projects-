"""
Admin module for the Bizeasy application.
Registers models with the Django admin interface.
"""

# Django imports
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Local imports
from .models import CustomUser as User, Category, SubCategory, Purchase, Product, SellingProduct, Discount, Invoice, InvoiceItem


# ==============================================================================
# User Management Admin
# ==============================================================================

class UserAdmin(BaseUserAdmin):
    """Admin configuration for CustomUser model."""
    
    # Type ignore to help linter with the fieldsets concatenation
    fieldsets = BaseUserAdmin.fieldsets + (  # type: ignore
        ('Role Info', {'fields': ('role',)}),
    )


# ==============================================================================
# Category Management Admin
# ==============================================================================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""
    
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for SubCategory model."""
    
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'category__name')


# ==============================================================================
# Purchase Management Admin
# ==============================================================================

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    """Admin configuration for Purchase model."""
    
    list_display = ('product_name', 'category', 'subcategory', 'quantity', 'product_rate', 'date', 'is_deleted')
    list_filter = ('category', 'subcategory', 'date', 'is_deleted')
    search_fields = ('product_name', 'category__name', 'subcategory__name')
    date_hierarchy = 'date'


# ==============================================================================
# Product Management Admin
# ==============================================================================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model."""
    
    list_display = ('name', 'category', 'subcategory', 'mrp', 'purchase_rate', 'stock_quantity')
    list_filter = ('category', 'subcategory')
    search_fields = ('name', 'category__name', 'subcategory__name')


@admin.register(SellingProduct)
class SellingProductAdmin(admin.ModelAdmin):
    """Admin configuration for SellingProduct model."""
    
    list_display = ('product', 'selling_price', 'date_added')
    list_filter = ('date_added',)
    search_fields = ('product__name',)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    """Admin configuration for Discount model."""
    
    list_display = ('product', 'discount_percent', 'start_date', 'end_date', 'is_active')
    list_filter = ('start_date', 'end_date')
    search_fields = ('product__name',)


# ==============================================================================
# Billing/Invoice Admin
# ==============================================================================

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Admin configuration for Invoice model."""
    
    list_display = ('bill_number', 'customer_name', 'date', 'total', 'created_by')
    list_filter = ('date', 'created_by')
    search_fields = ('bill_number', 'customer_name')
    date_hierarchy = 'date'


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    """Admin configuration for InvoiceItem model."""
    
    list_display = ('invoice', 'purchase', 'quantity', 'rate', 'total')
    list_filter = ('invoice__date',)
    search_fields = ('invoice__bill_number', 'purchase__product_name')


# Register the User model with the custom admin
admin.site.register(User, UserAdmin)