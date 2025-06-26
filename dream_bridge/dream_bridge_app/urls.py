from django.urls import path

from . import views

urlpatterns = [
    path('galerie/', views.galerie_filtrée, name='galerie'),
]