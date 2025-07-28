from django.contrib import admin
from .models import (
    UserProfile,
    ProductCategory,
    ProductSubcategory,
    Product,
    Transaction,
    TransactionItem,
    Invoice,
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'business_name', 'created_at']
    search_fields = ['user__username', 'business_name']

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(ProductSubcategory)
class ProductSubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_at']
    search_fields = ['name', 'category__name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'subcategory', 'price', 'quantity', 'user']
    list_filter = ['category', 'subcategory']
    search_fields = ['name']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'category', 'amount', 'date']
    list_filter = ['type', 'category']
    search_fields = ['user__username', 'category']

@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'product', 'quantity', 'total_price']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['user', 'customer_name', 'total_amount', 'date']
    search_fields = ['customer_name', 'user__username']
