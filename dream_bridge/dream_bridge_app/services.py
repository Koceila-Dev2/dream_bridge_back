# # dream_bridge_app/services.py

# import pickle
# import os
# from django.conf import settings
# from django.core.files.base import ContentFile
# from groq import Groq
# from mistralai import Mistral
# # Cet import est crucial pour reconnaître le type de fichier retourné par l'agent
# from mistralai.models import ToolFileChunk

# import requests
# from deep_translator import GoogleTranslator
# from datetime import datetime
# from django.contrib.auth import get_user_model

# from .models import Dream

# def get_system_prompt() -> str:
#     """Lit le prompt système depuis context.txt ou fournit un fallback."""
#     context_path = os.path.join(settings.BASE_DIR, 'dream_bridge_app', 'context.txt')
#     try:
#         with open(context_path, "r", encoding="utf-8") as file:
#             return file.read()
#     except FileNotFoundError:
#         print("Fichier context.txt non trouvé. Utilisation d'un prompt système par défaut.")
#         return """
#         Tu es un artiste onirique et un expert en interprétation des rêves. Ton rôle est de transformer la transcription d'un rêve en un prompt court, évocateur et très visuel pour un modèle de génération d'images.
#         - Décris la scène, les personnages, l'ambiance (joyeuse, angoissante, surréaliste...).
#         - Utilise un langage descriptif riche (couleurs, textures, lumières).
#         - Conclus toujours par des mots-clés de style comme "photorealistic, cinematic lighting, high detail, 8k".
#         - NE réponds QUE par le prompt, sans aucune phrase d'introduction ou de conclusion.
#         """

# def orchestrate_dream_generation(dream_id: str, audio_path: str) -> None:
#     """
#     Orchestre le pipeline complet avec Groq pour le texte et un agent Mistral AI pour l'image.
#     """
#     try:
#         dream = Dream.objects.get(id=dream_id)
#         dream.status = Dream.DreamStatus.PROCESSING
#         dream.save(update_fields=['status'])

#         USE_SIMULATION = True  # Changez à False pour utiliser les API réelles

#         if USE_SIMULATION: 
#             sim_path = os.path.join(settings.BASE_DIR, 'dream_bridge_app', 'simulation.pkl')
#             with open(sim_path, 'rb') as f:
#                 simulation_data = pickle.load(f)
#             dream.transcription = simulation_data['transcription']
#             dream.image_prompt = simulation_data['image_prompt']
#             file_bytes = simulation_data['image_bytes']
#             dream.save(update_fields=['transcription', 'image_prompt', 'updated_at'])
#             print(f"[{dream.id}] Simulation chargée avec succès.")
#         else:
#             # Initialisation des clients API
#             groq_client = Groq(api_key=settings.GROQ_API_KEY)
#             mistral_client = Mistral(api_key=settings.MISTRAL_API_KEY)

#             # --- ÉTAPE 1 & 2: Transcription et Génération de Prompt (Groq) ---
#             # Cette partie reste inchangée
#             print(f"[{dream.id}] Étape 1 & 2: Traitement du texte...")
#             with open(audio_path, "rb") as audio_file:
#                 transcription = groq_client.audio.transcriptions.create(
#                     file=audio_file, model="whisper-large-v3", language="fr"
#                 )
#             dream.transcription = transcription.text
            
#             completion = groq_client.chat.completions.create(
#                 model="llama3-70b-8192", 
#                 messages=[
#                     {"role": "system", "content": get_system_prompt()},
#                     {"role": "user", "content": dream.transcription}
#                 ]
#             )
#             image_prompt = completion.choices[0].message.content.strip()
#             dream.image_prompt = image_prompt
#             dream.save(update_fields=['transcription', 'image_prompt', 'updated_at'])
#             print(f"[{dream.id}] Prompt généré : '{dream.image_prompt[:50]}...'")

