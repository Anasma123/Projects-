from django.urls import path
from . import views

urlpatterns = [
    path('book/<int:design_id>/', views.book_design, name='book_design'),
    path('custom/', views.custom_booking, name='custom_booking'),
    path('list/', views.booking_list, name='booking_list'),
    path('detail/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('update/<int:booking_id>/', views.update_booking, name='update_booking'),
    path('edit/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('delete/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('payment/<int:booking_id>/', views.payment_process, name='payment_process'),
    path('payment/success/<int:booking_id>/', views.payment_success, name='payment_success'),
    path('payment/cancel/<int:booking_id>/', views.payment_cancel, name='payment_cancel'),
    path('get_subcategories/<int:category_id>/', views.get_subcategories, name='get_subcategories'),
    path('get_category_price/<int:category_id>/', views.get_category_price, name='get_category_price'),
]