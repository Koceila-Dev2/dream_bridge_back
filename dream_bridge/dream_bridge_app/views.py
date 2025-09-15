# import tempfile
# import uuid

# from django.shortcuts import render, redirect
# from django.urls import reverse
# from django.db.models import Q
# from django.contrib.auth import login
# from django.contrib.auth.decorators import login_required

# from .models import Dream
# from .forms import DreamForm
# from .tasks import process_dream_audio_task
# from .services import get_daily_message





# def home(request):
#     if request.user.is_authenticated:
#         return redirect('dashboard')
#     return render(request, 'dream_bridge_app/home.html') 
  
  

# @login_required
# def dream_create_view(request):
#     """
#     Gère l'affichage du formulaire (GET) et son traitement (POST).
#     """
#     if request.method == 'POST':
#         # Instancier le formulaire avec les données POST et les fichiers
#         form = DreamForm(request.POST, request.FILES)
        
#         # Vérifier si le formulaire est valide (ex: le fichier est bien présent)
#         if form.is_valid():
#             uploaded_file = request.FILES['audio']
            
#             # --- Implémentation du pattern "Fichier Transitoire" ---
#             # 1. Créer un chemin de fichier temporaire unique
#             temp_dir = tempfile.gettempdir()
#             temp_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
#             temp_path = f"{temp_dir}/{temp_filename}"
            
#             # 2. Écrire le contenu du fichier uploadé dans ce fichier temporaire
#             with open(temp_path, 'wb+') as temp_f:
#                 for chunk in uploaded_file.chunks():
#                     temp_f.write(chunk)
            
#             # 3. Créer l'objet Dream dans la BDD (statut PENDING par défaut)
#             dream = Dream.objects.create(user=request.user) 
            
#             # 4. Lancer la tâche de fond Celery
#             process_dream_audio_task.delay(dream.id, temp_path)
            
#             # 5. Rediriger l'utilisateur vers la page de statut
#             return redirect(reverse('dream-status', kwargs={'dream_id': dream.id}))
#     else:
#         # Si c'est une requête GET, créer un formulaire vide
#         form = DreamForm()

#     # Rendre le template en lui passant le formulaire dans le contexte
#     return render(request, 'dream_bridge_app/narrate.html', {'form': form})
  
# @login_required
# def dashboard(request):
#     return render(request, 'dream_bridge_app/dashboard.html') 
 
# @login_required
# def galerie_filtrée(request):
#     emotion_filtrée = request.GET.get('emotion')
#     date_filtrée = request.GET.get('created_at')

#     images = Dream.objects.filter(status='COMPLETED', generated_image__isnull=False)


#     if emotion_filtrée and emotion_filtrée != "all":
#         images = images.filter(emotion=emotion_filtrée)

#     if date_filtrée:
#         images = images.filter(date__date=date_filtrée)


#     # pour la liste déroulante des émotions
#     emotions_disponibles = Dream.objects.values_list('emotion', flat=True).distinct()

#     return render(request, 'dream_bridge_app/galerie.html', {
#         'images': images,
#         'emotions': emotions_disponibles,
#         'selected_emotion': emotion_filtrée,
#         'selected_date': date_filtrée,
#     })
  
  

  
# @login_required
# def library(request):
#     return render(request, 'dream_bridge_app/library.html')
  
# @login_required
# def dream_status_view(request, dream_id):
#     """
#     Affiche le statut d'un rêve, l'image générée si prête,
#     et le message du jour (horoscope ou citation).
#     """
#     try:
#         dream = Dream.objects.get(id=dream_id)
#     except Dream.DoesNotExist:
#         return redirect('home')

#     # --- NOUVEAU : récupérer le message du jour pour l'utilisateur ---
#     daily_message = get_daily_message(request.user.id)

#     return render(request, 'dream_bridge_app/dream_status.html', {
#         'dream': dream,
#         'daily_message': daily_message
#     })

# import tempfile
# import uuid

# from django.shortcuts import render, redirect
# from django.urls import reverse
# from django.db.models import Q
# from django.contrib.auth import login
# from django.contrib.auth.decorators import login_required
# from django.utils import timezone  # ✅

# from .models import Dream
# from .forms import DreamForm
# from .tasks import process_dream_audio_task
# from .services import get_daily_message, update_daily_phrase_in_dream  # ✅


# def home(request):
#     # ✅ Si connecté, on met à jour la phrase 1x/jour PUIS on redirige vers le dashboard
#     if request.user.is_authenticated:
#         today = timezone.localdate().isoformat()
#         if request.session.get("daily_phrase_done") != today:
#             try:
#                 # écrit la phrase dans le DERNIER rêve de l'utilisateur (si existe)
#                 update_daily_phrase_in_dream(request.user)
#             except Exception:
#                 pass
#             else:
#                 request.session["daily_phrase_done"] = today
#         return redirect('dashboard')
#     return render(request, 'dream_bridge_app/home.html')


