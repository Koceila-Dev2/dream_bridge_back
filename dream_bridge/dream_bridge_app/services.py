import os
import pickle
import json
import time
import requests
import google
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils import timezone

from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

from groq import Groq
from mistralai import Mistral
from mistralai.models import ToolFileChunk

from deep_translator import GoogleTranslator

from .models import Dream

User = get_user_model()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=GOOGLE_API_KEY)

logger = logging.getLogger(__name__)

PROMPTS_DIR = os.path.join(
    settings.BASE_DIR,
    "dream_bridge_app",
    "prompts"
)
PERSONAL_MSG_PROMPT_PATH = os.path.join(
    PROMPTS_DIR,
    "personal_daily_message.txt"
)

def read_context_file(filename="context.txt"):
    """Lit un fichier de contexte depuis le dossier de l'application."""
    path = os.path.join(settings.BASE_DIR, "dream_bridge_app", filename)
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return ""

def get_personal_message_template() -> str:
    """
    Charge le template /prompts/personal_daily_message.txt.
    Fallback plus expressif si le fichier est absent.
    """
    try:
        with open(PERSONAL_MSG_PROMPT_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # ✔ Fallback étoffé : émotion + nuance astro + micro-action
        return (
            "Tu écris un « message du jour » personnalisé, en français, pour "
            "{username}.\n\n"
            "CONTEXTE RÊVE\n"
            "- Transcription (brute) : {dream_transcription}\n"
            "- Ambiance / prompt d’image : {image_prompt}\n"
            "- Émotion dominante perçue : {dominant_emotion}\n\n"
            "PRÉFÉRENCES UTILISATEUR\n"
            "- Croit en l’astrologie : {believes_in_astrology}\n"
            "- Signe astrologique (si connu) : {zodiac_sign}\n\n"
            "INSTRUCTIONS\n"
            "- 2 à 3 phrases (≈ 70–110 mots), ton chaleureux mais précis, "
            "ancré dans le rêve.\n"
            "- Fais sentir explicitement l’émotion dominante et ce qu’elle "
            "invite à faire.\n"
            "- Si Croit en l’astrologie = True ET Signe renseigné, ajoute "
            "une nuance subtile et positive liée au signe "
            "(sans cliché ni horoscope brut).\n"
            "- Termine par une micro-action concrète issue du rêve "
            "(ex. noter, appeler, clarifier, respirer, poser une limite, "
            "oser demander).\n"
            "- Pas de liste, pas d’emoji, pas de titre. "
            "Sortie : uniquement le message.\n"
        )

# pas utilisé pour l'instant
# def read_context_file(filename="context.txt"):
#     """Lit un fichier de contexte depuis le dossier de l'application."""
#     path = os.path.join(settings.BASE_DIR, "dream_bridge_app", filename)
#     try:
#         with open(path, "r", encoding="utf-8") as file:
#             return file.read()
#     except FileNotFoundError:
#         return ""


def build_personal_message_prompt(dream: Dream, user) -> str:
    """
    Prépare le prompt avec données du rêve + profil (astro) +
    émotion dominante.
    """
    profile = getattr(user, "profile", None)
    believes = bool(getattr(profile, "believes_in_astrology", False))
    if profile:
        believes
    else:
        False

    # Récup signe astro
    sign = (getattr(profile, "zodiac_sign", "") or "").strip()
    if not sign and believes and getattr(profile, "birth_date", None):
        sign = get_astrological_sign(profile.birth_date).capitalize()

    try:
        emotion_label = dream.get_emotion_display()
    except Exception:
        emotion_label = dream.emotion or "neutre"

    ctx = {
        "username": user.get_full_name() or user.username,
        "first_name": user.first_name or user.username,
        "believes_in_astrology": "True" if believes else "False",
        "zodiac_sign": sign,
        "dream_transcription": (dream.transcription or "").strip(),
        "image_prompt": (dream.image_prompt or "").strip(),
        "dominant_emotion": emotion_label or "neutre",
    }

    template = get_personal_message_template()
    return template.format(**ctx)


def _fallback_personal_message(dream: Dream, user) -> str:
    """
    Message local si pas de clé GROQ, plus riche
    (émotion + nuance astro + action).
    """
    profile = getattr(user, "profile", None)
    believes = (
        bool(getattr(profile, "believes_in_astrology", False)) if
        profile
        else False
    )

    sign = (getattr(profile, "zodiac_sign", "") or "").strip().lower()
    if not sign and believes and getattr(profile, "birth_date", None):
        sign = get_astrological_sign(profile.birth_date).lower()

    # Force string conversion in case of dict or other type
    if isinstance(sign, dict):
        sign = str(sign.get("sign", ""))
    elif not isinstance(sign, str):
        sign = str(sign)

    try:
        emotion = dream.get_emotion_display()
    except Exception:
        emotion = dream.emotion or "neutre"

    # Petit extrait de la transcription si dispo
    snippet = (dream.transcription or "").strip()
    if len(snippet) > 120:
        snippet = snippet[:117].rsplit(" ", 1)[0] + "…"

    if emotion and emotion not in ("neutre", "erreur"):
        emo_txt = (
            f"Cette nuit a fait remonter {emotion}, signe d’un besoin réel "
            "qui cherche à s’exprimer. "
        )
    else:
        emo_txt = (
            "Ce rêve met en lumière quelque chose"
            "d’encore diffus mais important. "
        )

    astro_txt = ""
    if believes and sign:
        astro_txt = (
            f" En {sign}, appuie-toi sur tes qualités naturelles "
            "pour enraciner ce pas."
        )

    action = (
        " Choisis une action minuscule mais tangible aujourd’hui : "
        "écrire trois lignes, envoyer un message, "
        "ou poser une limite douce qui respecte ce que tu as compris."
    )

    core = (
        f"{emo_txt}"
        f"{('On y entend : « ' + snippet + ' ». ' if snippet else '')}"
        "Transforme ce signal en geste simple et concret, ici et maintenant."
    )

    return core + astro_txt + action


def generate_personal_message_for_dream(dream_id: str) -> str:
    """
    Génère et enregistre Dream.personal_phrase + date.
    Utilise la phrase du jour pour enrichir le message personnalisé.
    """
    try:
        # Récupération du rêve et de l'utilisateur
        dream = Dream.objects.select_related("user", "user__profile").get(id=dream_id)
        logger.info(f"Récupération du rêve avec ID {dream_id} réussie.")

        prompt = build_personal_message_prompt(dream, dream.user)
        logger.debug(f"Prompt généré : {prompt[:100]}...")

        # Vérification de la clé API Mistral
        if not MISTRAL_API_KEY:
            logger.error("MISTRAL_API_KEY n'est pas définie.")
            msg = _fallback_personal_message(dream, dream.user)
        else:
            try:
                # Préparation du client Mistral
                mistral_client = Mistral(api_key=MISTRAL_API_KEY)
                logger.info("Client Mistral initialisé avec succès.")

                chat_response = mistral_client.chat.complete(
                    model="mistral-large-latest",
                    messages=[
                        {"role": "system", "content": prompt},
                        {
                            "role": "user",
                            "content": (
                                "Utilise les infos ci-dessus pour rédiger le message :"
                                "2 à 3 phrases (≈ 70–110 mots), ton chaleureux mais précis, ancré dans le rêve."
                            )
                        },
                    ],
                    temperature=0.8,
                )

                if not chat_response or not chat_response.choices:
                    logger.warning("Réponse vide de Mistral.")
                    msg = _fallback_personal_message(dream, dream.user)
                else:
                    msg = (chat_response.choices[0].message.content or "").strip()
                    logger.info(f"Message généré avec succès : {msg[:100]}...")

            except Exception as e:
                logger.error(f"Erreur lors de l'appel à Mistral : {str(e)}")
                msg = _fallback_personal_message(dream, dream.user)

        # Enregistrement du message personnalisé
        if msg:
            dream.personal_phrase = msg
            dream.personal_phrase_date = timezone.localdate()
            dream.save(update_fields=["personal_phrase", "personal_phrase_date"])
            logger.info(f"Message personnalisé sauvegardé pour le rêve {dream_id}.")
            return msg
        else:
            logger.warning("Aucun message généré.")
            return ""

    except Dream.DoesNotExist:
        logger.error(f"Rêve avec ID {dream_id} non trouvé.")
        return ""
    except Exception as e:
        logger.error(f"Erreur inattendue : {str(e)}")
        return ""


def get_system_prompt() -> str:
    """Prompt système pour générer le prompt d'image si besoin."""
    content = read_context_file("context.txt")
    if content:
        return content
    return (
        "Tu es un artiste onirique et un expert en interprétation des rêves. "
        "Transforme la transcription d'un rêve en un prompt court,"
        "évocateur et visuel pour un modèle de génération d'images. "
        "- Décris la scène, les personnages, l'ambiance. "
        "- Utilise un langage descriptif riche (couleurs, textures, lumières)."
        "- Termine par des mots-clés de style : photorealistic, cinematic"
        "lighting, high detail, 8k. "
        "- Réponds uniquement par le prompt."
    )


# Code pour determiner l'émotion dominante via Mistral
def get_emotion_from_text(transcription: str) -> str:
    """Analyse la transcription pour déduire
    l'émotion principale via Mistral."""
    try:
        mistral_client = Mistral(api_key=MISTRAL_API_KEY)
        system_prompt = read_context_file("context_emotion.txt")
        if not system_prompt:
            return "neutre"

        chat_response = mistral_client.chat.complete(
            model="mistral-large-latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": (
                        "Analyse le texte ci-dessous. Ta réponse doit être un"
                        "dictionnaire JSON valide "
                        "avec des émotions en clé et"
                        "des scores entre 0 et 1 en valeur. "
                        "Ne mets pas de texte, uniquement du JSON : "
                        f"{transcription}"
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )

        prediction_str = chat_response.choices[0].message.content
        emotions_scores = json.loads(prediction_str)
        if not emotions_scores:
            return "neutre"
        return max(emotions_scores, key=emotions_scores.get)
    except Exception:
        return "neutre"

def save_image_or_fallback(response, dream_id):
    """
    Tente d'extraire les données de l'image de la réponse Gemini.
    Si cela échoue, utilise une image de secours locale.
    Retourne le nom du fichier et les données binaires de l'image.
    """
    file_bytes = None
    
    # Essai d'extraction des données de l'image de l'API
    try:
        # On accède directement à la partie qui nous intéresse
        file_bytes = response.candidates[0].content.parts[0].inline_data.data
        if not file_bytes:
            logger.warning(f"La réponse de Gemini pour le rêve {dream_id} ne contenait pas de données d'image.")
    except (AttributeError, IndexError, TypeError) as e:
        # Cette ligne intercepte toutes les erreurs possibles si la structure de la réponse n'est pas celle attendue
        logger.warning(f"Impossible d'extraire l'image de la réponse de Gemini pour le rêve {dream_id} : {e}. Utilisation de l'image par défaut.")
        file_bytes = None

    # Si on n'a pas réussi à obtenir l'image, on utilise le fallback
    if not file_bytes:
        default_image_path = os.path.join(settings.BASE_DIR, "media", "dreams", "images", "default_image.png")
        try:
            with open(default_image_path, "rb") as f:
                file_bytes = f.read()
            logger.info(f"Utilisation de l'image par défaut pour le rêve {dream_id}.")
        except FileNotFoundError:
            logger.critical(f"Le fichier par défaut '{default_image_path}' est introuvable.")
            raise  # On propage l'erreur car c'est un problème de configuration

    image_name = f"dream_{dream_id}.png"
    return image_name, file_bytes


def orchestrate_dream_generation(dream_id: str, audio_path: str) -> None:
    """Orchestre le pipeline (transcription → émotion → prompt → image)."""
    try:
        dream = Dream.objects.get(id=dream_id)
        dream.save(update_fields=["status"])

        USE_SIMULATION = False

        if USE_SIMULATION:
            sim_path = os.path.join(
                settings.BASE_DIR,
                "dream_bridge_app",
                "simulation.pkl",
            )
            with open(sim_path, "rb") as f:
                simulation_data = pickle.load(f)

            # dream.transcription = simulation_data["transcription"]
            dream.transcription = "Un rêve étrange avec des montagnes,"
            "des étoiles,"
            "et une rivière qui serpente à travers"
            "une forêt dense et mystérieuse."
            dream.image_prompt = simulation_data["image_prompt"]
            file_bytes = simulation_data["image_bytes"]
            dream.status = Dream.DreamStatus.PROCESSING

            print(
                "Simulation mode: le traitement est bien en processing"
            )

            transcription = dream.transcription
            dream.emotion = get_emotion_from_text(transcription) or "neutre"
            dream.save(
                update_fields=[
                    "status",
                    "transcription",
                    "image_prompt",
                    "emotion",
                    "updated_at",
                ]
            )

        else:
            # --- Transcription (Whisper Groq)
            groq_client = Groq(api_key=GROQ_API_KEY)
            mistral_client = Mistral(api_key=MISTRAL_API_KEY)

            with open(audio_path, "rb") as audio_file:
                transcription = groq_client.audio.transcriptions.create(
                    file=audio_file,
                    model="whisper-large-v3",
                    language="fr",
                )
            dream.transcription = transcription.text

            # --- Émotion
            dream.emotion = get_emotion_from_text(dream.transcription)
            dream.save(update_fields=["emotion"])

            # --- Prompt d'image
            completion = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": get_system_prompt()},
                    {"role": "user", "content": dream.transcription},
                ],
            )
            # Vérification pour completion
            if not completion or not completion.choices:
                raise ValueError("Aucune réponse valide pour le prompt d'image.")
            dream.image_prompt = completion.choices[0].message.content.strip()
            dream.save(
                update_fields=["transcription",
                               "image_prompt",
                               "updated_at"]
            )

 #================================== GIMINI test =======================           
            

            # prompt = (
            #     "Utilise l'outil de génération d'image pour"
            #         "créer une image "
            #         "basée sur le prompt fourni."
            # )
            prompt =  dream.image_prompt

            logger.debug(f"Prompt envoyé à Gemini : {prompt}")
            try:
                response = client.models.generate_content(
                    model="models/gemini-2.5-flash-image-preview",
                    contents=prompt,
                #     config=types.GenerateImagesConfig(
                #         number_of_images=1,
                # )
                )
                
                
            except Exception as e:
                logger.error(f"Erreur lors de l'appel à Gemini : {str(e)}")
                raise

            logger.debug(f"Réponse brute de Gemini : {response}")

           
            # dream.generated_image.save(image_name, ContentFile(file_bytes))
