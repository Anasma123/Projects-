from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin-home/', views.admin_home, name='admin_home'),
    path('user-home/', views.user_home, name='user_home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
]