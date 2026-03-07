from django.urls import path

from . import views

app_name = 'nearservice'

urlpatterns = [
    path('', views.nearservice_dashboard, name='dashboard'),
    path('categories/', views.categories_page, name='categories'),
    path('categories/new/', views.category_create, name='category-create'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='category-edit'),
    path('categories/request/', views.request_category, name='request-category'),
    path('categories/my-requests/', views.my_category_requests, name='my-category-requests'),
    path('providers/', views.provider_list, name='provider-list'),
    path('providers/<int:provider_id>/', views.provider_profile, name='provider-profile'),
    path('providers/become/', views.become_provider, name='become-provider'),
    path('providers/profile/', views.provider_profile_manage, name='provider-manage'),
    path('providers/toggle-availability/', views.toggle_availability, name='toggle-availability'),
    path('request-service/', views.request_service, name='request-service'),
    path('provider/dashboard/', views.provider_dashboard, name='provider-dashboard'),
    path('requests/<int:request_id>/', views.service_request_detail, name='request-detail'),
    path('requests/<int:request_id>/accept/', views.accept_request, name='accept-request'),
    path('requests/<int:request_id>/reject/', views.reject_request, name='reject-request'),
]
