from django.urls import path

from . import views

app_name = 'locations'

urlpatterns = [
    path('api/states/', views.states_api, name='states-api'),
    path('api/districts/', views.districts_api, name='districts-api'),
    path('api/localities/', views.localities_api, name='localities-api'),
]
