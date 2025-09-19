from django.utils import timezone
from datetime import timedelta
from collections import Counter
from .models import Dream
from collections import defaultdict, Counter # à regarder de plus près


# --- Liste des émotions disponibles pour un utilisateur ---
def emotions_disponible(user):
    qs = Dream.objects.all()
    if user is not None:
        qs = qs.filter(user=user)
    return qs.values_list('emotion', flat=True).distinct()


# --- Récupérer les rêves d’un utilisateur sur une période, avec filtre émotion ---
def get_dreams_in_period(user, period="all", emotion=None):
    today = timezone.localdate()
    qs = Dream.objects.filter(user=user).order_by("created_at")

    if period == "3d":
        start_date = today - timedelta(days=2)
        qs = qs.filter(created_at__date__gte=start_date, created_at__date__lte=today)
    elif period == "7d":
        start_date = today - timedelta(days=6)
        qs = qs.filter(created_at__date__gte=start_date, created_at__date__lte=today)
    elif period in ("1m", "30d"):
        start_date = today - timedelta(days=29)
        qs = qs.filter(created_at__date__gte=start_date, created_at__date__lte=today)
    # 'all' ou autres → pas de filtre par date, déjà pris en compte

    if emotion and emotion != "all":
        qs = qs.filter(emotion=emotion)

    return qs


# --- Total de rêves ---
def total_dreams(user, period="all", emotion=None):
    return get_dreams_in_period(user, period, emotion=emotion).count()


# --- Fréquence des jours avec rêve ---
def dream_frequency(user, period="all", emotion=None):
    qs = get_dreams_in_period(user, period, emotion=emotion)
    if not qs.exists():
        return 0.0

    dream_days = set(qs.values_list("created_at__date", flat=True))

    today = timezone.localdate()
    if period == "3d":
        total_days = 3
    elif period == "7d":
        total_days = 7
    elif period in ("1m", "30d"):
        total_days = 30
    else:
        earliest = qs.earliest('created_at').created_at.date()
        latest = qs.latest('created_at').created_at.date()
        total_days = max(1, (latest - earliest).days + 1)

    frequency = len(dream_days) / total_days * 100
    return round(min(frequency, 100.0), 2)


# --- Répartition des émotions ---
def emotion_distribution(user, period="all", emotion=None):
    qs = get_dreams_in_period(user, period, emotion=emotion)
    if not qs.exists():
        return {}

    counts = Counter(d.emotion for d in qs if d.emotion)
    total = sum(counts.values())
    if total == 0:
        return {}

    return {k: round(v / total, 3) for k, v in counts.items()}


# --- Longueur moyenne des transcriptions ---
# --- Longueur moyenne des récits ---
def get_transcription_trend(user, period="all", emotion=None):
    """
    Retourne la longueur moyenne des transcriptions par jour pour un utilisateur,
    en tenant compte de la période et éventuellement d'une émotion filtrée.
    Renvoie une liste de dicts : [{'date': 'YYYY-MM-DD', 'avg_length': 42.5}, ...]
    """
    today = timezone.localdate()
    qs = Dream.objects.filter(user=user, transcription__isnull=False).order_by("created_at")

    # Filtre sur la période
    if period == "3d":
        start_date = today - timedelta(days=2)
        qs = qs.filter(created_at__date__gte=start_date, created_at__date__lte=today)
    elif period == "7d":
        start_date = today - timedelta(days=6)
        qs = qs.filter(created_at__date__gte=start_date, created_at__date__lte=today)
    elif period in ("1m", "30d"):
        start_date = today - timedelta(days=29)
        qs = qs.filter(created_at__date__gte=start_date, created_at__date__lte=today)
    # 'all' → pas de filtre

    # Filtre par émotion si demandé
    if emotion and emotion != "all":
        qs = qs.filter(emotion=emotion)

    if not qs.exists():
        return []

    # Regrouper par jour
    lengths_by_day = defaultdict(list)
    for dream in qs:
        day = dream.created_at.date()
        lengths_by_day[day].append(len(dream.transcription))

    # Calculer la moyenne journalière
    trend = []
    for day in sorted(lengths_by_day):
        avg_length = sum(lengths_by_day[day]) / len(lengths_by_day[day])
        trend.append({"date": str(day), "avg_length": round(avg_length, 2)})

    return trend


