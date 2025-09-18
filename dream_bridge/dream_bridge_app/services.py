import os
import pickle
from datetime import datetime
import requests
from deep_translator import GoogleTranslator
import json 
import numpy as np 
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone
from groq import Groq
from mistralai import Mistral
from mistralai.models import ToolFileChunk

from .models import Dream


User = get_user_model()  # utilisé dans get_daily_message()

MISTRAL_API_KEY=settings.MISTRAL_API_KEY


def get_system_prompt() -> str:
    """Lit le prompt système depuis context.txt ou fournit un fallback."""
    context_path = os.path.join(settings.BASE_DIR, 'dream_bridge_app', 'context.txt')
    try:
        with open(context_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:

        return (
            "Tu es un artiste onirique et un expert en interprétation des rêves. "
            "Ton rôle est de transformer la transcription d'un rêve en un prompt court, "
            "évocateur et très visuel pour un modèle de génération d'images. "
            "- Décris la scène, les personnages, l'ambiance. "
            "- Utilise un langage descriptif riche (couleurs, textures, lumières). "
            "- Termine par des mots-clés de style : photorealistic, cinematic lighting, high detail, 8k. "
            "- Réponds uniquement par le prompt."
        )



def read_context_file(filename="context.txt"):
    """Lit un fichier de contexte depuis le dossier de l'application."""
    context_path = os.path.join(settings.BASE_DIR, 'dream_bridge_app', filename)
    try:
        with open(context_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Fichier {filename} non trouvé.")
        return ""
    





def get_emotion_from_text(transcription: str) -> str:
    """
    Analyse la transcription pour en déduire l'émotion principale en utilisant l'API Mistral.
    """
   

    try:
        mistral_client = Mistral(api_key=MISTRAL_API_KEY)

        system_prompt = read_context_file("context_emotion.txt")
        if not system_prompt:
            return "erreur"

        print("Appel à l'API Mistral pour l'analyse des émotions...")
        
        model = "mistral-large-latest"

        client = mistral_client

        chat_response = client.chat.complete(
            model = model,
            messages = [
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": f"Analyse le texte ci-dessous. Ta réponse doit être un dictionnaire JSON valide avec des émotions en clé et des scores entre 0 et 1 en valeur. Ne mets pas de texte, uniquement du JSON : {transcription}",
                },
            ],
            response_format={"type": "json_object",}
        )
        # --- FIN DE LA CORRECTION ---
        
        prediction_str = chat_response.choices[0].message.content
        emotions_scores = json.loads(prediction_str)
        
        if not emotions_scores:
            return "neutre"
            
        dominant_emotion = max(emotions_scores, key=emotions_scores.get)
        return dominant_emotion
            
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API Mistral : {e}")
        return "erreur"
    

def orchestrate_dream_generation(dream_id: str, audio_path: str) -> None:
    """Orchestre le pipeline (texte + image)."""
    try:
        dream = Dream.objects.get(id=dream_id)
        dream.status = Dream.DreamStatus.PROCESSING
        dream.save(update_fields=['status'])

        USE_SIMULATION = True

        if USE_SIMULATION:
            sim_path = os.path.join(settings.BASE_DIR, 'dream_bridge_app', 'simulation.pkl')
            with open(sim_path, 'rb') as f:
                simulation_data = pickle.load(f)
            dream.transcription = simulation_data['transcription']
            dream.image_prompt = simulation_data['image_prompt']
            file_bytes = simulation_data['image_bytes']
            dream.save(update_fields=['transcription', 'image_prompt', 'updated_at'])
        else:
            groq_client = Groq(api_key=settings.GROQ_API_KEY)
            mistral_client = Mistral(api_key=settings.MISTRAL_API_KEY)

            with open(audio_path, "rb") as audio_file:
                transcription = groq_client.audio.transcriptions.create(
                    file=audio_file, model="whisper-large-v3", language="fr"
                )
            dream.transcription = transcription.text


            print(f"[{dream.id}] Étape 2: Analyse des émotions...")
            dream.emotion = get_emotion_from_text(dream.transcription)
            dream.save(update_fields=['emotion'])
            
            completion = groq_client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": get_system_prompt()},
                    {"role": "user", "content": dream.transcription},
                ],
            )
            dream.image_prompt = completion.choices[0].message.content.strip()
            dream.save(update_fields=['transcription', 'image_prompt', 'updated_at'])

            image_agent = mistral_client.beta.agents.create(
                model="mistral-large-latest",
                name="Générateur d'images de rêves",
                description="Agent qui utilise un outil de génération d'images à partir d'un prompt texte.",
                instructions="Utilise l'outil de génération d'image pour créer une image basée sur le prompt fourni.",
                tools=[{"type": "image_generation"}],
            )

            conversation_response = mistral_client.beta.conversations.start(
                agent_id=image_agent.id, inputs=dream.image_prompt
            )
            file_bytes = None
            last_output = conversation_response.outputs[-1]
            for chunk in last_output.content:
                if isinstance(chunk, ToolFileChunk):
                    file_bytes = mistral_client.files.download(file_id=chunk.file_id).read()
                    break
            if file_bytes is None:
                raise ValueError("L'agent Mistral n'a pas retourné de fichier image.")

        image_name = f"dream_{dream.id}.png"
        dream.generated_image.save(image_name, ContentFile(file_bytes))
        dream.status = Dream.DreamStatus.COMPLETED
        dream.save(update_fields=['status', 'updated_at'])

    except Exception as e:
        if 'dream' in locals():
            dream.status = Dream.DreamStatus.FAILED
            dream.error_message = f"Une erreur est survenue lors du traitement: {str(e)}"
            dream.save(update_fields=['status', 'error_message', 'updated_at'])


