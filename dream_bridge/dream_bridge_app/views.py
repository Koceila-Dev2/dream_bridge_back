# dream_bridge_app/views.py
import tempfile
import uuid
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Dream
from .forms import DreamForm
from .tasks import process_dream_audio_task  
from django.contrib.auth.decorators import login_required 


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
            
            # --- Implémentation du pattern "Fichier Transitoire" ---
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
            process_dream_audio_task.delay(dream.id, temp_path)
            
            # 5. Rediriger l'utilisateur vers la page de statut
            return redirect(reverse('dream-status', kwargs={'dream_id': dream.id}))
    else:
        # Si c'est une requête GET, créer un formulaire vide
        form = DreamForm()

    # Rendre le template en lui passant le formulaire dans le contexte
    return render(request, 'dream_bridge_app/home.html', {'form': form})

def dream_status_view(request, dream_id):
    """
    Affiche le statut d'un rêve. (Assure-toi que ce template existe aussi)
    """
    try:
        dream = Dream.objects.get(id=dream_id)
    except Dream.DoesNotExist:
        return redirect('home')

    return render(request, 'dream_bridge_app/dream_status.html', {'dream': dream})