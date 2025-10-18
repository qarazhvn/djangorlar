from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('users/', views.users_list, name='users_list'),
    path('city-time/', views.city_time, name='city_time'),
    path('cnt/', views.counter, name='counter'),
]
