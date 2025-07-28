# from django.urls import path
# from . import views
#
# urlpatterns = [
#     path('', views.home, name='home'),  # root path
#     path('register/', views.register, name='register'),
#     path('dashboard/', views.dashboard, name='dashboard'),
#     path('products/', views.product_list, name='product_list'),
#     path('products/delete/<int:pk>/', views.product_delete, name='product_delete'),
#     path('transactions/', views.transaction_list, name='transaction_list'),
#     path('invoices/', views.invoice_list, name='invoice_list'),
#     path('invoices/<int:pk>/', views.invoice_detail, name='invoice_detail'),
#     path('invoices/<int:pk>/pdf/', views.generate_pdf, name='generate_pdf'),
# ]

# BizEasy/urls.py
from django.urls import path
from .views import register, CustomLoginView, custom_logout, dashboard

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('register/', register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', custom_logout, name='logout'),
]
