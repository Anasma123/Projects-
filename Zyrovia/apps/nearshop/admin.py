from django.contrib import admin

from .models import Offer, Product, Shop, ShopCategory, ShopCategoryRequest, ShopChat, ShopRating


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop_name', 'owner', 'category', 'shop_category', 'is_verified', 'average_rating', 'created_at')
    list_filter = ('category', 'is_verified')
    search_fields = ('shop_name', 'owner__full_name', 'owner__phone_number')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name', 'shop', 'price', 'stock_quantity', 'is_available')
    list_filter = ('category', 'is_available')
    search_fields = ('product_name', 'shop__shop_name')


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'shop', 'discount_percent', 'valid_until')
    list_filter = ('discount_percent',)


@admin.register(ShopChat)
class ShopChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop', 'sender', 'timestamp')


@admin.register(ShopRating)
class ShopRatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop', 'user', 'rating', 'created_at')
    list_filter = ('rating',)


@admin.register(ShopCategory)
class ShopCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)


@admin.register(ShopCategoryRequest)
class ShopCategoryRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'requested_by', 'category_name', 'status', 'created_at', 'reviewed_at')
    list_filter = ('status',)
    search_fields = ('requested_by__full_name', 'category_name')