#             # --- ÉTAPE 3: Génération de l'Image avec un Agent Mistral AI ---
#             print(f"[{dream.id}] Étape 3: Création de l'agent d'image Mistral...")
            
#             image_agent = mistral_client.beta.agents.create(
#                 model="mistral-large-latest", # Utilisons un modèle récent et puissant
#                 name="Générateur d'images de rêves",
#                 description="Agent qui utilise un outil de génération d'images à partir d'un prompt texte.",
#                 instructions="Utilise l'outil de génération d'image pour créer une image basée sur le prompt fourni par l'utilisateur.",
#                 tools=[{"type": "image_generation"}],
#             )

#             print(f"[{dream.id}] Démarrage de la conversation avec l'agent...")
#             conversation_response = mistral_client.beta.conversations.start(
#                 agent_id=image_agent.id,
#                 inputs=dream.image_prompt
#             )
        
#             # --- Extraction du fichier image depuis la réponse de l'agent ---
#             file_bytes = None
#             # La réponse de l'agent est dans le dernier message de la conversation
#             last_output = conversation_response.outputs[-1] 
            
#             for chunk in last_output.content:
#                 # On vérifie si un des morceaux de la réponse est un fichier
#                 if isinstance(chunk, ToolFileChunk):
#                     print(f"[{dream.id}] Fichier image trouvé (ID: {chunk.file_id}). Téléchargement...")
#                     file_bytes = mistral_client.files.download(file_id=chunk.file_id).read()
#                     break # On a trouvé notre image, on arrête de chercher
                
#             if file_bytes is None:
#                 raise ValueError("L'agent Mistral n'a pas retourné de fichier image.")

#             print(f"[{dream.id}] Image générée et téléchargée avec succès.")

#         # --- ÉTAPE 4: Sauvegarde de l'Image ---
#         image_name = f"dream_{dream.id}.png"
#         dream.generated_image.save(image_name, ContentFile(file_bytes))

#         dream.status = Dream.DreamStatus.COMPLETED
#         dream.save(update_fields=['status', 'updated_at'])

#     except Exception as e:
#         print(f"[{dream_id}] ERREUR CRITIQUE : {e}")
#         if 'dream' in locals():
#             dream.status = Dream.DreamStatus.FAILED
#             dream.error_message = f"Une erreur est survenue lors du traitement: {str(e)}"
#             dream.save(update_fields=['status', 'error_message', 'updated_at'])



# User = get_user_model()

# # Mapping et utilitaires pour horoscope
# sign_map = {
#     "belier": "aries",
#     "bélier": "aries",
#     "taureau": "taurus",
#     "gemeaux": "gemini",
#     "gémeaux": "gemini",
#     "cancer": "cancer",
#     "lion": "leo",
#     "vierge": "virgo",
#     "balance": "libra",
#     "scorpion": "scorpio",
#     "sagittaire": "sagittarius",
#     "capricorne": "capricorn",
#     "verseau": "aquarius",
#     "poissons": "pisces"
# }

# ACCENTS = "éèêëàâäùûüôöç"
# REPLACEMENTS = "eeeeaaauuuooc"

# def remove_accents(text):
#     translation_table = str.maketrans(ACCENTS, REPLACEMENTS)
#     return text.translate(translation_table)

# def get_astrological_sign(birth_date):
#     """Retourne le signe astrologique français à partir d'une date de naissance"""
#     day = birth_date.day
#     month = birth_date.month

#     if (month == 3 and day >= 21) or (month == 4 and day <= 19):
#         return "bélier"
#     elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
#         return "taureau"
#     elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
#         return "gémeaux"
#     elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
#         return "cancer"
#     elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
#         return "lion"
#     elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
#         return "vierge"
#     elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
#         return "balance"
#     elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
#         return "scorpion"
#     elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
#         return "sagittaire"
#     elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
#         return "capricorne"
#     elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
#         return "verseau"
#     elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
#         return "poissons"

