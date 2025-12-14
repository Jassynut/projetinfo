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
    HSEManagerListSerializer, HSEManagerDetailSerializer,
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
    permission_classes = [permissions.AllowAny]  # Permettre l'accès en lecture sans auth
    pagination_class = PageNumberPagination
    
    def get_permissions(self):
        """
        Permettre la lecture sans auth, mais exiger l'auth pour les modifications
        """
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return HSEUserDetailSerializer
        elif self.action == 'update_presence':
            return HSEUserCreateUpdateSerializer
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
        
        return queryset.order_by('nom', 'prénom')
    
    @action(detail=True, methods=['patch'])
    def update_presence(self, request, pk=None):
        """Mettre à jour la présence d'un utilisateur"""
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if 'presence' in serializer.validated_data:
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
        
        # Récupérer les tentatives par CIN
        from authentication.models import TestUser
        from tests.models import TestAttempt
        try:
            test_user = TestUser.objects.get(cin=user.cin)
            attempts = TestAttempt.objects.filter(user=test_user).order_by('-started_at')
            serializer = TestAttemptListSerializer(attempts, many=True)
            
            return Response({
                'success': True,
                'user_id': user.id,
                'attempts_count': attempts.count(),
                'attempts': serializer.data
            })
        except TestUser.DoesNotExist:
            return Response({
                'success': True,
                'user_id': user.id,
                'attempts_count': 0,
                'attempts': []
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
        
        return Response({
            'success': True,
            'statistics': {
                'total_users': total_users,
                'present_users': present_users,
                'present_percentage': round((present_users / total_users * 100) if total_users > 0 else 0, 1),
                'absent_users': total_users - present_users,
                'absent_percentage': round(((total_users - present_users) / total_users * 100) if total_users > 0 else 0, 1)
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


# =============================================================================
# FONCTION UNIFIÉE POUR PRÉVISUALISER EXCEL (remplace upload_excel)
# =============================================================================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def upload_excel(request):
    """
    Prévisualiser un fichier Excel (lecture uniquement, pas d'import)
    POST: /api/hse/upload_excel/
    Content-Type: multipart/form-data
    file: fichier Excel (.xlsx, .xls)
    
    Cette fonction trouve automatiquement la ligne d'en-tête contenant "Entité"
    et retourne les données du fichier.
    """
    if 'file' not in request.FILES:
        return Response({
            'success': False,
            'error': 'Aucun fichier fourni'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    excel_file = request.FILES['file']
    
    # Vérifier l'extension
    if not excel_file.name.endswith(('.xlsx', '.xls')):
        return Response({
            'success': False,
            'error': 'Le fichier doit être au format Excel (.xlsx ou .xls)'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        import pandas as pd
        
        # Lire sans header pour trouver la ligne d'en-tête
        df_raw = pd.read_excel(excel_file, header=None)
        
        # Trouver la ligne contenant "Entité" (l'en-tête réelle)
        header_row = None
        for i, row in df_raw.iterrows():
            if row.astype(str).str.contains("Entité", case=False, na=False).any():
                header_row = i
                break
        
        if header_row is None:
            return Response({
                'success': False,
                'error': 'Impossible de trouver l\'en-tête "Entité" dans ce fichier.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Recharger le fichier en utilisant la ligne trouvée comme header
        excel_file.seek(0)  # Réinitialiser le pointeur du fichier
        df = pd.read_excel(excel_file, header=header_row)
        
        # Supprimer colonnes 'Unnamed'
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # Supprimer lignes vides
        df = df.dropna(how="all")
        
        # Reset index
        df = df.reset_index(drop=True)
        
        # Convertir en liste de dictionnaires
        data_list = df.to_dict('records')
        
        return Response({
            'success': True,
            'data': data_list,
            'columns': list(df.columns),
            'row_count': len(df)
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': f'Erreur lors de la lecture du fichier : {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
