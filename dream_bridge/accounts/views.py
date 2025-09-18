# accounts/views.py
from django.contrib.auth import logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.decorators.http import require_http_methods

from .forms import CustomUserCreationForm
from accounts.models import UserProfile
from dream_bridge_app.forms import UserForm, ProfileForm  # on réutilise ces formulaires

User = get_user_model()


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "dream_bridge_app/register.html"
    success_url = reverse_lazy("login")


@require_http_methods(["GET", "POST"])
def logout_to_home(request):
    """Déconnecte puis redirige vers l’accueil."""
    logout(request)
    messages.success(request, "Vous avez été déconnecté.")
    return redirect("dream_bridge_app:home")


@login_required
def profile_view(request):
    """
    Page profil : l’utilisateur peut modifier
    - prénom / nom / email
    - croit à l’astrologie (case à cocher)
    La date de naissance et le signe NE sont PAS modifiables ici.
    """
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        uform = UserForm(request.POST, instance=user)
        pform = ProfileForm(request.POST, instance=profile)

        if uform.is_valid() and pform.is_valid():
            uform.save()
            pform.save()
            messages.success(request, "Profil mis à jour.")
            return redirect("accounts:profile")
        messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        uform = UserForm(instance=user)
        pform = ProfileForm(instance=profile)

    # champs en lecture seule
    readonly = {
        "birth_date": profile.birth_date,
        "zodiac_sign": (profile.zodiac_sign or "").strip(),
    }

    return render(
        request,
        "accounts/profile.html",  # chemin template corrigé
        {
            "user_form": uform,
            "profile_form": pform,
            "readonly": readonly,  # clé harmonisée
        },
    )
