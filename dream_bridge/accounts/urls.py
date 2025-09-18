
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import SignUpView, logout_to_home, profile_view

app_name = "accounts"



urlpatterns = [
    # Profil
    path("me/", profile_view, name="profile"),

    # Inscription
    path("signup/",   SignUpView.as_view(), name="signup"),

    # Connexion (UNE SEULE ROUTE)
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
            redirect_authenticated_user=True,
            extra_context=None,
        ),
        name="login",
    ),

    # Mot de passe oublié
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            success_url=__import__('django.urls').urls.reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"),
        name="password_reset_done",
    ),

    # Déconnexion
    path("logout/", logout_to_home, name="logout"),
]
