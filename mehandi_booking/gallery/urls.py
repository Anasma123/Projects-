from django.urls import path
from . import views

urlpatterns = [
    path('', views.gallery, name='gallery'),
    path('design/<int:design_id>/', views.design_detail, name='design_detail'),
]