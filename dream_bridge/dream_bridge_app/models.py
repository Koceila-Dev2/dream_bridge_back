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


class Dream(models.Model):
    
    transcription = models.TextField('transcription du rêve')
    date = models.DateTimeField('date du rêve', default=timezone.now)
    image64 = models.TextField('image encodée en base64', blank=True, null=True)

    def __str__(self):
        return self.image64
   