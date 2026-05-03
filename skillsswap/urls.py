from django.urls import path
from . import views

urlpatterns = [
    path('', views.skill_list, name='skill_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
]