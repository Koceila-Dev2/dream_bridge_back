from django.db import models
from django.conf import settings
import json

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    birth_date = models.DateField(null=True, blank=True)
    zodiac_sign = models.CharField(max_length=20, blank=True)
    believes_in_astrology = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        """
        Normalise la valeur de zodiac_sign :
        - dict -> prend la clé 'sign'
        - str JSON {'sign': '...'} -> parse et prend 'sign'
        - sinon -> garde le texte tel quel
        """
        val = self.zodiac_sign

        # Cas 1 : on nous donne déjà un dict
        if isinstance(val, dict):
            val = val.get("sign") or ""

        # Cas 2 : on nous donne une chaîne qui ressemble à du JSON
        elif isinstance(val, str):
            s = val.strip()
            if s.startswith("{") and s.endswith("}"):
                try:
                    obj = json.loads(s)
                    if isinstance(obj, dict):
                        val = obj.get("sign", val)
                except Exception:
                    pass  # si parse échoue, on garde la valeur telle quelle

        # Nettoyage final
        self.zodiac_sign = (val or "").strip()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Profil de {self.user.username}"

    # --- Compatibilité / helpers pour les templates ---
    @property
    def zodiac_sign_text(self) -> str:
        """Retourne le signe (texte simple)."""
        return self.zodiac_sign or ""

    @property
    def zodiac_quote_text(self) -> str:
        """Plus de citation stockée ici -> chaîne vide (compat)."""
        return ""

    @property
    def zodiac_quote_author(self) -> str:
        return ""

    @property
    def zodiac_quote_date(self) -> str:
        return ""