# def get_quote_of_the_day():
#     """Récupère la citation du jour et la traduit en français"""
#     url = "https://zenquotes.io/api/today"
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             data = response.json()
#             quote = data[0]["q"]
#             author = data[0]["a"]
#             translated_quote = GoogleTranslator(source='en', target='fr').translate(quote)
#             return f"« {translated_quote} » — {author}"
#         else:
#             return f"Erreur HTTP {response.status_code} lors de la récupération."
#     except Exception as e:
#         return f"Erreur lors de la requête : {e}"

# def get_daily_message(user_id, day="TODAY"):
#     """
#     Retourne soit l'horoscope soit la citation du jour selon le flag astro de l'utilisateur.
#     """
#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return "Utilisateur non trouvé."

#     if getattr(user, "astro", 0) == 1:
#         # Horoscope
#         birth_date = getattr(user, "date_joined", None)
#         #modifier la date quand bdd à jour
#         if not birth_date:
#             return "La date de naissance de l'utilisateur est inconnue."

#         sign_fr = get_astrological_sign(birth_date)
#         sign_key = remove_accents(sign_fr.lower())
#         sign_en = sign_map.get(sign_key)

#         if not sign_en:
#             return f"Signe astrologique '{sign_fr}' non reconnu."

#         url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={sign_en.capitalize()}&day={day.upper()}"
#         response = requests.get(url)

#         if response.status_code == 200:
#             json_data = response.json()
#             if json_data.get("success"):
#                 horoscope = json_data["data"]["horoscope_data"]
#                 translated_horoscope = GoogleTranslator(source='en', target='fr').translate(horoscope)
#                 return f"Horoscope pour {user.get_full_name() or user.username} ({sign_fr.capitalize()}) :\n{translated_horoscope}"
#             else:
#                 return "Erreur : réponse non réussie de l'API."
#         else:
#             return f"Erreur HTTP {response.status_code} lors de la récupération."
#     else:
#         # Citation du jour
#         return get_quote_of_the_day()

# dream_bridge_app/services.py

# import pickle
# import os
# from django.conf import settings
# from django.core.files.base import ContentFile
# from groq import Groq
# from mistralai import Mistral
# # Cet import est crucial pour reconnaître le type de fichier retourné par l'agent
# from mistralai.models import ToolFileChunk

# import requests
# from deep_translator import GoogleTranslator
# from datetime import datetime
# from django.contrib.auth import get_user_model
# from django.utils import timezone  # <-- ajout

# from .models import Dream

# def get_system_prompt() -> str:
#     """Lit le prompt système depuis context.txt ou fournit un fallback."""
#     context_path = os.path.join(settings.BASE_DIR, 'dream_bridge_app', 'context.txt')
#     try:
#         with open(context_path, "r", encoding="utf-8") as file:
#             return file.read()
#     except FileNotFoundError:
#         print("Fichier context.txt non trouvé. Utilisation d'un prompt système par défaut.")
#         return """
#         Tu es un artiste onirique et un expert en interprétation des rêves. Ton rôle est de transformer la transcription d'un rêve en un prompt court, évocateur et très visuel pour un modèle de génération d'images.
#         - Décris la scène, les personnages, l'ambiance (joyeuse, angoissante, surréaliste...).
#         - Utilise un langage descriptif riche (couleurs, textures, lumières).
#         - Conclus toujours par des mots-clés de style comme "photorealistic, cinematic lighting, high detail, 8k".
#         - NE réponds QUE par le prompt, sans aucune phrase d'introduction ou de conclusion.
#         """

# def orchestrate_dream_generation(dream_id: str, audio_path: str) -> None:
#     """
#     Orchestre le pipeline complet avec Groq pour le texte et un agent Mistral AI pour l'image.
#     """
#     try:
#         dream = Dream.objects.get(id=dream_id)
#         dream.status = Dream.DreamStatus.PROCESSING
#         dream.save(update_fields=['status'])

