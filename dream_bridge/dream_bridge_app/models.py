
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid


class Dream(models.Model):
    """
    Represents a single dream interpretation process,
    from audio to image.
    The audio file itself is not persisted.
    """
    class DreamStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PROCESSING = 'PROCESSING', _('Processing')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    status = models.CharField(
        max_length=10,
        choices=DreamStatus.choices,
        default=DreamStatus.PENDING,
        db_index=True,
    )

    # --- Données textuelles ---
    transcription = models.TextField(
        blank=True,
        help_text=_("The text transcribed from the audio file.")
    )
    image_prompt = models.TextField(
        blank=True,
        help_text=_("The prompt generated for the text-to-image model.")
    )

    phrase = models.TextField(
        blank=True,
        default="",
        help_text=_("Daily quote / astro message")
    )
    phrase_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Date when 'phrase' was last updated")
    )

    # ✅ NOUVEAU : message PERSONNALISÉ lié au rêve
    personal_phrase = models.TextField(
        blank=True,
        default="",
        help_text=_("Personalized message based on the dream.")
    )
    personal_phrase_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Date when 'personal_phrase' was last updated")
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
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='dreams'
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
