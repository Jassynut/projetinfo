from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from datetime import timedelta, datetime
import uuid

from .models import Certificate
from .serializers_api import (
    CertificateListSerializer, CertificateDetailSerializer,
    CertificateSearchSerializer
)
from tests.models import TestAttempt

# =============================================================================
# VIEWSETS CERTIFICATES
# =============================================================================

class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour accéder aux certificats
    
    Endpoints:
    - GET /api/certificates/ - Lister mes certificats
    - GET /api/certificates/{id}/ - Détails d'un certificat
    - GET /api/certificates/{id}/download/ - Télécharger le PDF
    - POST /api/certificates/search/ - Rechercher un certificat
    - POST /api/certificates/generate-from-attempt/ - Générer à partir d'une tentative
    """
    
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CertificateDetailSerializer
        elif self.action == 'search':
            return CertificateSearchSerializer
        return CertificateListSerializer
    
    def get_queryset(self):
        """Retourner les certificats de l'utilisateur actuel"""
        return Certificate.objects.filter(
            test_attempt__user=self.request.user
        ).order_by('-issued_date')
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Télécharger le PDF du certificat"""
        certificate = self.get_object()
        
        if certificate.is_expired:
            return Response({
                'success': False,
                'error': 'Le certificat a expiré'
            }, status=status.HTTP_410_GONE)
        
        if certificate.pdf_file:
            return FileResponse(
                certificate.pdf_file.open('rb'),
                as_attachment=True,
                filename=f"certificat_{certificate.certificate_number}.pdf"
            )
        
        return Response({
            'success': False,
            'error': 'Fichier PDF non disponible'
        }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def search(self, request):
        """Rechercher un certificat par nom ou CIN"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_name = serializer.validated_data.get('user_name', '').strip()
        user_cin = serializer.validated_data.get('user_cin', '').strip().upper()
        
        if not user_name and not user_cin:
            return Response({
                'success': False,
                'error': 'Veuillez fournir un nom ou un CIN'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = Certificate.objects.all()
        
        if user_cin:
            queryset = queryset.filter(user_cin=user_cin)
        elif user_name:
            queryset = queryset.filter(user_full_name__icontains=user_name)
        
        queryset = queryset.order_by('-issued_date')[:10]
        
        if not queryset.exists():
            return Response({
                'success': False,
                'error': 'Aucun certificat trouvé'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CertificateDetailSerializer(queryset, many=True)
        
        return Response({
            'success': True,
            'count': queryset.count(),
            'certificates': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def generate_from_attempt(self, request):
        """Générer un certificat à partir d'une tentative"""
        attempt_id = request.data.get('attempt_id')
        
        if not attempt_id:
            return Response({
                'success': False,
                'error': 'attempt_id requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            attempt = TestAttempt.objects.get(id=attempt_id)
            
            # Vérifier que l'utilisateur a le droit d'accéder à cette tentative
            if attempt.user != request.user and not request.user.is_staff:
                return Response({
                    'success': False,
                    'error': 'Accès refusé'
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Vérifier que le test est réussi
            if not attempt.passed:
                return Response({
                    'success': False,
                    'error': 'Le test n\'a pas été réussi'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Vérifier si un certificat existe déjà
            if hasattr(attempt, 'certificate'):
                serializer = CertificateDetailSerializer(attempt.certificate)
                return Response({
                    'success': True,
                    'message': 'Certificat déjà existant',
                    'certificate': serializer.data
                })
            
            # Créer un nouveau certificat
            user_full_name = attempt.user.full_name or attempt.user.username
            user_cin = attempt.user.cin
            
            certificate_number = f"HSE-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            expiry_date = (datetime.now() + timedelta(days=365)).date()
            
            certificate = Certificate.objects.create(
                test_attempt=attempt,
                certificate_number=certificate_number,
                user_full_name=user_full_name,
                user_cin=user_cin,
                test_version=attempt.test.version,
                score=int(attempt.overall_score_percentage),
                expiry_date=expiry_date
            )
            
            serializer = CertificateDetailSerializer(certificate)
            
            return Response({
                'success': True,
                'message': 'Certificat généré avec succès',
                'certificate': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except TestAttempt.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Tentative non trouvée'
            }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def search_certificate_by_name(request):
    """Rechercher un certificat publiquement (sans auth)"""
    user_name = request.data.get('user_name', '').strip()
    user_cin = request.data.get('user_cin', '').strip().upper()
    
    if not user_name and not user_cin:
        return Response({
            'success': False,
            'error': 'Veuillez fournir un nom ou un CIN'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    queryset = Certificate.objects.all()
    
    if user_cin:
        queryset = queryset.filter(user_cin=user_cin)
    elif user_name:
        queryset = queryset.filter(user_full_name__icontains=user_name)
    
    queryset = queryset.order_by('-issued_date')
    
    if not queryset.exists():
        return Response({
            'success': False,
            'error': 'Aucun certificat trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = CertificateDetailSerializer(queryset[:5], many=True)
    
    return Response({
        'success': True,
        'count': queryset.count(),
        'certificates': serializer.data
    })
