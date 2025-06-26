from django.urls import path
from .views import dream_create_view, dream_status_view

urlpatterns = [
    path('', dream_create_view, name='home'),

    path('dreams/<uuid:dream_id>/status/', dream_status_view, name='dream-status'),
]