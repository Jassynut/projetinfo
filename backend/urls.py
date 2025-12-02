# backend/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Interface d'administration Django
    path('admin/', admin.site.urls),
    
    # API Authentication (TestUsers et QR codes)
    path('api/auth/', include('authentication.urls')),     # ← SI ton app s'appelle authentication
    
    # API HSE (Tests, questions, résultats)
    path('api/hse_app/', include('hse_app.urls')),    
    # API Tests (si tu as une app séparée pour les tests généraux)
    path('api/tests/', include('tests.urls')),
    
    # API Dashboard (statistiques)
    path('api/dashboard/', include('dashboard.urls')),
    
    # API certificats (si séparé)
    path('api/certificats/', include('certificats.urls')),

]

# Pour servir les fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Pour les pages d'erreur personnalisées
handler404 = 'backend.views.handler404'
handler500 = 'backend.views.handler500'