#============================ Gemini image generation ============================


            # # --- Image (Mistral image tool)
            # image_agent = mistral_client.beta.agents.create(
            #     model="mistral-large-latest",
            #     name="Générateur d'images de rêves",
            #     description=(
            #         "Agent qui utilise un outil de génération d'images "
            #         "à partir d'un prompt texte."
            #     ),
            #     instructions=(
            #         "Utilise l'outil de génération d'image pour"
            #         "créer une image "
            #         "basée sur le prompt fourni."
            #     ),
            #     tools=[{"type": "image_generation"}],
            # )
            # conversation_response = mistral_client.beta.conversations.start(
            #     agent_id=image_agent.id,
            #     inputs=dream.image_prompt,
            # )

            # file_bytes = None
            # last_output = conversation_response.outputs[-1]
            # for chunk in last_output.content:
            #     if isinstance(chunk, ToolFileChunk):
            #         file_bytes = mistral_client.files.download(
            #             file_id=chunk.file_id
            #         ).read()
            #         break
            # if file_bytes is None:
            #     raise ValueError(
            #         "L'agent Mistral n'a pas retourné de fichier image."
            #     )

        # Gestion centralisée de l'enregistrement de l'image ou fallback
        
        # Remplacement dans orchestrate_dream_generation
        try:
            image_name, file_bytes = save_image_or_fallback(response, dream.id)
            dream.generated_image.save(image_name, ContentFile(file_bytes))
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de l'image : {str(e)}")
            raise

        # Génération auto du message personnalisé
        try:
            logger.info(f"Début de la génération du message personnalisé pour le rêve {dream_id}.")

            generate_personal_message_for_dream(str(dream.id))
            
            logger.info(f"Message personnalisé généré et sauvegardé pour le rêve {dream_id}.")
        except Exception as e:
            logger.error(f"Échec de la génération du message personnalisé automatique : {str(e)}")
            pass

        dream.status = Dream.DreamStatus.COMPLETED
        dream.save(update_fields=["status", "updated_at"])

    except Exception as e:
        if "dream" in locals():
            dream.status = Dream.DreamStatus.FAILED
            dream.error_message = (
                f"Une erreur est survenue lors du traitement: {str(e)}"
            )
            dream.save(update_fields=["status", "error_message", "updated_at"])


