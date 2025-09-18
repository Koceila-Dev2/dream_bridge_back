# dream_bridge_app/urls.py
from django.urls import path
from . import views

app_name = "dream_bridge_app"

urlpatterns = [
    path("", views.home, name="home"),
    path("accueil/", views.dashboard, name="accueil"),
    path("narrate/", views.dream_create_view, name="narrate"),
    path("dashboard/", views.report, name="dashboard"),
    path("galerie/", views.galerie_filtree, name="galerie"),

    # Détail d’un rêve
    path("dreams/<uuid:dream_id>/status/", views.dream_status_view, name="dream-status"),
    path("api/dreams/<uuid:dream_id>/status/", views.check_dream_status_api, name="check-dream-status-api"),

    # Action : personnaliser un rêve
    #path("dreams/<uuid:dream_id>/personalize/", views.generate_personal_message_view, name="dream-personalize"),

    # Profil (optionnel, mais tu as aussi un dans accounts → à harmoniser)
    path("profile/", views.profile_view, name="profile"),
]
