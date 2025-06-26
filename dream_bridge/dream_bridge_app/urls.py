from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('galerie/', views.galerie_filtrée, name='galerie'),
]



urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='dream_bridge_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Réinitialisation du mot de passe
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='dream_bridge_app/password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='dream_bridge_app/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='dream_bridge_app/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='dream_bridge_app/password_reset_complete.html'), name='password_reset_complete'),
    path('narrate/', views.narrate, name='narrate'),
    path('galerie/', views.galerie_filtrée, name='galerie'),
]