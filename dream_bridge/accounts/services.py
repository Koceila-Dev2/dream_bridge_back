# # accounts/services.py
# from django.utils import timezone
# # accounts/services.py
# import os
# import requests
# from django.utils import timezone

# API_URL = os.environ.get("ASTRO_QUOTE_API_URL")
# API_KEY = os.environ.get("ASTRO_QUOTE_API_KEY", "")

# def ensure_quote_for_today(profile) -> bool:
#     """
#     Si l'utilisateur croit à l'astrologie et a un 'sign' :
#       - si la citation du jour est déjà là -> rien
#       - sinon appelle l'API et met à jour profile.zodiac_sign (même colonne JSON)
#     Retourne True si mise à jour effectuée.
#     """
#     if not profile or not getattr(profile, "believes_in_astrology", False):
#         return False

#     data = dict(profile.zodiac_sign or {})
#     sign = data.get("sign")
#     if not sign:
#         return False

#     today = timezone.localdate().isoformat()
#     if data.get("date") == today and data.get("quote"):
#         return False  # déjà frais aujourd'hui

#     if not API_URL:
#         # Pas d’URL d’API configurée : on n’écrit rien
#         return False

#     headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}
#     r = requests.get(API_URL, params={"sign": sign}, headers=headers, timeout=15)
#     r.raise_for_status()
#     payload = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}

#     quote = payload.get("quote") or payload.get("text") or payload.get("message") or ""
#     author = payload.get("author") or ""

#     # écriture dans LA MÊME COLONNE JSON
#     data.update({"quote": quote, "author": author, "date": today})
#     profile.zodiac_sign = data
#     profile.save(update_fields=["zodiac_sign"])
#     return True

# def set_daily_quote_from_api(profile, quote_text: str, author: str = ""):
#     # profile.zodiac_sign est un dict (JSONField) : on le recopie pour ne pas écraser "sign"
#     payload = dict(profile.zodiac_sign or {})
#     payload.update({
#         "quote": quote_text,
#         "author": author or "",
#         "date": timezone.localdate().isoformat(),
#     })
#     profile.zodiac_sign = payload
#     profile.save(update_fields=["zodiac_sign"])
