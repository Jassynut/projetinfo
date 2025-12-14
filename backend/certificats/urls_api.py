from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import CertificateViewSet, search_certificate_by_name
from .views_public import search_certificate_public_fr, download_certificate_public_fr

router = DefaultRouter()
router.register(r'', CertificateViewSet, basename='certificate-viewset')

urlpatterns = [
    # Routes spécifiques AVANT le router pour éviter les conflits
    path('recherche/', search_certificate_public_fr, name='certificat-recherche-fr'),
    path('search-public/', search_certificate_by_name, name='search-certificate-public'),
    path('<str:pk>/pdf', download_certificate_public_fr, name='certificat-pdf-fr'),
    # Router DRF (doit être en dernier)
    path('', include(router.urls)),
]
