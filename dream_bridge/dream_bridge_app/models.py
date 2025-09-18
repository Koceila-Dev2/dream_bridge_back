# from django.db import models
# from django.conf import settings
# from django.utils import timezone
# from django.contrib.auth.models import (
#     AbstractBaseUser, BaseUserManager, PermissionsMixin
# )
# import uuid
# from django.db import models
# from django.utils.translation import gettext_lazy as _
# from django.conf import settings 

# class Dream(models.Model):
#     """
#     Represents a single dream interpretation process, from audio to image.
#     The audio file itself is not persisted.
#     """
#     class DreamStatus(models.TextChoices):
#         PENDING = 'PENDING', _('Pending')
#         PROCESSING = 'PROCESSING', _('Processing')
#         COMPLETED = 'COMPLETED', _('Completed')
#         FAILED = 'FAILED', _('Failed')

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
#     status = models.CharField(
#         max_length=10,
#         choices=DreamStatus.choices,
#         default=DreamStatus.PENDING,
#         db_index=True,
#     )
    
#     # --- Données textuelles ---
#     transcription = models.TextField(
#         blank=True, 
#         help_text=_("The text transcribed from the audio file.")
#     )
#     image_prompt = models.TextField(
#         blank=True,
#         help_text=_("The prompt generated for the text-to-image model.")
#     )
    
#     # --- Fichier Résultat ---
#     # On utilise ImageField pour que Django gère le fichier.
#     generated_image = models.ImageField(
#         upload_to='dreams/images/',
#         null=True,
#         blank=True,
#         help_text=_("The final image generated from the dream.")
#     )
    
#     error_message = models.TextField(blank=True)

#     # --- Timestamps ---
#     # auto_now_add=True est la bonne façon de définir une date de création.
#     created_at = models.DateTimeField(auto_now_add=True)
#     # auto_now=True met à jour le champ à chaque appel de .save()
#     updated_at = models.DateTimeField(auto_now=True)



#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='dreams' # Permet d'accéder aux rêves depuis un user : user.dreams.all()
#     )

#     EMOTIONS = [
#         ('joie', 'Joie'),
#         ('tristesse', 'Tristesse'),
#         ('colère', 'Colère'),
#         ('peur', 'Peur'),
#         ('surprise', 'Surprise'),
#         ('dégoût', 'Dégoût'),
#     ]
    
#     emotion = models.CharField(max_length=20, choices=EMOTIONS)
    
#     def __str__(self) -> str:
#         """
#         Une représentation textuelle claire et concise, utile dans l'admin Django.
#         """
#         return f"Dream {self.id} ({self.status})"

# dream_bridge_app/models.py
# from django.db import models
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _
# import uuid

# class Dream(models.Model):
#     """
#     Represents a single dream interpretation process, from audio to image.
#     The audio file itself is not persisted.
#     """
#     class DreamStatus(models.TextChoices):
#         PENDING = 'PENDING', _('Pending')
#         PROCESSING = 'PROCESSING', _('Processing')
#         COMPLETED = 'COMPLETED', _('Completed')
#         FAILED = 'FAILED', _('Failed')

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

#     status = models.CharField(
#         max_length=10,
#         choices=DreamStatus.choices,
#         default=DreamStatus.PENDING,
#         db_index=True,
#     )

#     # --- Données textuelles ---
#     transcription = models.TextField(
#         blank=True,
#         help_text=_("The text transcribed from the audio file.")
#     )
#     image_prompt = models.TextField(
#         blank=True,
#         help_text=_("The prompt generated for the text-to-image model.")
#     )

#     # --- Fichier Résultat ---
#     generated_image = models.ImageField(
#         upload_to='dreams/images/',
#         null=True,
#         blank=True,
#         help_text=_("The final image generated from the dream.")
#     )

#     error_message = models.TextField(blank=True)

#     # --- Timestamps ---
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='dreams'
#     )

#     EMOTIONS = [
#         ('joie', 'Joie'),
#         ('tristesse', 'Tristesse'),
#         ('colère', 'Colère'),
#         ('peur', 'Peur'),
#         ('surprise', 'Surprise'),
#         ('dégoût', 'Dégoût'),
#     ]
#     emotion = models.CharField(max_length=20, choices=EMOTIONS)

#     def __str__(self) -> str:
#         return f"Dream {self.id} ({self.status})"


# dream_bridge_app/models.py
# from django.db import models
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _
# import uuid

# class Dream(models.Model):
#     """
#     Represents a single dream interpretation process, from audio to image.
#     The audio file itself is not persisted.
#     """
#     class DreamStatus(models.TextChoices):
#         PENDING = 'PENDING', _('Pending')
#         PROCESSING = 'PROCESSING', _('Processing')
#         COMPLETED = 'COMPLETED', _('Completed')
#         FAILED = 'FAILED', _('Failed')

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

#     status = models.CharField(
#         max_length=10,
#         choices=DreamStatus.choices,
#         default=DreamStatus.PENDING,
#         db_index=True,
#     )

#     # --- Données textuelles ---
#     transcription = models.TextField(blank=True, help_text=_("The text transcribed from the audio file."))
#     image_prompt  = models.TextField(blank=True, help_text=_("The prompt generated for the text-to-image model."))

