from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
from datetime import timedelta
from unittest.mock import patch, MagicMock
from django.utils import timezone
from .services import *
from .models import Dream
from .metrics_dashboard import total_dreams, emotion_distribution
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import UserProfile



# --- Catégorie 9 : Edge cases pour DreamForm et Dream model ---
class DreamFormEdgeCaseTest(TestCase):
    """
    Teste les cas limites du formulaire DreamForm (données invalides, valeurs inattendues).
    """
    def setUp(self):
        self.user = User.objects.create_user(username='dreamedge', password='password')

    def test_form_invalid_emotion(self):
        """Le formulaire doit être invalide si l'émotion n'est pas dans la liste."""
        form_data = {
            'emotion': 'inconnue',  # valeur non autorisée
        }
        form = DreamForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_empty_data(self):
        """Le formulaire doit être invalide si tous les champs sont vides."""
        form = DreamForm(data={})
        self.assertFalse(form.is_valid())


  
# --- Catégorie 10 : API error/security tests ---
class DreamStatusApiErrorTest(TestCase):
    """
    Teste les erreurs et la sécurité de l'API check_dream_status_api.
    """
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='dreamapierr', password='password')
        self.client.login(username=self.user.username, password='password')
        self.dream = Dream.objects.create(user=self.user, status='COMPLETED')

    def test_api_invalid_id(self):
        """L'API doit retourner 404 si l'id n'existe pas."""
        import uuid
        fake_id = uuid.uuid4()
        url = reverse('dream_bridge_app:check-dream-status-api', kwargs={'dream_id': fake_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_api_permission_denied(self):
        """L'API doit retourner 404 si l'utilisateur n'a pas accès au rêve."""
        other_user = User.objects.create_user(username='otherapi', password='password')
        self.client.login(username=other_user.username, password='password')
        url = reverse('dream_bridge_app:check-dream-status-api', kwargs={'dream_id': self.dream.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
# --- Catégorie 6 : Tests sur les formulaires DreamForm ---
from .forms import DreamForm

class DreamFormTest(TestCase):
    """
    Teste la validation du formulaire DreamForm.
    Vérifie que le formulaire accepte et rejette correctement les données.
    """
    def setUp(self):
        self.user = User.objects.create_user(username='dreamformuser', password='password')

    def test_form_valid_data(self):
        """Le formulaire doit être valide avec un fichier audio correct."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        audio_file = SimpleUploadedFile("dream.webm", b"fake audio content", content_type="audio/webm")
        form_data = {}
        form_files = {'audio': audio_file}
        form = DreamForm(data=form_data, files=form_files)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_form_missing_audio(self):
        """Le formulaire doit être invalide si le fichier audio est manquant."""
        form_data = {}
        form = DreamForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_form_audio_too_large(self):
        """Le formulaire doit être invalide si le fichier audio dépasse la taille max."""
        big_content = b"0" * (51 * 1024 * 1024)  # 51 Mo
        audio_file = SimpleUploadedFile("big_audio.webm", big_content, content_type="audio/webm")
        form_data = {}
        form_files = {'audio': audio_file}
        form = DreamForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())

# --- Catégorie 7 : Tests sur le modèle UserProfile ---


class UserProfileModelTest(TestCase):
    """
    Teste le modèle UserProfile pour s'assurer que les propriétés fonctionnent correctement.
    """
    def test_zodiac_sign_text_property(self):
        """Vérifie que zodiac_sign_text retourne le bon texte."""
        user = User.objects.create_user(username='astro', password='password')
        profile = UserProfile.objects.create(user=user, zodiac_sign='Verseau')
        self.assertEqual(profile.zodiac_sign_text, 'Verseau')

    def test_str_method(self):
        """Vérifie que __str__ retourne un affichage utile."""
        user = User.objects.create_user(username='astro2', password='password')
        profile = UserProfile.objects.create(user=user, zodiac_sign='Lion')
        self.assertIn('Lion', str(profile))
        self.assertIn(user.username, str(profile))

# --- Catégorie 8 : Test API de statut du rêve ---
class DreamStatusApiTest(TestCase):
    """
    Teste l'API check_dream_status_api pour s'assurer qu'elle retourne le bon statut.
    """
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='dreamapi', password='password')
        self.client.login(username=self.user.username, password='password')
        self.dream = Dream.objects.create(user=self.user, status='COMPLETED')

    def test_api_returns_completed_status(self):
        url = reverse('dream_bridge_app:check-dream-status-api', kwargs={'dream_id': self.dream.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'COMPLETED')

    def test_api_returns_404_for_other_user(self):
        other_user = User.objects.create_user(username='otherdream', password='password')
        self.client.login(username=other_user.username, password='password')
        url = reverse('dream_bridge_app:check-dream-status-api', kwargs={'dream_id': self.dream.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

# =======
# Catégorie 1 : Tests Unitaires sur la Logique Métier
# =======

class MetricsDashboardLogicTest(TestCase):
    """
    Teste les fonctions de calcul du tableau de bord de manière isolée
    """
    def setUp(self):
        """
        On crée un utilisateur et plusieurs rêves avec des caractéristiques
        différentes pour pouvoir tester nos calculs.
        """
        self.user = User.objects.create_user(username='testmetrics', password='password')
        now = timezone.now()

        # Création de rêves pour les tests
        Dream.objects.create(user=self.user, status='COMPLETED', emotion='joie', created_at=now - timedelta(days=1))
        Dream.objects.create(user=self.user, status='COMPLETED', emotion='joie', created_at=now - timedelta(days=2))
        Dream.objects.create(user=self.user, status='COMPLETED', emotion='peur', created_at=now - timedelta(days=5))
        Dream.objects.create(user=self.user, status='PENDING', emotion='joie', created_at=now) # Ne doit pas être compté dans certaines stats
        
        # Un rêve pour un autre utilisateur, pour s'assurer qu'il n'est pas compté
        other_user = User.objects.create_user(username='otheruser', password='password')
        Dream.objects.create(user=other_user, status='COMPLETED', emotion='tristesse')

    def test_total_dreams_calculation(self):
        """Vérifie que la fonction total_dreams compte correctement les rêves de l'utilisateur."""
        # On attend 4 rêves au total pour self.user (3 completed, 1 pending)
        self.assertEqual(total_dreams(self.user, period="all"), 4)
        # On attend 4 rêves sur les 7 derniers jours
        self.assertEqual(total_dreams(self.user, period="7d"), 4)




# ---
# Catégorie 2 : Tests d'Intégration sur les Vues
# On teste ici le comportement complet d'une page, de la requête à la réponse.
# ---

class DreamAppViewsTest(TestCase):
    """
    Teste les vues principales de l'application (dashboard, galerie, etc.).
    C'est un exemple de test d'intégration.
    """
    def setUp(self):
        """Mise en place commune pour les tests de vues."""
        self.client = Client()
        self.password = 'a-strong-password'
        self.user = User.objects.create_user(username='testuser', password=self.password)
        self.client.login(username=self.user.username, password=self.password)
        
        fake_image_content = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        
        # On crée des rêves de test AVEC une image.
        dream1 = Dream.objects.create(user=self.user, status='COMPLETED', emotion='joie', transcription="Un beau rêve.")
        dream1.generated_image.save('test1.gif', SimpleUploadedFile('test1.gif', fake_image_content, 'image/gif'))
        
        dream2 = Dream.objects.create(user=self.user, status='COMPLETED', emotion='peur', transcription="Un cauchemar.")
        dream2.generated_image.save('test2.gif', SimpleUploadedFile('test2.gif', fake_image_content, 'image/gif'))

    def test_report_view_authenticated(self):
        """Vérifie que le rapport s'affiche et contient les bonnes données."""
        response = self.client.get(reverse('dream_bridge_app:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dream_bridge_app/dashboard.html')
        
        # Vérifie que les données calculées sont bien présentes dans le contexte du template
        self.assertIn('total_dreams', response.context)
        self.assertIn('emotion_distribution', response.context)
        self.assertEqual(response.context['total_dreams'], 2)

    def test_galerie_view(self):
        """Vérifie que la galerie s'affiche et contient les rêves."""
        response = self.client.get(reverse('dream_bridge_app:galerie'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dream_bridge_app/galerie.html')
        
        # Le contexte 'images' doit contenir nos 2 rêves
        self.assertEqual(len(response.context['images']), 2)

    def test_galerie_view_filter_by_emotion(self):
        """Vérifie que le filtre par émotion de la galerie fonctionne."""
        url = reverse('dream_bridge_app:galerie')
        # On ajoute le paramètre GET `?emotion=joie`
        response = self.client.get(f"{url}?emotion=joie")
        
        self.assertEqual(response.status_code, 200)
        # Le contexte ne doit contenir que le rêve de joie
        self.assertEqual(len(response.context['images']), 1)
        self.assertEqual(response.context['images'][0].emotion, 'joie')



class DreamCreateViewIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = 'a-strong-password'
        self.user = User.objects.create_user(username='testuser', password=self.password)
        self.client.login(username=self.user.username, password=self.password)
        self.narrate_url = reverse('dream_bridge_app:narrate')

    @patch('dream_bridge_app.views.process_dream_audio_task.delay')
    def test_post_audio_creates_dream_and_starts_task(self, mock_celery_task_delay):
        fake_audio_content = b'ceci est un faux fichier audio'
        audio_file = SimpleUploadedFile("dream.webm", fake_audio_content, content_type="audio/webm")
        response = self.client.post(self.narrate_url, {'audio': audio_file})
        
        self.assertEqual(Dream.objects.count(), 1)
        dream = Dream.objects.first()
        self.assertEqual(dream.user, self.user)
        
        mock_celery_task_delay.assert_called_once()
        
        self.assertEqual(response.status_code, 302)
        expected_redirect_url = reverse('dream_bridge_app:dream-status', kwargs={'dream_id': dream.id})
        self.assertRedirects(response, expected_redirect_url)

class ServicesLogicTest(TestCase):
    """
    Teste la fonction d'orchestration `orchestrate_dream_generation` en simulant
    les appels aux API externes (Groq, Mistral) pour ne pas dépendre d'eux.
    """
    def setUp(self):
        self.user = User.objects.create_user(username='testservices', password='password')
        self.dream = Dream.objects.create(user=self.user)
    
    # Le décorateur @patch intercepte les appels aux fonctions spécifiées
    # et les remplace par des "mocks" (simulateurs) que l'on peut contrôler.
    @patch('dream_bridge_app.services.Mistral')
    @patch('dream_bridge_app.services.Groq')
    @patch('dream_bridge_app.services.get_emotion_from_text')
    def test_orchestrate_dream_generation_success(self, mock_get_emotion, mock_groq, mock_mistral):
        """
        Teste le scénario idéal où toutes les API répondent correctement.
        
        Args:
            mock_get_emotion: Le mock pour la fonction d'analyse d'émotion.
            mock_groq: Le mock pour le client Groq.
            mock_mistral: Le mock pour le client Mistral.
            (L'ordre est inversé par rapport aux décorateurs)
        """
        # --- 1. Arrange (Préparation) ---
        # On configure le comportement de nos mocks pour qu'ils retournent des fausses données.
        
        # Simuler la réponse de Groq pour la transcription
        mock_groq.return_value.audio.transcriptions.create.return_value.text = "Ceci est une transcription simulée."
        # Simuler la réponse de Groq pour la génération de prompt
        mock_groq.return_value.chat.completions.create.return_value.choices[0].message.content = "Un prompt d'image simulé."
        
        # Simuler la réponse de notre fonction d'analyse d'émotion
        mock_get_emotion.return_value = 'joie'
        
        # Simuler la réponse de Mistral AI pour la génération d'image
        mock_mistral.return_value.beta.agents.create.return_value = MagicMock()
        mock_mistral.return_value.files.download.return_value.read.return_value = b'fausses_donnees_image'
        
        # --- 2. Act (Action) ---
        # On appelle la fonction que l'on veut tester.
        orchestrate_dream_generation(str(self.dream.id), 'fake/path/to/audio.webm')
        
        # --- 3. Assert (Vérification) ---
    def test_dashboard_view_authenticated(self):
        """Vérifie que le dashboard s'affiche et contient les bonnes données."""
        self.client.login(username=self.user.username, password='password')
        response = self.client.get(reverse('dream_bridge_app:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dream_bridge_app/dashboard.html')
        self.assertIn('total_dreams', response.context)
        self.assertIn('emotion_distribution', response.context)
        self.assertEqual(response.context['total_dreams'], 1)

    @patch('dream_bridge_app.services.Groq')
    def test_orchestrate_dream_generation_api_failure(self, mock_groq):
        """
        Teste le scénario où une des API lève une exception.
        """
        # --- 1. Arrange ---
        # On configure le mock de Groq pour qu'il simule une erreur.
        mock_groq.return_value.audio.transcriptions.create.side_effect = Exception("Erreur API simulée")
        
        # --- 2. Act ---
        orchestrate_dream_generation(str(self.dream.id), 'fake/path/to/audio.webm')
        
        # --- 3. Assert ---
        self.dream.refresh_from_db()
        
        self.assertEqual(self.dream.status, Dream.DreamStatus.FAILED)
        self.assertIn("Une erreur est survenue lors du traitement: [Errno 2] No such file or directory: 'fake/path/to/audio.webm'", self.dream.error_message)
class SecurityTest(TestCase):
    """Vérifie que les utilisateurs ne peuvent pas accéder aux données des autres."""
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.dream_user1 = Dream.objects.create(user=self.user1)

    def test_user_cannot_access_other_user_dream_status(self):
        """
        Vérifie qu'un utilisateur connecté ne peut pas voir la page de statut d'un rêve qui ne lui appartient pas.
        """
        # On connecte user2
        self.client.login(username='user2', password='password')
        
        # On essaie d'accéder à la page de statut du rêve de user1
        url = reverse('dream_bridge_app:dream-status', kwargs={'dream_id': self.dream_user1.id})
        response = self.client.get(url)
        
       
        self.assertEqual(response.status_code, 404)


# ---
# Catégorie 3 : Tests Unitaires sur le modèle Dream
# ---
class DreamModelTest(TestCase):
    """
    Teste les méthodes personnalisées du modèle Dream.
    Permet de s'assurer que la logique métier du modèle fonctionne comme attendu.
    """
    def setUp(self):
        self.user = User.objects.create_user(username='dreamer', password='password')

    def test_str_method(self):
        """
        Vérifie que la méthode __str__ retourne le bon format (id et statut).
        C'est utile pour l'affichage dans l'admin Django et le debug.
        """
        dream = Dream.objects.create(user=self.user, status='COMPLETED', emotion='joie')
        self.assertIn(str(dream.id), str(dream))
        self.assertIn('COMPLETED', str(dream))

    def test_get_emotion_display(self):
        """
        Vérifie que get_emotion_display retourne le label correct pour l'émotion.
        Permet d'afficher le bon texte dans les templates.
        """
        dream = Dream.objects.create(user=self.user, status='COMPLETED', emotion='joie')
        self.assertEqual(dream.get_emotion_display(), 'Joie')


# ---
# Catégorie 4 : Tests Unitaires sur les services
# ---
class ServicesTest(TestCase):
    """
    Teste les fonctions utilitaires du module services.
    Ici, on vérifie la détection d'émotion sur un texte simple.
    """
    def test_get_emotion_from_text(self):
        """
        Teste la fonction get_emotion_from_text sur un texte positif.
        On s'attend à ce que l'émotion retournée soit dans la liste des émotions connues.
        """
        text = "C'était une journée merveilleuse et pleine de bonheur."
        emotion = get_emotion_from_text(text)
        self.assertIn(emotion, ['joie', 'tristesse', 'colère', 'peur', 'surprise', 'dégoût', 'neutre'])


# ---
# Catégorie 5 : Tests Unitaires sur les tâches Celery
# ---
from unittest.mock import patch
from .tasks import *

class TasksTest(TestCase):
    """
    Teste la tâche Celery process_dream_audio_task.
    On vérifie que la fonction d'orchestration est appelée et que le fichier temporaire est supprimé.
    """
    @patch('dream_bridge_app.tasks.orchestrate_dream_generation')
    @patch('os.remove')
    def test_process_dream_audio_task_deletes_temp_file(self, mock_remove, mock_orchestrate):
        """
        Vérifie que le fichier temporaire est supprimé après traitement.
        On mocke orchestrate_dream_generation pour ne pas exécuter la vraie logique.
        """
        temp_path = '/tmp/fake_audio.wav'
        process_dream_audio_task('fake_id', temp_path)
        mock_orchestrate.assert_called_once_with('fake_id', temp_path)
        mock_remove.assert_called_once_with(temp_path)
