import os
from celery import Celery

# Définir le module de settings par défaut pour le programme 'celery'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dream_bridge.settings')

app = Celery('dream_bridge')

# Utilisation des settings Django pour la configuration de Celery
app.config_from_object('django.conf:settings', namespace='CELERY')


# Découverte automatique des tâches dans toutes les applications Django installées
app.autodiscover_tasks()