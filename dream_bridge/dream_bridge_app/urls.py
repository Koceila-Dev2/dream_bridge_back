from django.urls import path
from . import views
from .views import *

app_name = 'dream_bridge_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'), 
    path('narrate/', views.dream_create_view, name='narrate'),
    path('dreams/<uuid:dream_id>/status/', views.dream_status_view, name='dream-status'),  
    path('galerie/', views.galerie_filtrée, name='galerie'),
    path('api/dreams/<uuid:dream_id>/status/', views.check_dream_status_api, name='check-dream-status-api')
]
