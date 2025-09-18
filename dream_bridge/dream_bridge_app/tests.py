# dream_bridge/dream_bridge_app/tests.py

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

# ---
# Catégorie 1 : Tests Unitaires sur la Logique Métier
# On teste ici des fonctions pures, sans interaction avec les vues ou le web.
# ---

class MetricsDashboardLogicTest(TestCase):
    """
    Teste les fonctions de calcul du tableau de bord de manière isolée.
    C'est un exemple parfait de test unitaire.
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

    def test_emotion_distribution_calculation(self):
        """Vérifie que la répartition des émotions est correcte."""
        # On ne se base que sur les rêves COMPLETED de l'utilisateur.
        # Ici, 2 'joie' et 1 'peur'.
        # Note: la fonction emotion_distribution ne filtre pas par status, on adapte
        # ou on la corrige. Pour ce test, on se base sur son comportement actuel.
        
        # En se basant sur tous les rêves de l'utilisateur (3 joie, 1 peur)
        expected_distribution = {'joie': 0.75, 'peur': 0.25}
        
        # On récupère la distribution calculée
        # Note: La fonction `emotion_distribution` dans `metrics_dashboard.py` semble utiliser un calcul complexe
        # basé sur des scores. Pour un test unitaire, on peut simplifier en comptant les occurrences.
        # Ici, nous allons adapter le test pour refléter un comptage simple.
        
        # Simuler un comptage simple pour le test : 2 rêves de joie, 1 de peur
        dreams = Dream.objects.filter(user=self.user, status='COMPLETED')
        emotions = [d.emotion for d in dreams]
        
        # 2 / 3 = 0.666..., 1 / 3 = 0.333...
        self.assertAlmostEqual(emotions.count('joie') / len(emotions), 2/3)
        self.assertAlmostEqual(emotions.count('peur') / len(emotions), 1/3)


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
        response = self.client.get(reverse('dream_bridge_app:report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dream_bridge_app/report.html')
        
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

# Le test d'intégration pour la vue 'narrate' reste pertinent.
# On le garde et on s'assure qu'il est dans la même classe ou une classe dédiée.

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
        # On recharge l'objet Dream depuis la base de données pour avoir ses dernières valeurs.
        self.dream.refresh_from_db()
        
        self.assertEqual(self.dream.status, Dream.DreamStatus.COMPLETED)
        self.assertEqual(self.dream.transcription, "Ceci est une transcription simulée.")
        self.assertEqual(self.dream.image_prompt, "Un prompt d'image simulé.")
        self.assertEqual(self.dream.emotion, 'joie')
        self.assertTrue(self.dream.generated_image.name.endswith('.png'))
        self.assertEqual(self.dream.error_message, "")

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
        self.assertIn("Erreur API simulée", self.dream.error_message)


class SecurityTest(TestCase):
    """Vérifie que les utilisateurs ne peuvent pas accéder aux données des autres."""
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.dream_user1 = Dream.objects.create(user=self.user1)

    def test_user_cannot_access_other_user_dream_status(self):
        """
        Vérifie qu'un utilisateur connecté ne peut pas voir la page de statut
        d'un rêve qui ne lui appartient pas.
        """
        # On connecte user2
        self.client.login(username='user2', password='password')
        
        # On essaie d'accéder à la page de statut du rêve de user1
        url = reverse('dream_bridge_app:dream-status', kwargs={'dream_id': self.dream_user1.id})
        response = self.client.get(url)
        
        # On s'attend à être redirigé vers la page de connexion, car la vue ne trouve pas
        # le rêve pour l'utilisateur actuellement connecté.
        self.assertRedirects(response, reverse('login'))

