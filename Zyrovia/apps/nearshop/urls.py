from django.urls import path

from . import views

app_name = 'nearshop'

urlpatterns = [
    path('', views.nearshop_dashboard, name='dashboard'),
    path('categories/request/', views.request_shop_category, name='request-category'),
    path('categories/my-requests/', views.my_shop_category_requests, name='my-shop-category-requests'),
    path('shops/', views.shop_list, name='shop-list'),
    path('shops/<int:shop_id>/', views.shop_detail, name='shop-detail'),
    path('owner/register/', views.register_shop, name='register-shop'),
    path('owner/dashboard/', views.owner_dashboard, name='owner-dashboard'),
    path('owner/edit/', views.edit_shop, name='edit-shop'),
    path('owner/products/', views.product_management, name='product-management'),
    path('owner/products/<int:product_id>/edit/', views.edit_product, name='edit-product'),
    path('owner/products/<int:product_id>/delete/', views.delete_product, name='delete-product'),
    path('owner/offers/<int:offer_id>/delete/', views.delete_offer, name='delete-offer'),
]
