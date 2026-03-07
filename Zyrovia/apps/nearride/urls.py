from django.urls import path

from . import views

app_name = 'nearride'

urlpatterns = [
    path('', views.nearride_dashboard, name='dashboard'),
    path('categories/request/', views.request_ride_category, name='request-category'),
    path('categories/my-requests/', views.my_ride_category_requests, name='my-ride-category-requests'),
    path('notifications/', views.my_ride_notifications, name='my-notifications'),
    path('locations/request/', views.request_new_location, name='request-location'),
    path('locations/my-requests/', views.my_location_requests, name='my-location-requests'),
    path('driver/become/', views.become_driver, name='become-driver'),
    path('driver/dashboard/', views.driver_dashboard, name='driver-dashboard'),
    path('driver/<int:driver_id>/edit/', views.edit_driver, name='edit-driver'),
    path('driver/<int:driver_id>/delete/', views.delete_driver, name='delete-driver'),
    path('driver/<int:driver_id>/toggle-status/', views.toggle_driver_status, name='toggle-driver-status-by-id'),
    path('driver/toggle-status/', views.toggle_driver_status, name='toggle-driver-status'),
    path('rides/create/', views.create_ride_request, name='create-ride'),
    path('api/drivers/', views.available_drivers_api, name='available-drivers-api'),
    path('driver/requests/', views.driver_requests, name='driver-requests'),
    path('driver/requests/<int:ride_id>/accept/', views.accept_ride_request, name='accept-ride'),
    path('driver/requests/<int:ride_id>/reject/', views.reject_ride_request, name='reject-ride'),
    path('rides/<int:ride_id>/', views.ride_detail, name='ride-detail'),
]
