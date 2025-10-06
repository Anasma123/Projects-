from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import (
    add_billing, delete_invoice, invoice_list, invoice_view,
    ajax_load_categories, ajax_load_subcategories, ajax_load_products, ajax_get_product_details
)

urlpatterns = [
    path('', views.login_view, name='login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
      path('logout/', LogoutView.as_view(), name='logout'),

      # Category management URLs
    path('add-category/', views.add_category, name='add_category'),
    path('categories/', views.list_category, name='list_category'),
    path('edit-category/<int:pk>/', views.edit_category, name='edit_category'),  # 👈 Add this
    path('delete-category/<int:pk>/', views.delete_category, name='delete_category'),  # optional

    # Subcategory management URLs
    path('subcategory/add/', views.add_subcategory, name='add_subcategory'),
    path('subcategory/list/', views.list_subcategory, name='list_subcategory'),
    path('subcategory/edit/<int:pk>/', views.edit_subcategory, name='edit_subcategory'),
    path('subcategory/delete/<int:pk>/', views.delete_subcategory, name='delete_subcategory'),


    #purchase management URLs

    path('purchases/', views.list_purchases, name='list_purchases'),
    path('purchases/add/', views.add_purchase, name='add_purchase'),
    path('purchases/edit/<int:pk>/', views.edit_purchase, name='edit_purchase'),
    path('purchases/delete/<int:pk>/', views.delete_purchase, name='delete_purchase'),

#     path('purchases/fixed/', views.fixed_purchases, name='fixed_purchases'),
# path('purchases/fixed/edit/<int:pk>/', views.edit_purchase_fixed, name='edit_purchase_fixed'),


    #product management URLs

    path('products/', views.list_products, name='list_products'),
    path('products/staff/', views.list_products_staff, name='list_products_staff'),  # Fixed by adding a trailing slash
    path('products/add-discount/<int:purchase_id>/', views.add_discount, name='add_discount'),
    path('products/view-discount/', views.view_discount, name='view_discount'),
    path('dashboard/', views.owner_dashboard, name='owner_dashboard'),
    # path('set-product-discount/<int:product_id>/', views.set_product_discount, name='set_product_discount'),

    path("stock-report/", views.stock_report, name="stock_report"),
    # billing management URLs


    # path('billing/', views.billing_list, name='billing_list'),
    # path('billing/add/', views.add_billing, name='add_billing'),
    # path('ajax/load-products/', views.ajax_load_products, name='ajax_load_products'),
    # path('ajax/load-subcategories/', views.ajax_load_subcategories, name='ajax_load_subcategories'),
    # path('ajax/get-purchase-details/', views.ajax_load_purchase_details, name='ajax_load_purchase_details'),



    path('billing/add/', views.add_billing, name='add_billing'),
    path('ajax/create-invoice/', views.add_billing, name='ajax_create_invoice'),
    path('billing/view/<int:invoice_id>/', views.invoice_view, name='invoice_view'),
    path('billing/list/', views.invoice_list, name='invoice_list'),
    path('ajax/load-categories/', views.ajax_load_categories, name='ajax_load_categories'),
    path('ajax/load-subcategories/', views.ajax_load_subcategories, name='ajax_load_subcategories'),
    path('ajax/load-products/', views.ajax_load_products, name='ajax_load_products'),
    path('ajax/get-product-details/', views.ajax_get_product_details, name='ajax_get_product_details'),
    path('billing/delete/<int:invoice_id>/', views.delete_invoice, name='delete_invoice'),




    path("dashboard/shop_report/", views.shop_report, name="shop_report"),
    path('api/dashboard-data/', views.dashboard_data, name='dashboard_data'),
    
    ]
   


    