# -------- Horoscope & citations --------

sign_map = {
    "belier": "aries", "bélier": "aries",
    "taureau": "taurus",
    "gemeaux": "gemini", "gémeaux": "gemini",
    "cancer": "cancer", "lion": "leo", "vierge": "virgo",
    "balance": "libra", "scorpion": "scorpio",
    "sagittaire": "sagittarius", "capricorne": "capricorn",
    "verseau": "aquarius", "poissons": "pisces"
}

ACCENTS = "éèêëàâäùûüôöç"
REPLACEMENTS = "eeeeaaauuuooc"

def remove_accents(text: str) -> str:
    return text.translate(str.maketrans(ACCENTS, REPLACEMENTS))

def get_astrological_sign(birth_date):
    d = birth_date.day
    m = birth_date.month
    if (m == 3 and d >= 21) or (m == 4 and d <= 19): return "bélier"
    if (m == 4 and d >= 20) or (m == 5 and d <= 20): return "taureau"
    if (m == 5 and d >= 21) or (m == 6 and d <= 20): return "gémeaux"
    if (m == 6 and d >= 21) or (m == 7 and d <= 22): return "cancer"
    if (m == 7 and d >= 23) or (m == 8 and d <= 22): return "lion"
    if (m == 8 and d >= 23) or (m == 9 and d <= 22): return "vierge"
    if (m == 9 and d >= 23) or (m == 10 and d <= 22): return "balance"
    if (m == 10 and d >= 23) or (m == 11 and d <= 21): return "scorpion"
    if (m == 11 and d >= 22) or (m == 12 and d <= 21): return "sagittaire"
    if (m == 12 and d >= 22) or (m == 1 and d <= 19): return "capricorne"
    if (m == 1 and d >= 20) or (m == 2 and d <= 18): return "verseau"
    return "poissons"

def get_quote_of_the_day() -> str:
    url = "https://zenquotes.io/api/today"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            quote = data[0]["q"]
            author = data[0]["a"]
            translated = GoogleTranslator(source='en', target='fr').translate(quote)
            return f"« {translated} » — {author}"
        return f"Erreur HTTP {r.status_code} lors de la récupération."
    except Exception as e:
        return f"Erreur lors de la requête : {e}"

def get_daily_message(user_id, day="TODAY") -> str:
    """Renvoie soit l'horoscope soit la citation du jour selon le flag utilisateur."""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return "Utilisateur non trouvé."

    # Vérifier si l'utilisateur a bien un profil
    if not hasattr(user, "profile"):
        return "Profil utilisateur introuvable."

    profile = user.profile  # ton UserProfile lié

    if profile.believes_in_astrology:
        # Horoscope
        birth_date = profile.birth_date
        if not birth_date:
            return "La date de naissance de l'utilisateur est inconnue."
        sign_fr = get_astrological_sign(birth_date)
        sign_en = sign_map.get(remove_accents(sign_fr.lower()))
        if not sign_en:
            return f"Signe astrologique '{sign_fr}' non reconnu."
        url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={sign_en.capitalize()}&day={day.upper()}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("success"):
                horoscope = data["data"]["horoscope_data"]
                translated = GoogleTranslator(source='en', target='fr').translate(horoscope)
                return f"Horoscope pour {user.get_full_name() or user.username} ({sign_fr.capitalize()}) :\n{translated}"
            return "Erreur : réponse non réussie de l'API."
        return f"Erreur HTTP {r.status_code} lors de la récupération."
    else:
        return get_quote_of_the_day()

def update_daily_phrase_in_dream(user, dream_id: str | None = None):
    """
    Écrit la phrase/horoscope du jour dans le rêve ciblé (ou le plus récent),
    1 fois par jour (via phrase_date). Retourne le Dream mis à jour ou None.
    """
    message = get_daily_message(user.id)
    today = timezone.localdate()

    qs = Dream.objects.filter(user=user)
    if dream_id:
        qs = qs.filter(id=dream_id)

    dream = qs.order_by('-created_at').first()
    if not dream:
        return None

    if dream.phrase and dream.phrase_date != today:
        return dream  # déjà fait aujourd'hui

    dream.phrase = message or ""
    dream.phrase_date = today
    dream.save(update_fields=["phrase", "phrase_date", "updated_at"])
    return dream


def update_daily_phrase_for_all_users_latest_dream() -> int:
    """
    Pour chaque utilisateur ayant au moins un rêve, met à jour la phrase
    du dernier rêve (au plus une fois par jour grâce à phrase_date).
    """
    user_ids = (Dream.objects.values_list('user_id', flat=True)
                .order_by('user_id').distinct())
    updated = 0
    UserModel = get_user_model()
    for uid in user_ids:
        try:
            user = UserModel.objects.get(id=uid)
            if update_daily_phrase_in_dream(user):
                updated += 1
        except Exception:update_daily_phrase_in_dream
        pass
    return updated
