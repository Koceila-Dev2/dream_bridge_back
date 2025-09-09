from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.decorators.http import require_http_methods

from .forms import CustomUserCreationForm


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    # ton template d'inscription existant
    template_name = 'dream_bridge_app/register.html'
    success_url = reverse_lazy('login')


@require_http_methods(["GET", "POST"])
def logout_to_home(request):
    """
    Déconnecte l'utilisateur puis redirige vers la page d'accueil.
    Accepte GET et POST (évite les 405 si l'URL est ouverte directement).
    """
    logout(request)
    messages.success(request, "Vous avez été déconnecté.")
    return redirect('home')
