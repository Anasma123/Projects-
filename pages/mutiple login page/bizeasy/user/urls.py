from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.login_view, name='login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('owner/dashboard/', views.owner_dashboard, name='owner_dashboard'),
      path('logout/', LogoutView.as_view(), name='logout'),
]