#         USE_SIMULATION = True  # Changez à False pour utiliser les API réelles

#         if USE_SIMULATION:
#             sim_path = os.path.join(settings.BASE_DIR, 'dream_bridge_app', 'simulation.pkl')
#             with open(sim_path, 'rb') as f:
#                 simulation_data = pickle.load(f)
#             dream.transcription = simulation_data['transcription']
#             dream.image_prompt = simulation_data['image_prompt']
#             file_bytes = simulation_data['image_bytes']
#             dream.save(update_fields=['transcription', 'image_prompt', 'updated_at'])
#             print(f"[{dream.id}] Simulation chargée avec succès.")
#         else:
#             # Initialisation des clients API
#             groq_client = Groq(api_key=settings.GROQ_API_KEY)
#             mistral_client = Mistral(api_key=settings.MISTRAL_API_KEY)

#             # --- ÉTAPE 1 & 2: Transcription et Génération de Prompt (Groq) ---
#             print(f"[{dream.id}] Étape 1 & 2: Traitement du texte...")
#             with open(audio_path, "rb") as audio_file:
#                 transcription = groq_client.audio.transcriptions.create(
#                     file=audio_file, model="whisper-large-v3", language="fr"
#                 )
#             dream.transcription = transcription.text

#             completion = groq_client.chat.completions.create(
#                 model="llama3-70b-8192",
#                 messages=[
#                     {"role": "system", "content": get_system_prompt()},
#                     {"role": "user", "content": dream.transcription}
#                 ]
#             )
#             image_prompt = completion.choices[0].message.content.strip()
#             dream.image_prompt = image_prompt
#             dream.save(update_fields=['transcription', 'image_prompt', 'updated_at'])
#             print(f"[{dream.id}] Prompt généré : '{dream.image_prompt[:50]}...'")

#             # --- ÉTAPE 3: Génération de l'Image avec un Agent Mistral AI ---
#             print(f"[{dream.id}] Étape 3: Création de l'agent d'image Mistral...")

#             image_agent = mistral_client.beta.agents.create(
#                 model="mistral-large-latest",  # Utilisons un modèle récent et puissant
#                 name="Générateur d'images de rêves",
#                 description="Agent qui utilise un outil de génération d'images à partir d'un prompt texte.",
#                 instructions="Utilise l'outil de génération d'image pour créer une image basée sur le prompt fourni par l'utilisateur.",
#                 tools=[{"type": "image_generation"}],
#             )

#             print(f"[{dream.id}] Démarrage de la conversation avec l'agent...")
#             conversation_response = mistral_client.beta.conversations.start(
#                 agent_id=image_agent.id,
#                 inputs=dream.image_prompt
#             )

#             # --- Extraction du fichier image depuis la réponse de l'agent ---
#             file_bytes = None
#             last_output = conversation_response.outputs[-1]

#             for chunk in last_output.content:
#                 if isinstance(chunk, ToolFileChunk):
#                     print(f"[{dream.id}] Fichier image trouvé (ID: {chunk.file_id}). Téléchargement...")
#                     file_bytes = mistral_client.files.download(file_id=chunk.file_id).read()
#                     break

#             if file_bytes is None:
#                 raise ValueError("L'agent Mistral n'a pas retourné de fichier image.")

#             print(f"[{dream.id}] Image générée et téléchargée avec succès.")

#         # --- ÉTAPE 4: Sauvegarde de l'Image ---
#         image_name = f"dream_{dream.id}.png"
#         dream.generated_image.save(image_name, ContentFile(file_bytes))

#         dream.status = Dream.DreamStatus.COMPLETED
#         dream.save(update_fields=['status', 'updated_at'])

#     except Exception as e:
#         print(f"[{dream_id}] ERREUR CRITIQUE : {e}")
#         if 'dream' in locals():
#             dream.status = Dream.DreamStatus.FAILED
#             dream.error_message = f"Une erreur est survenue lors du traitement: {str(e)}"
#             dream.save(update_fields=['status', 'error_message', 'updated_at'])


