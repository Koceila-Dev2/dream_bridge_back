# dream_bridge_app/services.py

import os
from django.conf import settings
from django.core.files.base import ContentFile
from groq import Groq
from mistralai import Mistral
# Cet import est crucial pour reconnaître le type de fichier retourné par l'agent
from mistralai.models import ToolFileChunk

from .models import Dream

def get_system_prompt() -> str:
    """Lit le prompt système depuis context.txt ou fournit un fallback."""
    context_path = os.path.join(settings.BASE_DIR, 'dream_bridge_app', 'context.txt')
    try:
        with open(context_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print("Fichier context.txt non trouvé. Utilisation d'un prompt système par défaut.")
        return """
        Tu es un artiste onirique et un expert en interprétation des rêves. Ton rôle est de transformer la transcription d'un rêve en un prompt court, évocateur et très visuel pour un modèle de génération d'images.
        - Décris la scène, les personnages, l'ambiance (joyeuse, angoissante, surréaliste...).
        - Utilise un langage descriptif riche (couleurs, textures, lumières).
        - Conclus toujours par des mots-clés de style comme "photorealistic, cinematic lighting, high detail, 8k".
        - NE réponds QUE par le prompt, sans aucune phrase d'introduction ou de conclusion.
        """

def orchestrate_dream_generation(dream_id: str, audio_path: str) -> None:
    """
    Orchestre le pipeline complet avec Groq pour le texte et un agent Mistral AI pour l'image.
    """
    try:
        dream = Dream.objects.get(id=dream_id)
        dream.status = Dream.DreamStatus.PROCESSING
        dream.save(update_fields=['status'])

        # Initialisation des clients API
        groq_client = Groq(api_key=settings.GROQ_API_KEY)
        mistral_client = Mistral(api_key=settings.MISTRAL_API_KEY)

        # --- ÉTAPE 1 & 2: Transcription et Génération de Prompt (Groq) ---
        # Cette partie reste inchangée
        print(f"[{dream.id}] Étape 1 & 2: Traitement du texte...")
        with open(audio_path, "rb") as audio_file:
            transcription = groq_client.audio.transcriptions.create(
                file=audio_file, model="whisper-large-v3", language="fr"
            )
        dream.transcription = transcription.text
        
        completion = groq_client.chat.completions.create(
            model="llama3-70b-8192", 
            messages=[
                {"role": "system", "content": get_system_prompt()},
                {"role": "user", "content": dream.transcription}
            ]
        )
        image_prompt = completion.choices[0].message.content.strip()
        dream.image_prompt = image_prompt
        dream.save(update_fields=['transcription', 'image_prompt', 'updated_at'])
        print(f"[{dream.id}] Prompt généré : '{dream.image_prompt[:50]}...'")

        # --- ÉTAPE 3: Génération de l'Image avec un Agent Mistral AI ---
        print(f"[{dream.id}] Étape 3: Création de l'agent d'image Mistral...")
        
        image_agent = mistral_client.beta.agents.create(
            model="mistral-large-latest", # Utilisons un modèle récent et puissant
            name="Générateur d'images de rêves",
            description="Agent qui utilise un outil de génération d'images à partir d'un prompt texte.",
            instructions="Utilise l'outil de génération d'image pour créer une image basée sur le prompt fourni par l'utilisateur.",
            tools=[{"type": "image_generation"}],
        )

        print(f"[{dream.id}] Démarrage de la conversation avec l'agent...")
        conversation_response = mistral_client.beta.conversations.start(
            agent_id=image_agent.id,
            inputs=dream.image_prompt
        )
        
        # --- Extraction du fichier image depuis la réponse de l'agent ---
        file_bytes = None
        # La réponse de l'agent est dans le dernier message de la conversation
        last_output = conversation_response.outputs[-1] 
        
        for chunk in last_output.content:
            # On vérifie si un des morceaux de la réponse est un fichier
            if isinstance(chunk, ToolFileChunk):
                print(f"[{dream.id}] Fichier image trouvé (ID: {chunk.file_id}). Téléchargement...")
                file_bytes = mistral_client.files.download(file_id=chunk.file_id).read()
                break # On a trouvé notre image, on arrête de chercher
            
        if file_bytes is None:
            raise ValueError("L'agent Mistral n'a pas retourné de fichier image.")

        print(f"[{dream.id}] Image générée et téléchargée avec succès.")

        # --- ÉTAPE 4: Sauvegarde de l'Image ---
        image_name = f"dream_{dream.id}.png"
        dream.generated_image.save(image_name, ContentFile(file_bytes))
        
        dream.status = Dream.DreamStatus.COMPLETED
        dream.save(update_fields=['status', 'updated_at'])

    except Exception as e:
        print(f"[{dream_id}] ERREUR CRITIQUE : {e}")
        if 'dream' in locals():
            dream.status = Dream.DreamStatus.FAILED
            dream.error_message = f"Une erreur est survenue lors du traitement: {str(e)}"
            dream.save(update_fields=['status', 'error_message', 'updated_at'])

