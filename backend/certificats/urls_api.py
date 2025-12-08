from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import CertificateViewSet, search_certificate_by_name

router = DefaultRouter()
router.register(r'', CertificateViewSet, basename='certificate')

urlpatterns = [
    path('', include(router.urls)),
    path('search-public/', search_certificate_by_name, name='search-certificate-public'),
]
