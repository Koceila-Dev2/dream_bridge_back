from datetime import date
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email address")
    birth_date = forms.DateField(
        required=False,
        label="Date de naissance",
        widget=forms.DateInput(attrs={"type": "date"})
    )
    believes_in_astrology = forms.BooleanField(
        required=False,
        label="Je crois à l’astrologie"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2", "birth_date", "believes_in_astrology")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': "Nom d'utilisateur"}
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
        self.fields['birth_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['believes_in_astrology'].widget.attrs.update({'class': 'form-check-input'})

    # --- Sauvegarde + calcul du signe ---
    def save(self, commit=True):
        user = super().save(commit=True)  # besoin de l'id
        from .models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=user)

        profile.birth_date = self.cleaned_data.get("birth_date")
        profile.believes_in_astrology = bool(self.cleaned_data.get("believes_in_astrology"))

        if profile.believes_in_astrology and profile.birth_date:
            sign = self._compute_zodiac(profile.birth_date)
            profile.zodiac_sign = {"sign": sign}   # citation viendra plus tard
        else:
            profile.zodiac_sign = {}

        profile.save()
        return user


    @staticmethod
    def _compute_zodiac(d: date) -> str:
        m, day = d.month, d.day
        if (m == 3 and day >= 21) or (m == 4 and day <= 19): return "Bélier"
        if (m == 4 and day >= 20) or (m == 5 and day <= 20): return "Taureau"
        if (m == 5 and day >= 21) or (m == 6 and day <= 20): return "Gémeaux"
        if (m == 6 and day >= 21) or (m == 7 and day <= 22): return "Cancer"
        if (m == 7 and day >= 23) or (m == 8 and day <= 22): return "Lion"
        if (m == 8 and day >= 23) or (m == 9 and day <= 22): return "Vierge"
        if (m == 9 and day >= 23) or (m == 10 and day <= 22): return "Balance"
        if (m == 10 and day >= 23) or (m == 11 and day <= 21): return "Scorpion"
        if (m == 11 and day >= 22) or (m == 12 and day <= 21): return "Sagittaire"
        if (m == 12 and day >= 22) or (m == 1 and day <= 19): return "Capricorne"
        if (m == 1 and day >= 20) or (m == 2 and day <= 18): return "Verseau"
        return "Poissons"
