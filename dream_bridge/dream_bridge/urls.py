# dream_bridge/urls.py (Version finale et complète)
from django.contrib import admin
from django.urls import path, include

# On importe les deux lignes nécessaires
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    # Inclure les URLs de notre application dream_bridge_app
    path('', include('dream_bridge_app.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
] 

if settings.DEBUG:
    # On dit à Django d'ajouter une nouvelle règle :
    # "Pour toute URL qui commence par MEDIA_URL, va chercher le fichier correspondant
    # dans le dossier MEDIA_ROOT."
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)