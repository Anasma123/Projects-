from django.urls import path

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('actions/<str:action>/', views.protected_action, name='protected-action'),
]