# User = get_user_model()

# # Mapping et utilitaires pour horoscope
# sign_map = {
#     "belier": "aries",
#     "bélier": "aries",
#     "taureau": "taurus",
#     "gemeaux": "gemini",
#     "gémeaux": "gemini",
#     "cancer": "cancer",
#     "lion": "leo",
#     "vierge": "virgo",
#     "balance": "libra",
#     "scorpion": "scorpio",
#     "sagittaire": "sagittarius",
#     "capricorne": "capricorn",
#     "verseau": "aquarius",
#     "poissons": "pisces"
# }

# ACCENTS = "éèêëàâäùûüôöç"
# REPLACEMENTS = "eeeeaaauuuooc"

# def remove_accents(text):
#     translation_table = str.maketrans(ACCENTS, REPLACEMENTS)
#     return text.translate(translation_table)

# def get_astrological_sign(birth_date):
#     """Retourne le signe astrologique français à partir d'une date de naissance"""
#     day = birth_date.day
#     month = birth_date.month

#     if (month == 3 and day >= 21) or (month == 4 and day <= 19):
#         return "bélier"
#     elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
#         return "taureau"
#     elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
#         return "gémeaux"
#     elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
#         return "cancer"
#     elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
#         return "lion"
#     elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
#         return "vierge"
#     elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
#         return "balance"
#     elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
#         return "scorpion"
#     elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
#         return "sagittaire"
#     elif (month == 12 and day >= 22) or (month == 1 and day <= 19):  # <-- ici: and (pas "et")
#         return "capricorne"
#     elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
#         return "verseau"
#     elif (month == 2 and day >= 19) or (month == 3 and day <= 20):
#         return "poissons"

# def get_quote_of_the_day():
#     """Récupère la citation du jour et la traduit en français"""
#     url = "https://zenquotes.io/api/today"
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             data = response.json()
#             quote = data[0]["q"]
#             author = data[0]["a"]
#             translated_quote = GoogleTranslator(source='en', target='fr').translate(quote)
#             return f"« {translated_quote} » — {author}"
#         else:
#             return f"Erreur HTTP {response.status_code} lors de la récupération."
#     except Exception as e:
#         return f"Erreur lors de la requête : {e}"

# def get_daily_message(user_id, day="TODAY"):
#     """
#     Retourne soit l'horoscope soit la citation du jour selon le flag astro de l'utilisateur.
#     """
#     try:
#         user = User.objects.get(id=user_id)
#     except User.DoesNotExist:
#         return "Utilisateur non trouvé."

#     if getattr(user, "astro", 0) == 1:
#         # Horoscope
#         birth_date = getattr(user, "date_joined", None)
#         # TODO: remplace 'date_joined' par la vraie date de naissance quand elle sera dispo
#         if not birth_date:
#             return "La date de naissance de l'utilisateur est inconnue."

#         sign_fr = get_astrological_sign(birth_date)
#         sign_key = remove_accents(sign_fr.lower())
#         sign_en = sign_map.get(sign_key)

#         if not sign_en:
#             return f"Signe astrologique '{sign_fr}' non reconnu."

#         url = f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily?sign={sign_en.capitalize()}&day={day.upper()}"
#         response = requests.get(url)

#         if response.status_code == 200:
#             json_data = response.json()
#             if json_data.get("success"):
#                 horoscope = json_data["data"]["horoscope_data"]
#                 translated_horoscope = GoogleTranslator(source='en', target='fr').translate(horoscope)
#                 return f"Horoscope pour {user.get_full_name() or user.username} ({sign_fr.capitalize()}) :\n{translated_horoscope}"
#             else:
#                 return "Erreur : réponse non réussie de l'API."
#         else:
#             return f"Erreur HTTP {response.status_code} lors de la récupération."
#     else:
#         # Citation du jour
#         return get_quote_of_the_day()


