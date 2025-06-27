# accounts/forms.py (Version Correcte et Simplifiée)

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email") # On inclut l'email

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Supprimer les textes d'aide par défaut qui sont trop longs
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        
        # Ajouter des placeholders pour un look plus moderne
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'}
        )
        self.fields['email'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Adresse e-mail'}
        )
        self.fields['password1'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Mot de passe'}
        )
        self.fields['password2'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Confirmation du mot de passe'}
        )