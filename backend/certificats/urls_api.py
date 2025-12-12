from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import CertificateViewSet, search_certificate_by_name
from .views_public import search_certificate_public_fr, download_certificate_public_fr

router = DefaultRouter()
router.register(r'', CertificateViewSet, basename='certificate-viewset')

urlpatterns = [
    path('', include(router.urls)),
    path('search-public/', search_certificate_by_name, name='search-certificate-public'),
    # Alias FR sans auth
    path('recherche/', search_certificate_public_fr, name='certificat-recherche-fr'),
    path('<int:pk>/pdf', download_certificate_public_fr, name='certificat-pdf-fr'),
]
