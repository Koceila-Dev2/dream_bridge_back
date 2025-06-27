# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views # On importe les vues de Django
from .views import SignUpView

urlpatterns = [
    # Inscription
    path('signup/', SignUpView.as_view(template_name='accounts/signup.html'), name='signup'),
    
   
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    
    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]