# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import SignUpView, logout_to_home, profile_view

app_name = "accounts"

urlpatterns = [
    # Profil
    path("me/", profile_view, name="profile"),

    # Inscription
    path("signup/", SignUpView.as_view(), name="signup"),
    path("register/", SignUpView.as_view(), name="register"),  # alias

    # Connexion
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),

    path(
        "login/",
        auth_views.LoginView.as_view(template_name="dream_bridge_app/login_custom.html"),
        name="login",
    ),

    # Mot de passe oublié
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"),
        name="password_reset",
    ),

    # Déconnexion
    path("logout/", logout_to_home, name="logout"),
]
