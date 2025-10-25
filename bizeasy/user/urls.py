from django.urls import path
from . import views
from . import views_test
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),

    # Test URLs
    path('test/add-discount/<int:purchase_id>/', views_test.test_add_discount, name='test_add_discount'),

    # Category management URLs
    path('add-category/', views.add_category, name='add_category'),
    path('categories/', views.list_category, name='list_category'),
    path('edit-category/<int:pk>/', views.edit_category, name='edit_category'),
    path('delete-category/<int:pk>/', views.delete_category, name='delete_category'),

    # Subcategory management URLs
    path('subcategory/add/', views.add_subcategory, name='add_subcategory'),
    path('subcategory/list/', views.list_subcategory, name='list_subcategory'),
    path('subcategory/edit/<int:pk>/', views.edit_subcategory, name='edit_subcategory'),
    path('subcategory/delete/<int:pk>/', views.delete_subcategory, name='delete_subcategory'),

    # Purchase management URLs
    path('purchases/', views.list_purchases, name='list_purchases'),
    path('purchases/add/', views.add_purchase, name='add_purchase'),
    path('purchases/edit/<int:pk>/', views.edit_purchase, name='edit_purchase'),
    path('purchases/delete/<int:pk>/', views.delete_purchase, name='delete_purchase'),
    path('purchases/remove/<int:pk>/', views.remove_purchase, name='remove_purchase'),

    # Product management URLs
    path('products/', views.list_products, name='list_products'),
    path('products/staff/', views.list_products_staff, name='list_products_staff'),
    path('products/add-discount/<int:purchase_id>/', views.add_discount, name='add_discount'),
    path('products/view-discount/', views.view_discount, name='view_discount'),
    path('products/delete-discount/<int:purchase_id>/', views.delete_discount, name='delete_discount'),
    path('products/remove-expired-discounts/', views.remove_expired_discounts_view, name='remove_expired_discounts'),

    # Stock management URLs
    path("stock-report/", views.stock_report, name="stock_report"),
    path("stock/update/<int:purchase_id>/", views.update_stock, name="update_stock"),
    path("purchase-history/", views.purchase_history, name="purchase_history"),
    
    # Shop report URL
    path("dashboard/shop_report/", views.shop_report, name="shop_report"),
    path("dashboard/staff_wise_report/<int:staff_id>/", views.staff_wise_report, name="staff_wise_report"),
    
    # Billing/Invoice URLs
    path("billing/", views.invoice_list, name="invoice_list"),
    path("billing/add/", views.add_billing, name="add_billing"),
    path("billing/<int:invoice_id>/", views.invoice_view, name="invoice_view"),
    path("billing/<int:invoice_id>/print/", views.print_invoice, name="print_invoice"),
    path("billing/<int:invoice_id>/delete/", views.delete_invoice, name="delete_invoice"),
    path("billing/list/", views.billing_list, name="billing_list"),
    path("billing/list-billing/", views.list_billing, name="list_billing"),
    
    # Staff Management URLs
    path("staff/list/", views.staff_list, name="staff_list"),
    path("staff/add/", views.add_staff, name="add_staff"),
    path("staff/edit/<int:staff_id>/", views.edit_staff, name="edit_staff"),
    path("staff/delete/<int:staff_id>/", views.delete_staff, name="delete_staff"),
    
    # AJAX endpoints for billing
    path("ajax/load-subcategories/", views.load_subcategories, name="load_subcategories"),
    path("ajax/load-products/", views.load_products, name="load_products"),
    path("ajax/get-product-details/", views.get_product_details, name="get_product_details"),

    # API endpoints for dashboard
    path("api/dashboard-data/", views.api_dashboard_data, name="api_dashboard_data"),
]