# ----------------------- Horoscope & citations -----------------------

sign_map = {
    "belier": "aries", "bélier": "aries",
    "taureau": "taurus",
    "gemeaux": "gemini", "gémeaux": "gemini",
    "cancer": "cancer", "lion": "leo", "vierge": "virgo",
    "balance": "libra", "scorpion": "scorpio",
    "sagittaire": "sagittarius", "capricorne": "capricorn",
    "verseau": "aquarius", "poissons": "pisces",
}

ACCENTS = "éèêëàâäùûüôöç"
REPLACEMENTS = "eeeeaaauuuooc"


def remove_accents(text: str) -> str:
    return text.translate(str.maketrans(ACCENTS, REPLACEMENTS))


def get_astrological_sign(birth_date):
    d = birth_date.day
    m = birth_date.month

    if (m == 4 and d >= 20) or (m == 5 and d <= 20):
        return "taureau"
    if (m == 5 and d >= 21) or (m == 6 and d <= 20):
        return "gémeaux"
    if (m == 6 and d >= 21) or (m == 7 and d <= 22):
        return "cancer"
    if (m == 7 and d >= 23) or (m == 8 and d <= 22):
        return "lion"
    if (m == 8 and d >= 23) or (m == 9 and d <= 22):
        return "vierge"
    if (m == 9 and d >= 23) or (m == 10 and d <= 22):
        return "balance"
    if (m == 10 and d >= 23) or (m == 11 and d <= 21):
        return "scorpion"
    if (m == 11 and d >= 22) or (m == 12 and d <= 21):
        return "sagittaire"
    if (m == 12 and d >= 22) or (m == 1 and d <= 19):
        return "capricorne"
    if (m == 1 and d >= 20) or (m == 2 and d <= 18):
        return "verseau"

    return "poissons"


