# import pickle
# import os
# import json 
# import numpy as np 
# # from django.conf import settings
# from django.core.files.base import ContentFile
# from groq import Groq
# from mistralai import Mistral
# # Cet import est crucial pour reconnaître le type de fichier retourné par l'agent
# from mistralai.models import ToolFileChunk

# import requests
# from deep_translator import GoogleTranslator
# from datetime import datetime
# from django.contrib.auth import get_user_model



# MISTRAL_API_KEY=os.environ.get("MISTRAL_API_KEY")




# def read_context_file(filename="context.txt"):
#     """Lit un fichier de contexte depuis le dossier de l'application."""
#     context_path = os.path.join(settings.BASE_DIR, 'dream_bridge_app', filename)
#     try:
#         with open(context_path, "r", encoding="utf-8") as file:
#             return file.read()
#     except FileNotFoundError:
#         print(f"Fichier {filename} non trouvé.")
#         return ""
    



# def get_emotion_from_text(transcription: str) -> str:
#     """Analyse la transcription pour en déduire l'émotion principale."""
#     from django.conf import settings
#     try:
#         mistral_client = Mistral(api_key=settings.MISTRAL_API_KEY)
        
#         system_prompt = read_context_file("context_emotion.txt")
#         if not system_prompt:
#             return "neutre" # Fallback si le contexte est manquant

#         chat_response = mistral_client.chat(
#             model="mistral-large-latest",
#             messages=[
#                 {"role": "system", "content": system_prompt},
#                 {"role": "user", "content": f"Voici la transcription du rêve à analyser : {transcription}"}
#             ],
#             response_format={"type": "json_object"}
#         )
        
#         prediction_str = chat_response.choices[0].message.content
#         emotions_scores = json.loads(prediction_str)
        
#         # Trouve l'émotion avec le score le plus élevé
#         if not emotions_scores:
#             return "neutre"
            
#         dominant_emotion = max(emotions_scores, key=emotions_scores.get)
        
#         # Vérifier si l'émotion retournée est valide
#         # valid_emotions = [e[0] for e in Dream.EMOTIONS]
#         # if dominant_emotion in valid_emotions:
#         #     print(f"Émotion dominante détectée : {dominant_emotion}")
#         if dominant_emotion:    
#             return dominant_emotion
#         else:
#             print(f"Émotion '{dominant_emotion}' non valide, retour à 'neutre'.")
#             return "neutre"
            
#     except Exception as e:
#         print(f"Erreur lors de l'analyse des émotions : {e}")
#         return "neutre" # Retourne une valeur sûre en cas d'erreur
    



# sim_path = "C:\\Users\\Koceila\\Desktop\\projet_final_serieux\\dream_bridge_back\\dream_bridge\\dream_bridge_app\\simulation.pkl"
# with open(sim_path, 'rb') as f:
#     simulation_data = pickle.load(f)
#     print("Données de simulation chargées.")

# transcription = simulation_data['transcription']
# image_prompt = simulation_data['image_prompt']
# file_bytes = simulation_data['image_bytes']

# print(" Étape 2: Analyse des émotions...")

# emotion = get_emotion_from_text(transcription)

# print(f"Émotion analysée : {emotion}")

import os
import json
import pickle
from mistralai import Mistral
from dotenv import load_dotenv

# --- ÉTAPE 1: CONFIGURATION ---

def setup_environment():
    """
    Charge les variables d'environnement depuis le fichier .env du projet Django.
    Retourne la clé API de Mistral.
    """
    # On construit le chemin vers le fichier .env qui est dans le dossier 'dream_bridge'
    # à partir de l'emplacement de ce script.
    script_dir = os.path.dirname(__file__)
    dotenv_path = os.path.join(script_dir, 'dream_bridge', '.env') 
    
    if os.path.exists(dotenv_path):
        print(f"Chargement des variables depuis : {dotenv_path}")
        load_dotenv(dotenv_path=dotenv_path)
    else:
        print(f"AVERTISSEMENT : Fichier .env non trouvé à l'emplacement : {dotenv_path}")

    return os.environ.get("MISTRAL_API_KEY")

def read_context_file(filename="context_emotion.txt"):
    """
    Lit le fichier de contexte en construisant le chemin depuis la racine du projet.
    """
    script_dir = os.path.dirname(__file__)
    context_path = os.path.join(script_dir, 'dream_bridge', 'dream_bridge_app', filename)
    try:
        with open(context_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"Fichier contexte '{filename}' non trouvé à '{context_path}'.")
        return None

# --- ÉTAPE 2: LOGIQUE D'ANALYSE (SANS DJANGO) ---

def get_emotion_from_text(transcription: str, api_key: str) -> str:
    """
    Analyse la transcription pour en déduire l'émotion principale en utilisant l'API Mistral.
    """
    if not api_key:
        print("Erreur critique : La clé API Mistral est manquante.")
        return "erreur"

    try:
        mistral_client = Mistral(api_key=api_key)
        
        system_prompt = read_context_file("context_emotion.txt")
        if not system_prompt:
            return "erreur"

        print("Appel à l'API Mistral pour l'analyse des émotions...")
        chat_response = mistral_client.chat(
            model="mistral-large-latest",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Voici la transcription du rêve à analyser : {transcription}"}
            ],
            response_format={"type": "json_object"}
        )
        
        prediction_str = chat_response.choices[0].message.content
        emotions_scores = json.loads(prediction_str)
        
        if not emotions_scores:
            return "neutre"
            
        dominant_emotion = max(emotions_scores, key=emotions_scores.get)
        return dominant_emotion
            
    except Exception as e:
        print(f"Erreur lors de l'appel à l'API Mistral : {e}")
        return "erreur"

# --- ÉTAPE 3: EXÉCUTION DU TEST ---

if __name__ == "__main__":
    MISTRAL_API_KEY = setup_environment()

    # On charge les données de simulation pour avoir un texte à analyser
    script_dir = os.path.dirname(__file__)
    sim_path = os.path.join(script_dir, "dream_bridge", "dream_bridge_app", "simulation.pkl")
    
    try:
        with open(sim_path, 'rb') as f:
            simulation_data = pickle.load(f)
            print("Données de simulation chargées avec succès.")
        
        transcription_texte = simulation_data['transcription']
        print(f"Texte à analyser : \"{transcription_texte[:80]}...\"")

        # On appelle la fonction d'analyse
        emotion_resultat = get_emotion_from_text(transcription_texte, MISTRAL_API_KEY)
        
        print("-" * 30)
        print(f"✅ ÉMOTION DÉTECTÉE : {emotion_resultat.upper()}")
        print("-" * 30)

    except FileNotFoundError:
        print(f"Erreur : Le fichier de simulation 'simulation.pkl' est introuvable à '{sim_path}'")
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")
