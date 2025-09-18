# dream_bridge_app/forms.py
from django import forms
from django.contrib.auth import get_user_model
from accounts.models import UserProfile  # ton modèle de profil

User = get_user_model()


# =========
# DreamForm
# =========
class DreamForm(forms.Form):
    """
    Formulaire simple pour uploader un fichier audio.
    Le fichier n'est pas stocké en base : il est transmis à la tâche Celery.
    """
    audio = forms.FileField(
        label="Fichier audio",
        widget=forms.ClearableFileInput(attrs={
            "class": "form-control",
            "accept": "audio/*",
        })
    )

    def clean_audio(self):
        f = self.cleaned_data["audio"]
        # (Optionnel) Petite validation : taille max 50 Mo
        max_mb = 50
        if f.size > max_mb * 1024 * 1024:
            raise forms.ValidationError(f"Le fichier audio dépasse {max_mb} Mo.")
        return f


# =========
# UserForm
# =========
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]
        labels = {
            "first_name": "Prénom",
            "last_name": "Nom",
            "email": "Adresse e-mail",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


# =============
# ProfileForm
# =============
class ProfileForm(forms.ModelForm):
    """
    On NE permet PAS de modifier birth_date ni zodiac_sign ici.
    Seul 'believes_in_astrology' est modifiable.
    """
    class Meta:
        model = UserProfile
        fields = ["believes_in_astrology"]
        labels = {
            "believes_in_astrology": "Je crois à l’astrologie",
        }
        widgets = {
            "believes_in_astrology": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
