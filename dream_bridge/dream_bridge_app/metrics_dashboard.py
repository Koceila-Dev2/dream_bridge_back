from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
import pandas as pd
from .models import Dream


# Filtrage par période
def get_dreams_in_period(user, period="all"):
    now = timezone.now()
    if period == "3d":
        start_date = now - timedelta(days=3)
    elif period == "7d":
        start_date = now - timedelta(days=7)
    elif period == "1m":
        start_date = now - timedelta(days=30)
    else:
        start_date = None

    qs = Dream.objects.filter(user=user)
    if start_date:
        qs = qs.filter(created_at__gte=start_date)
    return qs

# Nombre total de rêves
def total_dreams(user, period="all"):
    return get_dreams_in_period(user, period).count()

# Fréquence des enregistrements (nb jours avec au moins 1 rêve / nb jours dans période)
def dream_frequency(user, period="7d"):
    qs = get_dreams_in_period(user, period)
    if not qs.exists():
        return 0
    
    days_with_dreams = qs.values("created_at__date").distinct().count()
    
    if period == "3d":
        total_days = 3
    elif period == "7d":
        total_days = 7
    elif period == "1m":
        total_days = 30
    else:
        first_dream = Dream.objects.filter(user=user).order_by("created_at").first()
        if not first_dream:
            return 0
        total_days = (timezone.now().date() - first_dream.created_at.date()).days + 1
    
    return round((days_with_dreams / total_days) * 100, 2)  # % de jours avec rêve

# Répartition des émotions dominantes (camembert)
def emotion_distribution(user, period="all"):
    qs = get_dreams_in_period(user, period)
    emotions_count = {}

    for dream in qs:
        emo = dream.emotion  # champ str
        if emo:  # ignore les valeurs vides
            emotions_count[emo] = emotions_count.get(emo, 0) + 1

    total = sum(emotions_count.values())
    if total == 0:
        return {}

    # Retour en proportions
    return {emo: round(val / total, 3) for emo, val in emotions_count.items()}


# Tendance des émotions (time series)
def emotion_trend(user, period="7d"):
    qs = get_dreams_in_period(user, period).order_by("created_at")
    data = []

    for dream in qs:
        # Convertir la date en string pour JSON
        data.append({
            "date": dream.created_at.date().isoformat(),  # <-- ici
            "emotion": dream.emotion
        })

    if not data:
        return []

    df = pd.DataFrame(data)
    df = df.groupby(["date", "emotion"]).size().unstack(fill_value=0)
    df = df.reset_index()

    return df.to_dict(orient="records")

