# accounts/models.py
from django.db import models
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    birth_date = models.DateField(null=True, blank=True)
    believes_in_astrology = models.BooleanField(default=False)
    #zodiac_sign = models.CharField(max_length=20, blank=True)

    #def __str__(self):
        #return f"Profil de {self.user.username}"
    zodiac_sign = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Profil de {self.user.username}"

    # Helpers pratiques pour les templates
    @property
    def zodiac_sign_text(self) -> str:
        return (self.zodiac_sign or {}).get("sign", "")

    @property
    def zodiac_quote_text(self) -> str:
        return (self.zodiac_sign or {}).get("quote", "")

    @property
    def zodiac_quote_author(self) -> str:
        return (self.zodiac_sign or {}).get("author", "")

    @property
    def zodiac_quote_date(self) -> str:
        return (self.zodiac_sign or {}).get("date", "")