# @login_required
# def dream_create_view(request):
#     """
#     Gère l'affichage du formulaire (GET) et son traitement (POST).
#     """
#     if request.method == 'POST':
#         form = DreamForm(request.POST, request.FILES)

#         if form.is_valid():
#             uploaded_file = request.FILES['audio']

#             # --- Fichier temporaire ---
#             temp_dir = tempfile.gettempdir()
#             temp_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
#             temp_path = f"{temp_dir}/{temp_filename}"

#             with open(temp_path, 'wb+') as temp_f:
#                 for chunk in uploaded_file.chunks():
#                     temp_f.write(chunk)

#             # Création du rêve (PENDING)
#             dream = Dream.objects.create(user=request.user)

#             # Lancer la tâche de fond Celery
#             process_dream_audio_task.delay(dream.id, temp_path)

#             # Redirection vers le statut
#             return redirect(reverse('dream-status', kwargs={'dream_id': dream.id}))
#     else:
#         form = DreamForm()

#     return render(request, 'dream_bridge_app/narrate.html', {'form': form})


# @login_required
# def dashboard(request):
#     # ✅ On passe le dernier rêve au template pour afficher la phrase si dispo
#     latest = request.user.dreams.order_by('-created_at').first()
#     return render(request, 'dream_bridge_app/dashboard.html', {
#         'latest_dream': latest
#     })


# @login_required
# def galerie_filtrée(request):
#     emotion_filtrée = request.GET.get('emotion')
#     date_filtrée = request.GET.get('created_at')

#     images = Dream.objects.filter(status='COMPLETED', generated_image__isnull=False)

#     if emotion_filtrée and emotion_filtrée != "all":
#         images = images.filter(emotion=emotion_filtrée)

#     # NOTE: si tu veux filtrer par date de création, utilise created_at__date
#     if date_filtrée:
#         images = images.filter(created_at__date=date_filtrée)

#     emotions_disponibles = Dream.objects.values_list('emotion', flat=True).distinct()

#     return render(request, 'dream_bridge_app/galerie.html', {
#         'images': images,
#         'emotions': emotions_disponibles,
#         'selected_emotion': emotion_filtrée,
#         'selected_date': date_filtrée,
#     })


# @login_required
# def library(request):
#     return render(request, 'dream_bridge_app/library.html')


# @login_required
# def dream_status_view(request, dream_id):
#     """
#     Affiche le statut d'un rêve, l'image générée si prête,
#     et le message du jour (stocké dans Dream.phrase).
#     """
#     try:
#         dream = Dream.objects.get(id=dream_id, user=request.user)
#     except Dream.DoesNotExist:
#         return redirect('home')

#     # ✅ On force l’écriture de la phrase sur CE rêve (1x/jour si phrase_date existe)
#     try:
#         update_daily_phrase_in_dream(request.user, dream_id=str(dream.id))
#     except Exception:
#         pass

#     # Rafraîchir l'objet si besoin
#     dream.refresh_from_db(fields=['phrase'])

#     # Fallback si jamais aucune phrase n'a pu être écrite
#     daily_message = dream.phrase or get_daily_message(request.user.id)

#     return render(request, 'dream_bridge_app/dream_status.html', {
#         'dream': dream,
#         'daily_message': daily_message
#     })

# import tempfile
# import uuid

# from django.shortcuts import render, redirect
# from django.urls import reverse
# from django.contrib.auth.decorators import login_required

# from .models import Dream
# from .forms import DreamForm
# from .tasks import process_dream_audio_task
# from .services import get_daily_message  # ✅ plus d'update_daily_phrase_in_dream


# def home(request):
#     # Si connecté, on envoie vers le dashboard
#     if request.user.is_authenticated:
#         return redirect('dashboard')
#     # Visiteurs non connectés : on peut simplement afficher la home
#     # (si tu veux aussi une phrase ici pour les non-connectés, on pourra l’ajouter)
#     return render(request, 'dream_bridge_app/home.html')


# @login_required
# def dream_create_view(request):
#     """
#     Gère l'affichage du formulaire (GET) et son traitement (POST).
#     """
#     if request.method == 'POST':
#         form = DreamForm(request.POST, request.FILES)
#         if form.is_valid():
#             uploaded_file = request.FILES['audio']

#             # Fichier temporaire
#             temp_dir = tempfile.gettempdir()
#             temp_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
#             temp_path = f"{temp_dir}/{temp_filename}"

#             with open(temp_path, 'wb+') as temp_f:
#                 for chunk in uploaded_file.chunks():
#                     temp_f.write(chunk)

