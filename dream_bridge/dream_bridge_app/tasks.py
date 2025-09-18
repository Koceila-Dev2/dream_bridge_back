import os
from celery import shared_task
from .services import orchestrate_dream_generation

# bind=True permet d'accéder à l'instance de la tâche (self)
@shared_task
def process_dream_audio_task(dream_id: str, temp_audio_path: str):
    """
    Celery task that receives a temporary file path for processing.
    It ensures the temporary file is deleted after execution.
    """
    try:
        print(f"Processing dream {dream_id} from temp file: {temp_audio_path}")
        orchestrate_dream_generation(dream_id, temp_audio_path)
    finally:
        
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
            print(f"Deleted temporary file: {temp_audio_path}")