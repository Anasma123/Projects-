from django.urls import path

from . import views

app_name = 'control'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('users/', views.user_management, name='users'),
    path('drivers/', views.driver_management, name='drivers'),
    path('shops/', views.shop_management, name='shops'),
    path('providers/', views.provider_management, name='providers'),
    path('categories/', views.category_management, name='categories'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='category-edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category-delete'),
    path('category-requests/', views.category_request_management, name='category-requests'),
    path('ride-categories/', views.ride_category_management, name='ride-categories'),
    path('ride-categories/<int:category_id>/edit/', views.ride_category_edit, name='ride-category-edit'),
    path('ride-categories/<int:category_id>/delete/', views.ride_category_delete, name='ride-category-delete'),
    path('ride-category-requests/', views.ride_category_request_management, name='ride-category-requests'),
    path('shop-categories/', views.shop_category_management, name='shop-categories'),
    path('shop-categories/<int:category_id>/edit/', views.shop_category_edit, name='shop-category-edit'),
    path('shop-categories/<int:category_id>/delete/', views.shop_category_delete, name='shop-category-delete'),
    path('shop-category-requests/', views.shop_category_request_management, name='shop-category-requests'),
    path('location-requests/', views.location_request_management, name='location-requests'),
    path('reports/', views.report_management, name='reports'),
    path('reports/create/', views.create_report, name='report-create'),
]
