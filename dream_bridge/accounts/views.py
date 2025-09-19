# accounts/views.py
from django.contrib.auth import logout, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.decorators.http import require_http_methods

from .forms import CustomUserCreationForm
from accounts.models import UserProfile
from dream_bridge_app.forms import UserForm, ProfileForm  # réutilisés

User = get_user_model()


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:login")


@require_http_methods(["GET", "POST"])
def logout_to_home(request):
    """Déconnecte puis redirige vers la page de login."""
    logout(request)
    messages.success(request, "Vous avez été déconnecté.")
    return redirect("accounts:login")


@login_required
def profile_view(request):
    """
    Page profil simplifiée :
    - Modifiables : email, believes_in_astrology
    - Action séparée : changement de mot de passe
    - Plus d’édition du prénom/nom, plus de bloc de droite.
    """
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    # Forms par défaut (GET)
    user_form = UserForm(instance=user)
    profile_form = ProfileForm(instance=profile)
    password_form = PasswordChangeForm(user=user)

    if request.method == "POST":
        # 1) Soumission du bloc "Mot de passe"
        if "change_password" in request.POST:
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                # Rester connecté après changement de mot de passe
                update_session_auth_hash(request, user)
                messages.success(request, "Mot de passe mis à jour.")
                return redirect("accounts:profile")
            else:
                messages.error(request, "Veuillez corriger les erreurs du mot de passe.")
        else:
            # 2) Soumission du bloc "Informations du compte"
            # On veut empêcher toute modif de first_name/last_name :
            # on injecte silencieusement les valeurs actuelles pour la validation du UserForm
            data = request.POST.copy()
            data.setdefault("first_name", user.first_name or "")
            data.setdefault("last_name", user.last_name or "")

            user_form = UserForm(data, instance=user)
            profile_form = ProfileForm(request.POST, instance=profile)

            if user_form.is_valid() and profile_form.is_valid():
                # On ne sauvegarde effectivement que l'email côté utilisateur
                # (UserForm gère l'email; first/last_name restent identiques grâce au setdefault ci-dessus)
                user_form.save()
                profile_form.save()
                messages.success(request, "Profil mis à jour.")
                return redirect("accounts:profile")
            else:
                messages.error(request, "Veuillez corriger les erreurs du formulaire.")

    return render(
        request,
        "accounts/profile.html",
        {
            "user_form": user_form,
            "profile_form": profile_form,
            "password_form": password_form,
        },
    )