#     # ✅ NOUVELLES COLONNES
#     phrase      = models.TextField(blank=True, default="", help_text=_("Daily quote / astro message"))
#     phrase_date = models.DateField(null=True, blank=True, help_text=_("Date when 'phrase' was last updated"))

#     # --- Fichier Résultat ---
#     generated_image = models.ImageField(
#         upload_to='dreams/images/', null=True, blank=True,
#         help_text=_("The final image generated from the dream.")
#     )

#     error_message = models.TextField(blank=True)

#     # --- Timestamps ---
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dreams')

#     EMOTIONS = [
#         ('joie', 'Joie'),
#         ('tristesse', 'Tristesse'),
#         ('colère', 'Colère'),
#         ('peur', 'Peur'),
#         ('surprise', 'Surprise'),
#         ('dégoût', 'Dégoût'),
#     ]
#     emotion = models.CharField(max_length=20, choices=EMOTIONS)

#     def __str__(self) -> str:
#         return f"Dream {self.id} ({self.status})"

# from django.db import models
# from django.conf import settings
# from django.utils.translation import gettext_lazy as _
# import uuid

# class Dream(models.Model):
#     """
#     Represents a single dream interpretation process, from audio to image.
#     The audio file itself is not persisted.
#     """
#     class DreamStatus(models.TextChoices):
#         PENDING = 'PENDING', _('Pending')
#         PROCESSING = 'PROCESSING', _('Processing')
#         COMPLETED = 'COMPLETED', _('Completed')
#         FAILED = 'FAILED', _('Failed')

#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

#     status = models.CharField(
#         max_length=10,
#         choices=DreamStatus.choices,
#         default=DreamStatus.PENDING,
#         db_index=True,
#     )

#     # --- Données textuelles ---
#     transcription = models.TextField(
#         blank=True, help_text=_("The text transcribed from the audio file.")
#     )
#     image_prompt = models.TextField(
#         blank=True, help_text=_("The prompt generated for the text-to-image model.")
#     )

#     # ✅ Nouvelles colonnes (phrase du jour / horoscope)
#     phrase = models.TextField(
#         blank=True, default="", help_text=_("Daily quote / astro message")
#     )
#     phrase_date = models.DateField(
#         null=True, blank=True, help_text=_("Date when 'phrase' was last updated")
#     )

#     # --- Fichier résultat ---
#     generated_image = models.ImageField(
#         upload_to='dreams/images/', null=True, blank=True,
#         help_text=_("The final image generated from the dream.")
#     )

#     error_message = models.TextField(blank=True)

#     # --- Timestamps ---
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dreams'
#     )

#     EMOTIONS = [
#         ('joie', 'Joie'),
#         ('tristesse', 'Tristesse'),
#         ('colère', 'Colère'),
#         ('peur', 'Peur'),
#         ('surprise', 'Surprise'),
#         ('dégoût', 'Dégoût'),
#     ]
   
#     emotion = models.CharField(
#         max_length=20, 
#         choices=EMOTIONS, 
#         default='neutre', 
#         blank=True
#     )    
    
#     def __str__(self) -> str:
#         return f"Dream {self.id} ({self.status})"


from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid

class Dream(models.Model):
    """
    Represents a single dream interpretation process, from audio to image.
    The audio file itself is not persisted.
    """
    class DreamStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PROCESSING = 'PROCESSING', _('Processing')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    status = models.CharField(
        max_length=10,
        choices=DreamStatus.choices,
        default=DreamStatus.PENDING,
        db_index=True,
    )

    # --- Données textuelles ---
    transcription = models.TextField(
        blank=True, help_text=_("The text transcribed from the audio file.")
    )
    image_prompt = models.TextField(
        blank=True, help_text=_("The prompt generated for the text-to-image model.")
    )

    # ✅ Message générique (citation/horoscope) éventuel
    phrase = models.TextField(
        blank=True, default="", help_text=_("Daily quote / astro message")
    )
    phrase_date = models.DateField(
        null=True, blank=True, help_text=_("Date when 'phrase' was last updated")
    )

    # ✅ NOUVEAU : message PERSONNALISÉ lié au rêve
    personal_phrase = models.TextField(
        blank=True, default="", help_text=_("Personalized message based on the dream.")
    )
    personal_phrase_date = models.DateField(
        null=True, blank=True, help_text=_("Date when 'personal_phrase' was last updated")
    )

    # --- Fichier résultat ---
    generated_image = models.ImageField(
        upload_to='dreams/images/', null=True, blank=True,
        help_text=_("The final image generated from the dream.")
    )

    error_message = models.TextField(blank=True)

    # --- Timestamps ---
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dreams'
    )

    EMOTIONS = [
        ('neutre', 'Neutre'),     # ✅ ajouté pour matcher le default
        ('joie', 'Joie'),
        ('tristesse', 'Tristesse'),
        ('colère', 'Colère'),
        ('peur', 'Peur'),
        ('surprise', 'Surprise'),
        ('dégoût', 'Dégoût'),
    ]
    emotion = models.CharField(
        max_length=20,
        choices=EMOTIONS,
        default='neutre',
        blank=True
    )

    def __str__(self) -> str:
        return f"Dream {self.id} ({self.status})"
