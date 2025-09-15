import tempfile
import uuid
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
import time
from datetime import datetime
from time import localtime
from .models import Dream
from .forms import DreamForm
from .tasks import process_dream_audio_task
from .services import get_daily_message, update_daily_phrase_in_dream
import json
from django.shortcuts import render
from .metrics_dashboard import *

def home(request):
    if request.user.is_authenticated:
        return redirect('dream_bridge_app:dashboard')
 
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
            # 3. Créer l'objet Dream dans la BDD (statut PENDING par défaut)
            dream = Dream.objects.create(user=request.user) 
            
            # 4. Lancer la tâche de fond Celery
            process_dream_audio_task.delay(str(dream.id), temp_path)
            
            # 5. Rediriger l'utilisateur vers la page de statut
            return redirect(reverse('dream_bridge_app:dream-status', kwargs={'dream_id': dream.id}))
    else:
        form = DreamForm()
    return render(request, 'dream_bridge_app/narrate.html', {'form': form})


@login_required
def dashboard(request):
    """
    Affiche la phrase/horoscope du jour et l’enregistre dans le
    dernier rêve de l’utilisateur (1×/jour).
    """
    daily_message = get_daily_message(request.user.id)

    today_key = timezone.localdate().isoformat()
    if request.session.get("quote_saved_on") != today_key:
        try:
            update_daily_phrase_in_dream(request.user)  # écrit dans le dernier rêve s’il existe
        except Exception:
            pass
        request.session["quote_saved_on"] = today_key

    return render(request, 'dream_bridge_app/dashboard.html', {
        'daily_message': daily_message,
    })


@login_required
def galerie_filtrée(request):
    emotion_filtrée = request.GET.get('emotion')
    date_filtrée = request.GET.get('created_at')

    images = Dream.objects.filter(status='COMPLETED', generated_image__isnull=False)

    if emotion_filtrée and emotion_filtrée != "all":
        images = images.filter(emotion=emotion_filtrée)

    if date_filtrée:
        images = images.filter(created_at__date=date_filtrée)

    emotions_disponibles = Dream.objects.values_list('emotion', flat=True).distinct()

    return render(request, 'dream_bridge_app/galerie.html', {
        'images': images,
        'emotions': emotions_disponibles,
        'selected_emotion': emotion_filtrée,
        'selected_date': date_filtrée,
    })

@login_required
def library(request):
    return render(request, 'dream_bridge_app/library.html')


@login_required
def dream_status_view(request, dream_id):
    try:
        dream = Dream.objects.get(id=dream_id, user=request.user)
    except Dream.DoesNotExist:
        return redirect('dream_bridge_app:home')

    daily_message = get_daily_message(request.user.id)

    created_at_local = timezone.localtime(dream.created_at)  # version locale
    created_at_ts = int(created_at_local.timestamp() * 1000)  # timestamp en ms
    return render(request, 'dream_bridge_app/dream_status.html', {
        'dream': dream,
        'daily_message': daily_message,
        'created_at_timestamp': created_at_ts

    })

@login_required
def check_dream_status_api(request, dream_id):
    """
    Retourne le statut d'un rêve au format JSON.
    C'est cette vue que le JavaScript va appeler.
    """
    try:
        dream = Dream.objects.get(id=dream_id, user=request.user)
        # Si le rêve est terminé, on inclut l'URL de la page de statut complète
        # pour que le JavaScript puisse rediriger l'utilisateur.
        if dream.status == 'COMPLETED' or dream.status == 'FAILED':
            status_url = reverse('dream_bridge_app:dream-status', kwargs={'dream_id': dream.id})
            return JsonResponse({'status': dream.status, 'status_url': status_url})
        else:
            return JsonResponse({'status': dream.status})

    except Dream.DoesNotExist:
        return JsonResponse({'status': 'NOT_FOUND'}, status=404)

@login_required
def dashboard_view(request):
    user = request.user
    period = request.GET.get("period", "7d")

    td = total_dreams(user, period)
    freq = dream_frequency(user, period)
    ed = emotion_distribution(user, period)      # dict { "joy": 0.4, ... }
    trend = emotion_trend(user, period)          # list[dict] [{ "date": "2025-09-01", "joy":0.5, ... }, ...]

    context = {
        "total_dreams": td,
        "dream_frequency": freq,
        # sérialise en JSON pour que le template puisse utiliser safe JS directement
        "emotion_distribution": json.dumps(ed),
        "emotion_trend": json.dumps(trend),
        "period": period,
    }
    return render(request, "dream_bridge_app/report.html", context)