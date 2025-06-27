from django.urls import path

from .views import *

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('narrate/', dream_create_view, name='narrate'),
    path('dreams/<uuid:dream_id>/status/', dream_status_view, name='dream-status'),
    path('galerie/', views.galerie_filtrée, name='galerie'),

]