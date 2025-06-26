from django.db import models
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, nom, prenom, date_naissance, password=None, **extra_fields):
#         if not email:
#             raise ValueError('L’utilisateur doit avoir une adresse email')
#         email = self.normalize_email(email)
#         user = self.model(
#             email=email,
#             nom=nom,
#             prenom=prenom,
#             date_naissance=date_naissance,
#             **extra_fields
#         )
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, nom, prenom, date_naissance, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Le superutilisateur doit avoir is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Le superutilisateur doit avoir is_superuser=True.')
#         return self.create_user(email, nom, prenom, date_naissance, password, **extra_fields)


# class CustomUser(AbstractBaseUser, PermissionsMixin):
#     """
#     Modèle utilisateur personnalisé.
#     Champs : id, nom, prénom, email, rôle, date de naissance, mot de passe (hashé), astrologie, date d’inscription.
#     """
#     email = models.EmailField('email', unique=True)
#     nom = models.CharField('nom', max_length=150)
#     prenom = models.CharField('prénom', max_length=150)
#     role = models.CharField('rôle', max_length=100)
#     date_naissance = models.DateField('date de naissance')
#     astrologie = models.CharField('signe astrologique', max_length=50, blank=True, null=True)
#     date_inscription = models.DateTimeField('date d’inscription', auto_now_add=True)

#     is_active = models.BooleanField('actif', default=True)
#     is_staff = models.BooleanField('membre du staff', default=False)

#     objects = CustomUserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['nom', 'prenom', 'date_naissance']

#     class Meta:
#         verbose_name = 'utilisateur'
#         verbose_name_plural = 'utilisateurs'

#     def __str__(self):
#         return f"{self.prenom} {self.nom} <{self.email}>"


# dream_bridge_app/models.py
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

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
        blank=True, 
        help_text=_("The text transcribed from the audio file.")
    )
    image_prompt = models.TextField(
        blank=True,
        help_text=_("The prompt generated for the text-to-image model.")
    )
    
    # --- Fichier Résultat ---
    # On utilise ImageField pour que Django gère le fichier.
    generated_image = models.ImageField(
        upload_to='dreams/images/',
        null=True,
        blank=True,
        help_text=_("The final image generated from the dream.")
    )
    
    error_message = models.TextField(blank=True)

    # --- Timestamps ---
    # auto_now_add=True est la bonne façon de définir une date de création.
    created_at = models.DateTimeField(auto_now_add=True)
    # auto_now=True met à jour le champ à chaque appel de .save()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        """
        Une représentation textuelle claire et concise, utile dans l'admin Django.
        """
        return f"Dream {self.id} ({self.status})"