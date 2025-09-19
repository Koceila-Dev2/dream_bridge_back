from django.urls import path
from . import views
from .views import *

app_name = 'dream_bridge_app'

urlpatterns = [

    path('', views.home, name='home'),
    path('dreams/<uuid:dream_id>/status/', dream_status_view, name='dream-status'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('narrate/', dream_create_view, name='narrate'),
    path('galerie/', views.galerie_filtrée, name='galerie'),
    path('dreams/<uuid:dream_id>/status/', views.dream_status_view, name='dream-status'),
    path('api/dreams/<uuid:dream_id>/status/', views.check_dream_status_api, name='check-dream-status-api'),

]
