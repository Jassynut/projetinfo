from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count
from django.utils import timezone
from datetime import timedelta

from .models import HSEUser, HSEManager
from .serializers import (
    HSEUserListSerializer, HSEUserDetailSerializer, HSEUserCreateUpdateSerializer,
    HSEUserPresenceSerializer, HSEManagerListSerializer, HSEManagerDetailSerializer,
    HSEManagerCreateUpdateSerializer
)
from tests.models import Test, TestAttempt
from tests.serializers_api import (
    TestListSerializer, TestDetailSerializer, TestCreateUpdateSerializer,
    TestAttemptListSerializer, TestAttemptDetailSerializer
)

# =============================================================================
# VIEWSETS HSE USERS
# =============================================================================

class HSEUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les utilisateurs HSE
    
    Endpoints:
    - GET /api/hse/users/ - Lister tous les utilisateurs
    - POST /api/hse/users/ - Créer un utilisateur
    - GET /api/hse/users/{id}/ - Détails d'un utilisateur
    - PUT /api/hse/users/{id}/ - Modifier un utilisateur
    - PATCH /api/hse/users/{id}/ - Modification partielle
    - DELETE /api/hse/users/{id}/ - Supprimer un utilisateur
    - PATCH /api/hse/users/{id}/update-presence/ - Modifier présence
    - GET /api/hse/users/{id}/test-history/ - Historique des tests
    - GET /api/hse/users/search/?cin=xxx - Rechercher par CIN
    """
    
    queryset = HSEUser.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = PageNumberPagination
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HSEUserDetailSerializer
        elif self.action == 'update-presence':
            return HSEUserPresenceSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return HSEUserCreateUpdateSerializer
        return HSEUserListSerializer
    
    def get_queryset(self):
        queryset = HSEUser.objects.all()
        
        cin = self.request.query_params.get('cin')
        if cin:
            queryset = queryset.filter(cin__icontains=cin)
        
        # Filtrer par entité
        entite = self.request.query_params.get('entite')
        if entite:
            queryset = queryset.filter(entite__icontains=entite)
        
        # Filtrer par entreprise
        entreprise = self.request.query_params.get('entreprise')
        if entreprise:
            queryset = queryset.filter(entreprise__icontains=entreprise)
        
        # Filtrer par présence
        presence = self.request.query_params.get('presence')
        if presence in ['true', 'false']:
            queryset = queryset.filter(presence=presence.lower() == 'true')
        
        # Filtrer par réussite
        reussite = self.request.query_params.get('reussite')
        if reussite in ['true', 'false']:
            queryset = queryset.filter(reussite=reussite.lower() == 'true')
        
        return queryset.order_by('-updated_at')
    
    @action(detail=True, methods=['patch'])
    def update_presence(self, request, pk=None):
        """Mettre à jour la présence d'un utilisateur"""
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user.presence = serializer.validated_data['presence']
        user.save()
        
        return Response({
            'success': True,
            'message': 'Présence mise à jour',
            'presence': user.presence
        })
    
    @action(detail=True, methods=['get'])
    def test_history(self, request, pk=None):
        """Récupérer l'historique des tests d'un utilisateur"""
        user = self.get_object()
        
        if user.test_user:
            attempts = user.test_user.testattempt_set.all().order_by('-started_at')
            serializer = TestAttemptListSerializer(attempts, many=True)
            
            return Response({
                'success': True,
                'user_id': user.id,
                'attempts_count': attempts.count(),
                'attempts': serializer.data
            })
        
        return Response({
            'success': True,
            'attempts_count': 0,
            'attempts': []
        })
    
    @action(detail=False, methods=['get'])
    def search_by_cin(self, request):
        """Rechercher un utilisateur par CIN"""
        cin = request.query_params.get('cin', '').strip().upper()
        
        if not cin:
            return Response({
                'success': False,
                'error': 'CIN requis'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = HSEUser.objects.get(cin=cin)
            serializer = HSEUserDetailSerializer(user)
            return Response({
                'success': True,
                'user': serializer.data
            })
        except HSEUser.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Utilisateur non trouvé'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Statistiques globales des utilisateurs"""
        total_users = HSEUser.objects.count()
        present_users = HSEUser.objects.filter(presence=True).count()
        successful_users = HSEUser.objects.filter(reussite=True).count()
        avg_score = HSEUser.objects.aggregate(Avg('score'))['score__avg'] or 0
        
        return Response({
            'success': True,
            'statistics': {
                'total_users': total_users,
                'present_users': present_users,
                'present_percentage': round((present_users / total_users * 100) if total_users > 0 else 0, 1),
                'successful_users': successful_users,
                'success_rate': round((successful_users / total_users * 100) if total_users > 0 else 0, 1),
                'average_score': round(avg_score, 2)
            }
        })


# =============================================================================
# VIEWSETS MANAGERS
# =============================================================================

class HSEManagerViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les managers HSE
    
    Endpoints:
    - GET /api/hse/managers/ - Lister tous les managers
    - POST /api/hse/managers/ - Créer un manager
    - GET /api/hse/managers/{id}/ - Détails d'un manager
    - PUT /api/hse/managers/{id}/ - Modifier un manager
    - DELETE /api/hse/managers/{id}/ - Supprimer un manager
    """
    
    queryset = HSEManager.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HSEManagerDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return HSEManagerCreateUpdateSerializer
        return HSEManagerListSerializer