# # ========================
# # 👇👇 Helpers demandés 👇👇
# # ========================

# def update_daily_phrase_in_dream(user, dream_id: str | None = None, day: str = "TODAY") -> bool:
#     """
#     Récupère la phrase du jour via get_daily_message() et l'enregistre
#     dans un enregistrement Dream :
#       - si dream_id est fourni : dans CE rêve (s'il appartient à l'user)
#       - sinon : dans le DERNIER rêve (par date de création) de l'utilisateur
#     Si le champ 'phrase_date' existe dans Dream, on ne réécrit pas si déjà maj aujourd'hui.
#     Retourne True si la mise à jour a été faite, False sinon.
#     """
#     if not user:
#         return False

#     qs = Dream.objects.filter(user=user)
#     dream = qs.filter(id=dream_id).first() if dream_id else qs.order_by('-created_at').first()
#     if not dream:
#         return False  # aucun rêve cible

#     today = timezone.localdate()

#     # Si ton modèle a phrase_date, on évite les doublons le même jour
#     if hasattr(dream, "phrase_date"):
#         if dream.phrase and dream.phrase_date == today:
#             return False

#     # Récupération via ton API/logiciel existant
#     text = get_daily_message(user.id, day=day)

#     # Écriture
#     dream.phrase = text or ""
#     update_fields = ['phrase', 'updated_at']
#     if hasattr(dream, "phrase_date"):
#         dream.phrase_date = today
#         update_fields.insert(1, 'phrase_date')

#     dream.save(update_fields=update_fields)
#     return True

# def update_daily_phrase_for_all_users_latest_dream() -> int:
#     """
#     Utilitaire batch : pour chaque utilisateur ayant au moins un rêve,
#     met à jour la phrase du DERNIER rêve (au plus une fois par jour si 'phrase_date' existe).
#     Retourne le nombre de rêves mis à jour.
#     """
#     user_ids = (Dream.objects.values_list('user_id', flat=True)
#                           .order_by('user_id').distinct())
#     updated = 0
#     for uid in user_ids:
#         try:
#             User = get_user_model()
#             user = User.objects.get(id=uid)
#             if update_daily_phrase_in_dream(user):
#                 updated += 1
#         except Exception:
#             # continue même si un user pose problème
#             pass
#     return updated

# def update_daily_phrase_in_dream(user, dream_id: str | None = None):
#     """
#     Écrit la phrase/horoscope du jour dans le rêve ciblé (ou le plus récent),
#     1 fois par jour (via phrase_date).
#     Retourne le Dream mis à jour ou None si aucun rêve n'existe.
#     """
#     # Récupère la phrase du jour (horoscope si l'user croit à l'astro, sinon citation)
#     message = get_daily_message(user.id)
#     today = timezone.localdate()

#     qs = Dream.objects.filter(user=user)
#     if dream_id:
#         qs = qs.filter(id=dream_id)

#     dream = qs.order_by('-created_at').first()
#     if not dream:
#         return None  # l'utilisateur n'a pas encore de rêve → rien à sauver

#     # N’écrase pas si déjà écrit aujourd’hui
#     if dream.phrase and dream.phrase_date == today:
#         return dream

#     dream.phrase = message
#     dream.phrase_date = today
#     dream.save(update_fields=["phrase", "phrase_date"])
#     return dream

import os
import pickle
from datetime import datetime

import requests
from deep_translator import GoogleTranslator
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone
from groq import Groq
from mistralai import Mistral
from mistralai.models import ToolFileChunk

from .models import Dream

User = get_user_model()  # utilisé dans get_daily_message()


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

    if getattr(user, "astro", 0) == 1:
        birth_date = getattr(user, "date_joined", None)  # TODO: remplacer par vraie date de naissance
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


# -------- Helpers d’écriture dans Dream --------

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

    if dream.phrase and dream.phrase_date == today:
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
        except Exception:
            pass
    return updated
