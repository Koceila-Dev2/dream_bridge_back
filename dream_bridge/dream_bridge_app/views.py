import tempfile
import uuid
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from .models import Dream
from .forms import DreamForm
from .tasks import process_dream_audio_task
from .services import get_daily_message





def home(request):
    if request.user.is_authenticated:
        return redirect('dream_bridge_app:dashboard')
    return render(request, 'dream_bridge_app/home.html')


@login_required
def dream_create_view(request):
    """
    Gère l'affichage du formulaire (GET) et son traitement (POST).
    """
    if request.method == 'POST':
        # Instancier le formulaire avec les données POST et les fichiers
        form = DreamForm(request.POST, request.FILES)
        
        # Vérifier si le formulaire est valide (ex: le fichier est bien présent)
        if form.is_valid():
            uploaded_file = request.FILES['audio']
            
            # Implémentation du pattern "Fichier Transitoire" 
            # 1. Créer un chemin de fichier temporaire unique
            temp_dir = tempfile.gettempdir()
            temp_filename = f"{uuid.uuid4()}_{uploaded_file.name}"
            temp_path = f"{temp_dir}/{temp_filename}"
            
            # 2. Écrire le contenu du fichier uploadé dans ce fichier temporaire
            with open(temp_path, 'wb+') as temp_f:
                for chunk in uploaded_file.chunks():
                    temp_f.write(chunk)
            
            # 3. Créer l'objet Dream dans la BDD (statut PENDING par défaut)
            dream = Dream.objects.create(user=request.user) 
            
            # 4. Lancer la tâche de fond Celery
            process_dream_audio_task.delay(str(dream.id), temp_path)
            
            # 5. Rediriger l'utilisateur vers la page de statut
            return redirect(reverse('dream-status', kwargs={'dream_id': dream.id}))
    else:
        # Si c'est une requête GET, créer un formulaire vide
        form = DreamForm()

    # Rendre le template en lui passant le formulaire dans le contexte
    return render(request, 'dream_bridge_app/narrate.html', {'form': form})
  
@login_required
def dashboard(request):
    return render(request, 'dream_bridge_app/dashboard.html') 
 
@login_required
def galerie_filtrée(request):
    emotion_filtrée = request.GET.get('emotion')
    date_filtrée = request.GET.get('created_at')

    images = Dream.objects.filter(status='COMPLETED', generated_image__isnull=False)


    if emotion_filtrée and emotion_filtrée != "all":
        images = images.filter(emotion=emotion_filtrée)

    if date_filtrée:
        images = images.filter(date__date=date_filtrée)


    # pour la liste déroulante des émotions
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
    """
    Affiche le statut d'un rêve, l'image générée si prête,
    et le message du jour (horoscope ou citation).
    """
    try:
        dream = Dream.objects.get(id=dream_id)
    except Dream.DoesNotExist:
        return redirect('dream_bridge_app:home')

    # --- NOUVEAU : récupérer le message du jour pour l'utilisateur ---
    daily_message = get_daily_message(request.user.id)

    return render(request, 'dream_bridge_app/dream_status.html', {
        'dream': dream,
        'daily_message': daily_message
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
            status_url = reverse('dream-status', kwargs={'dream_id': dream.id})
            return JsonResponse({'status': dream.status, 'status_url': status_url})
        else:
            return JsonResponse({'status': dream.status})

    except Dream.DoesNotExist:
        return JsonResponse({'status': 'NOT_FOUND'}, status=404)
