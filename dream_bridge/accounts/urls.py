# # accounts/urls.py
# from django.urls import path
# from django.contrib.auth import views as auth_views # On importe les vues de Django
# from .views import SignUpView

# urlpatterns = [
#     # Inscription
#     path('signup/', SignUpView.as_view(template_name='accounts/signup.html'), name='signup'),
    
   
#     path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    
    
#     path('logout/', auth_views.LogoutView.as_view(), name='logout'),
# ]

# accounts/urls.py
# accounts/urls.py
# 

# from django.urls import path
# from django.contrib.auth import views as auth_views
# from .views import SignUpView, logout_to_home

# urlpatterns = [
#     # Inscription -> templates/dream_bridge_app/register.html
#     path('signup/', SignUpView.as_view(), name='signup'),

#     # Connexion -> templates/dream_bridge_app/login.html
#     path('login/', auth_views.LoginView.as_view(template_name='dream_bridge_app/login.html'), name='login'),

#     # Déconnexion -> accepte GET/POST et redirige vers 'home'
#     path('logout/', logout_to_home, name='logout'),
# ]

from django.urls import path
from django.contrib.auth import views as auth_views
from .views import SignUpView, logout_to_home

urlpatterns = [
    # Inscription
    path('signup/',   SignUpView.as_view(), name='signup'),
    # Alias pour éviter NoReverseMatch si un template utilise encore 'register'
    path('register/', SignUpView.as_view(), name='register'),

    # Connexion
    path('login/', auth_views.LoginView.as_view(
        template_name='dream_bridge_app/login.html'
    ), name='login'),

    # Mot de passe oublié (page de demande d’email)
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='dream_bridge_app/password_reset.html'
    ), name='password_reset'),

    # Déconnexion -> redirige toujours vers 'home'
    path('logout/', logout_to_home, name='logout'),
]
