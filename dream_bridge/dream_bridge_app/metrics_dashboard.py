from django.utils import timezone
from datetime import timedelta
from collections import Counter
from .models import Dream

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
# --- Fréquence des jours avec rêve corrigée ---
def dream_frequency(user, period="all", emotion=None):
    qs = get_dreams_in_period(user, period, emotion=emotion)
    if not qs.exists():
        return 0.0

    # Extraire les dates uniques des rêves
    dream_days = set(qs.values_list("created_at__date", flat=True))

    # Calcul du nombre total de jours selon la période
    today = timezone.localdate()
    if period == "3d":
        total_days = 3
    elif period == "7d":
        total_days = 7
    elif period in ("1m", "30d"):
        total_days = 30
    else:
        # Pour 'all' ou autre, prendre la plage entre le plus ancien et le plus récent rêve
        earliest = qs.earliest('created_at').created_at.date()
        latest = qs.latest('created_at').created_at.date()
        total_days = max(1, (latest - earliest).days + 1)

    # Fréquence des jours avec rêve, limitée à 100 %
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


# --- Tendance des émotions dans le temps ---
def emotion_trend(user, period="all", emotion=None):
    qs = get_dreams_in_period(user, period, emotion=emotion)
    if not qs.exists():
        return {}

    trend = {}
    today = timezone.localdate()

    if period == "3d":
        days_range = [today - timedelta(days=2), today - timedelta(days=1), today]
    elif period == "7d":
        days_range = [today - timedelta(days=i) for i in reversed(range(7))]
    elif period in ("1m", "30d"):
        days_range = [today - timedelta(days=i) for i in reversed(range(30))]
    else:
        days_range = sorted(qs.values_list("created_at__date", flat=True).distinct())

    for date in days_range:
        dreams_on_day = qs.filter(created_at__date=date)
        counts = Counter(d.emotion for d in dreams_on_day if d.emotion)
        total = sum(counts.values())
        date_key = date.isoformat() if hasattr(date, "isoformat") else str(date)
        trend[date_key] = {k: round(v / total, 3) for k, v in counts.items()} if total > 0 else {}

    return trend