#             # Création du rêve (PENDING)
#             dream = Dream.objects.create(user=request.user)

#             # Lancer la tâche de fond Celery
#             process_dream_audio_task.delay(dream.id, temp_path)

#             # Redirection vers le statut
#             return redirect(reverse('dream-status', kwargs={'dream_id': dream.id}))
#     else:
#         form = DreamForm()

#     return render(request, 'dream_bridge_app/narrate.html', {'form': form})


# @login_required
# def dashboard(request):
#     """
#     Affiche le dashboard + la phrase du jour indépendante des rêves.
#     """
#     daily_message = get_daily_message(request.user.id)  # ✅ pas de lien avec un rêve
#     return render(request, 'dream_bridge_app/dashboard.html', {
#         'daily_message': daily_message
#     })


# @login_required
# def galerie_filtrée(request):
#     emotion_filtrée = request.GET.get('emotion')
#     date_filtrée = request.GET.get('created_at')

#     images = Dream.objects.filter(status='COMPLETED', generated_image__isnull=False)

#     if emotion_filtrée and emotion_filtrée != "all":
#         images = images.filter(emotion=emotion_filtrée)

#     # Filtre de date sur created_at__date
#     if date_filtrée:
#         images = images.filter(created_at__date=date_filtrée)

#     emotions_disponibles = Dream.objects.values_list('emotion', flat=True).distinct()

#     return render(request, 'dream_bridge_app/galerie.html', {
#         'images': images,
#         'emotions': emotions_disponibles,
#         'selected_emotion': emotion_filtrée,
#         'selected_date': date_filtrée,
#     })


# @login_required
# def library(request):
#     return render(request, 'dream_bridge_app/library.html')


# @login_required
# def dream_status_view(request, dream_id):
#     """
#     Statut d’un rêve. On montre aussi la phrase du jour indépendante.
#     """
#     try:
#         dream = Dream.objects.get(id=dream_id, user=request.user)
#     except Dream.DoesNotExist:
#         return redirect('home')

#     daily_message = get_daily_message(request.user.id)  # ✅ indépendant
#     return render(request, 'dream_bridge_app/dream_status.html', {
#         'dream': dream,
#         'daily_message': daily_message
#     })


# dream_bridge_app/views.py
# import tempfile
# import uuid

# from django.shortcuts import render, redirect
# from django.urls import reverse
# from django.contrib.auth.decorators import login_required
# from django.utils import timezone

# from .models import Dream
# from .forms import DreamForm
# from .tasks import process_dream_audio_task
# from .services import get_daily_message   # ⬅️ on ne garde plus update_daily_phrase_in_dream


# def home(request):
#     # Si connecté, on va au tableau de bord
#     if request.user.is_authenticated:
#         return redirect('dashboard')
#     return render(request, 'dream_bridge_app/home.html')


# @login_required
# def dream_create_view(request):
#     if request.method == 'POST':
#         form = DreamForm(request.POST, request.FILES)
#         if form.is_valid():
#             uploaded_file = request.FILES['audio']
#             temp_dir = tempfile.gettempdir()
#             temp_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
#             temp_path = f"{temp_dir}/{temp_filename}"
#             with open(temp_path, 'wb+') as temp_f:
#                 for chunk in uploaded_file.chunks():
#                     temp_f.write(chunk)

#             dream = Dream.objects.create(user=request.user)
#             process_dream_audio_task.delay(dream.id, temp_path)
#             return redirect(reverse('dream-status', kwargs={'dream_id': dream.id}))
#     else:
#         form = DreamForm()
#     return render(request, 'dream_bridge_app/narrate.html', {'form': form})


# @login_required
# def dashboard(request):
#     # ⬇️ On récupère la phrase/horoscope du jour à l'affichage
#     daily_message = get_daily_message(request.user.id)

#     return render(request, 'dream_bridge_app/dashboard.html', {
#         'daily_message': daily_message,
#     })


# @login_required
# def galerie_filtrée(request):
#     emotion_filtrée = request.GET.get('emotion')
#     date_filtrée = request.GET.get('created_at')

#     images = Dream.objects.filter(status='COMPLETED', generated_image__isnull=False)

#     if emotion_filtrée and emotion_filtrée != "all":
#         images = images.filter(emotion=emotion_filtrée)

#     if date_filtrée:
#         images = images.filter(created_at__date=date_filtrée)

#     emotions_disponibles = Dream.objects.values_list('emotion', flat=True).distinct()

#     return render(request, 'dream_bridge_app/galerie.html', {
#         'images': images,
#         'emotions': emotions_disponibles,
#         'selected_emotion': emotion_filtrée,
#         'selected_date': date_filtrée,
#     })


# @login_required
# def library(request):
#     return render(request, 'dream_bridge_app/library.html')


