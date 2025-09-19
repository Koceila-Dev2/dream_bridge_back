# dream_bridge_app/views.py
import tempfile
import uuid
import json

from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Dream
from .forms import DreamForm, UserForm, ProfileForm
from .tasks import process_dream_audio_task
from .metrics_dashboard import *
from .services import *

# ✅ importe ton modèle de profil
from accounts.models import UserProfile


def home(request):
    if request.user.is_authenticated:
        return redirect('dream_bridge_app:accueil')
    return render(request, 'dream_bridge_app/home.html')


@login_required
def dream_create_view(request):
    if request.method == 'POST':
        form = DreamForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['audio']
            temp_dir = tempfile.gettempdir()
            temp_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
            temp_path = f"{temp_dir}/{temp_filename}"
            with open(temp_path, 'wb+') as temp_f:
                for chunk in uploaded_file.chunks():
                    temp_f.write(chunk)

            dream = Dream.objects.create(user=request.user)
            process_dream_audio_task.delay(str(dream.id), temp_path)
            return redirect(reverse('dream_bridge_app:dream-status', kwargs={'dream_id': dream.id}))
    else:
        form = DreamForm()
    return render(request, 'dream_bridge_app/narrate.html', {'form': form})


@login_required
def dashboard(request):
    """Affiche la phrase/horoscope du jour et l’enregistre à CHAQUE affichage."""
    daily_message = get_daily_message(request.user.id)

    return render(request, 'dream_bridge_app/accueil.html', {
        'daily_message': daily_message,
    })


@login_required
def galerie_filtree(request):
    emotion_filtreedate_filtree = request.GET.get('emotion')
    date_filtree = request.GET.get('created_at')
    images = Dream.objects.filter(status='COMPLETED', generated_image__isnull=False, phrase__isnull=False).order_by('-created_at')

    if emotion_filtreedate_filtree and emotion_filtreedate_filtree != "all":
        images = images.filter(emotion=emotion_filtreedate_filtree)

    if date_filtree:
        images = images.filter(created_at__date=date_filtree)

    emotions_disponibles = (Dream.objects
                            .filter(user=request.user)
                            .values_list('emotion', flat=True)
                            .distinct()
                            .order_by('emotion'))

    return render(request, 'dream_bridge_app/galerie.html', {
        'images': images,
        'emotions': emotions_disponibles,
        'selected_emotion': emotion_filtreedate_filtree,
        'selected_date': date_filtree,
    })

@login_required
def library(request):
    return render(request, 'dream_bridge_app/library.html')


@login_required
def dream_status_view(request, dream_id):
    """
    Page d’un rêve : génère/affiche le message personnalisé.
    - Montre l’émotion dominante et la date locale.
    """
    dream = get_object_or_404(Dream, id=dream_id, user=request.user)

    if dream.status == Dream.DreamStatus.COMPLETED:
        try:
            generate_personal_message_for_dream(str(dream.id), force=True)
            dream.refresh_from_db(fields=["personal_phrase", "personal_phrase_date", "phrase", "phrase_date", "emotion"])
        except Exception:
            pass

    # Priorité d’affichage
    daily_message = dream.personal_phrase or dream.phrase or get_daily_message(request.user.id)

    # Données d’affichage
    created_at_local = timezone.localtime(dream.created_at)
    try:
        emotion_label = dream.get_emotion_display()
    except Exception:
        emotion_label = dream.emotion or "—"

    return render(request, 'dream_bridge_app/dream_status.html', {
        'dream': dream,
        'daily_message': daily_message,
        'created_at_local': created_at_local,
        'emotion_label': emotion_label,
    })


@login_required
def check_dream_status_api(request, dream_id):
    """Retourne le statut d'un rêve au format JSON."""
    try:
        dream = Dream.objects.get(id=dream_id, user=request.user)
        if dream.status in ('COMPLETED', 'FAILED'):
            status_url = reverse('dream_bridge_app:dream-status', kwargs={'dream_id': dream.id})
            return JsonResponse({'status': dream.status, 'status_url': status_url})
        return JsonResponse({'status': dream.status})
    except Dream.DoesNotExist:
        return JsonResponse({'status': 'NOT_FOUND'}, status=404)


@login_required
def report(request):
    user = request.user
    period = request.GET.get("period", "7d")
    selected_emotion = request.GET.get("emotion", "all")

    # Rêves filtrés
    dreams = get_dreams_in_period(user, period, emotion=selected_emotion)

    td = dreams.count()
    freq = dream_frequency(user, period, emotion=selected_emotion)
    ed = emotion_distribution(user, period, emotion=selected_emotion)

    # --- Nouvelle métrique : longueur moyenne des transcriptions ---
    transcription_data = get_transcription_trend(user, period, emotion=selected_emotion)

    context = {
        "total_dreams": td,
        "dream_frequency": freq,
        "emotion_distribution": json.dumps(ed),
        "transcription_trend": json.dumps(transcription_data),
        "period": period,
        "emotions": list(emotions_disponible(user)),
        "selected_emotion": selected_emotion,
    }

    return render(request, "dream_bridge_app/dashboard.html", context)



@login_required
def generate_personal_message_view(request, dream_id):
    """Bouton “Générer / Régénérer” depuis la galerie."""
    if request.method != "POST":
        return HttpResponseBadRequest("Méthode non autorisée.")

    dream = get_object_or_404(Dream, id=dream_id, user=request.user)
    try:
        generate_personal_message_for_dream(str(dream.id), force=True)
        messages.success(request, "Message personnalisé mis à jour.")
    except Exception as e:
        messages.error(request, f"Échec de la génération : {e}")

    return redirect('dream_bridge_app:galerie')


# =========================
# ✅ PAGE PROFIL UTILISATEUR
# =========================
@login_required
def profile_view(request):
    """
    Affiche les infos du user + profil (édition limitée).
    - Modifiables: first_name, last_name, email, believes_in_astrology
    - Non modifiables mais affichées: birth_date, zodiac_sign
    """
    # Assure-toi qu’un profil existe (si pas de signal post_save)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            # Le ProfileForm ne touche qu'à believes_in_astrology
            profile_form.save()
            messages.success(request, "Profil mis à jour.")
            return redirect('dream_bridge_app:profile')
        else:
            messages.error(request, "Merci de corriger les erreurs du formulaire.")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    # Valeurs read-only à afficher
    read_only = {
        "birth_date": profile.birth_date,
        "zodiac_sign": profile.zodiac_sign_text,  # propriété pratique dans ton modèle
    }

    return render(request, "dream_bridge_app/profile.html", {
        "user_form": user_form,
        "profile_form": profile_form,
        "read_only": read_only,
    })
