# dream_bridge_app/forms.py
from django import forms

class DreamForm(forms.Form):
    """
    Formulaire simple pour valider l'upload du fichier audio.
    """
    audio = forms.FileField(
        label="Sélectionnez votre fichier audio",
        allow_empty_file=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'audio/*'  # Aide le navigateur à filtrer les fichiers
        })
    )