# @login_required
# def dream_status_view(request, dream_id):
#     # (inchangé) – cette vue reste centrée sur un rêve précis si tu en as besoin
#     try:
#         dream = Dream.objects.get(id=dream_id, user=request.user)
#     except Dream.DoesNotExist:
#         return redirect('home')

#     daily_message = get_daily_message(request.user.id)
#     return render(request, 'dream_bridge_app/dream_status.html', {
#         'dream': dream,
#         'daily_message': daily_message
#     })

# import tempfile
# import uuid

# from django.shortcuts import render, redirect
# from django.urls import reverse
# from django.contrib.auth.decorators import login_required
# from django.utils import timezone

# from .models import Dream
# from .forms import DreamForm
# from .tasks import process_dream_audio_task
# from .services import (
#     get_daily_message,
#     update_daily_phrase_in_dream,   # ✅ on importe l’écriture en DB
# )


# def home(request):
#     # Si connecté, on va au tableau de bord
#     if request.user.is_authenticated:
#         return redirect('dashboard')
#     return render(request, 'dream_bridge_app/home.html')


# @login_required
# def dream_create_view(request):
#     if request.method == 'POST':
#         form = DreamForm(request.POST, request.FILES)
#         if form.is_valid():
#             uploaded_file = request.FILES['audio']
#             temp_dir = tempfile.gettempdir()
#             temp_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
#             temp_path = f"{temp_dir}/{temp_filename}"
#             with open(temp_path, 'wb+') as temp_f:
#                 for chunk in uploaded_file.chunks():
#                     temp_f.write(chunk)

#             dream = Dream.objects.create(user=request.user)
#             process_dream_audio_task.delay(dream.id, temp_path)
#             return redirect(reverse('dream-status', kwargs={'dream_id': dream.id}))
#     else:
#         form = DreamForm()
#     return render(request, 'dream_bridge_app/narrate.html', {'form': form})


# @login_required
# def dashboard(request):
#     """
#     Affiche la phrase/horoscope du jour et l’enregistre
#     dans le dernier rêve de l’utilisateur une fois par jour.
#     """
#     # 1) Toujours afficher
#     daily_message = get_daily_message(request.user.id)

#     # 2) Persister 1x/jour dans la DB (session pour éviter de réécrire à chaque refresh)
#     today_key = timezone.localdate().isoformat()
#     if request.session.get("quote_saved_on") != today_key:
#         try:
#             # Écrit dans le dernier rêve de l'utilisateur s'il existe
#             update_daily_phrase_in_dream(request.user)
#         except Exception:
#             # On ne bloque pas l’affichage si l’écriture échoue
#             pass
#         # Marque comme fait pour aujourd’hui (même en cas d’échec, on évite la boucle)
#         request.session["quote_saved_on"] = today_key

#     return render(request, 'dream_bridge_app/dashboard.html', {
#         'daily_message': daily_message,
#     })


# @login_required
# def galerie_filtrée(request):
#     emotion_filtrée = request.GET.get('emotion')
#     date_filtrée = request.GET.get('created_at')

#     images = Dream.objects.filter(status='COMPLETED', generated_image__isnull=False)

#     if emotion_filtrée and emotion_filtrée != "all":
#         images = images.filter(emotion=emotion_filtrée)

#     if date_filtrée:
#         images = images.filter(created_at__date=date_filtrée)

#     emotions_disponibles = Dream.objects.values_list('emotion', flat=True).distinct()

#     return render(request, 'dream_bridge_app/galerie.html', {
#         'images': images,
#         'emotions': emotions_disponibles,
#         'selected_emotion': emotion_filtrée,
#         'selected_date': date_filtrée,
#     })


# @login_required
# def library(request):
#     return render(request, 'dream_bridge_app/library.html')


# @login_required
# def dream_status_view(request, dream_id):
#     # Vue centrée sur un rêve précis (affichage standard)
#     try:
#         dream = Dream.objects.get(id=dream_id, user=request.user)
#     except Dream.DoesNotExist:
#         return redirect('home')

#     daily_message = get_daily_message(request.user.id)
#     return render(request, 'dream_bridge_app/dream_status.html', {
#         'dream': dream,
#         'daily_message': daily_message
#     })

import tempfile
import uuid

from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import Dream
from .forms import DreamForm
from .tasks import process_dream_audio_task
from .services import get_daily_message, update_daily_phrase_in_dream


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
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
            process_dream_audio_task.delay(dream.id, temp_path)
            return redirect(reverse('dream-status', kwargs={'dream_id': dream.id}))
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
        return redirect('home')

    daily_message = get_daily_message(request.user.id)
    return render(request, 'dream_bridge_app/dream_status.html', {
        'dream': dream,
        'daily_message': daily_message
    })
