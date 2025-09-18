from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date
from .forms import CustomUserCreationForm

class ZodiacSignTestCase(TestCase):
    """
    Cette classe de test vérifie de manière unitaire la logique de calcul
    du signe astrologique dans le formulaire d'inscription.
    """

    def test_compute_zodiac_sign(self):
        """
        Teste la fonction _compute_zodiac avec des dates clés pour s'assurer
        qu'elle retourne le bon signe.
        """
        # Création d'une instance du formulaire pour accéder à sa méthode statique
        form = CustomUserCreationForm()

        # Dictionnaire de cas de test 
        test_cases = {
            date(2000, 3, 21): "Bélier",
            date(2000, 4, 19): "Bélier",
            date(2000, 4, 20): "Taureau",
            date(2000, 12, 22): "Capricorne",
            date(2000, 1, 19): "Capricorne",
            date(2000, 1, 20): "Verseau",
            date(2000, 2, 19): "Poissons",
        }

        for birth_date, expected_sign in test_cases.items():
            # On utilise subTest pour que si un cas échoue, les autres continuent et on sait exactement lequel a posé problème.
            with self.subTest(birth_date=birth_date):
                self.assertEqual(form._compute_zodiac(birth_date), expected_sign)

class UserCreationTestCase(TestCase):
    """
    Teste la création complète d'un utilisateur et de son profil.
    """
    def test_user_and_profile_creation(self):
        """
        Vérifie que la soumission du CustomUserCreationForm crée bien un User
        ET un UserProfile associé avec les bonnes informations.
        """
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'a-strong-password',
            'password2': 'a-strong-password',
            'birth_date': '1995-05-21', # Gémeaux
            'believes_in_astrology': True
        }
        form = CustomUserCreationForm(data=form_data)

        # On vérifie que le formulaire est valide
        self.assertTrue(form.is_valid())

        # On sauvegarde le formulaire
        user = form.save()

        # On vérifie que l'utilisateur a bien été créé
        self.assertIsInstance(user, User)
        self.assertEqual(User.objects.count(), 1)
        
        # On vérifie que le profil a été créé et correctement rempli
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.birth_date, date(1995, 5, 21))
        self.assertTrue(user.profile.believes_in_astrology)
        self.assertEqual(user.profile.zodiac_sign, "Gémeaux")
