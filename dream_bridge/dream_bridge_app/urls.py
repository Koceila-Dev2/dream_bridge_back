from django.urls import path

from . import views

urlpatterns = [
    path("homepage", views.home_page, name="home_page"),
]