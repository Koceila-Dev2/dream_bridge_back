from django.urls import path

from . import views
from .views import dream_create_view, dream_status_view



urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('narrate/', dream_create_view, name='narrate'),
    path('dreams/<uuid:dream_id>/status/', dream_status_view, name='dream-status'),
    path('report/', views.dashboard_view, name='report'),
    path('galerie/', views.galerie_filtrée, name='galerie'),

]