def get_quote_of_the_day() -> str:
    url = "https://zenquotes.io/api/today"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            quote = data[0]["q"]
            author = data[0]["a"]
            translated = GoogleTranslator(
                source="en",
                target="fr"
            ).translate(quote)
            return f"« {translated} » — {author}"
        return f"Erreur HTTP {r.status_code} lors de la récupération."
    except Exception as e:
        return f"Erreur lors de la requête : {e}"


def get_daily_message(user_id, day="TODAY") -> str:
    """Renvoie l'horoscope (si croyance) ou la citation du jour."""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return "Utilisateur non trouvé."

    if not hasattr(user, "profile"):
        return "Profil utilisateur introuvable."

    profile = user.profile

    if profile.believes_in_astrology:
        birth_date = profile.birth_date
        if not birth_date:
            return "La date de naissance de l'utilisateur est inconnue."

        sign_fr = get_astrological_sign(birth_date)
        sign_en = sign_map.get(remove_accents(sign_fr.lower()))
        if not sign_en:
            return f"Signe astrologique '{sign_fr}' non reconnu."

        url = (
            f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily"
            f"?sign={sign_en.capitalize()}&day={day.upper()}"
        )
        r = requests.get(url, timeout=10)

        if r.status_code == 200:
            data = r.json()
            if data.get("success"):
                horoscope = data["data"]["horoscope_data"]
                translated = GoogleTranslator(
                    source="en", target="fr"
                ).translate(horoscope)
                user_name = user.get_full_name() or user.username
                return (
                    f"Horoscope pour {user_name} ({sign_fr.capitalize()}) :\n"
                    f"{translated}"
                )
            return "Erreur : réponse non réussie de l'API."

        return f"Erreur HTTP {r.status_code} lors de la récupération."

    return get_quote_of_the_day()
