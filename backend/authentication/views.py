# authentication/views.py
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.utils import timezone
from .models import TestUserManager, LoginSession
from .serializers import LoginSerializer, UserSerializer, ChangeAccessCodeSerializer, CreateUserSerializer

def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    Authentification de l'utilisateur avec username et code d'accès
    """
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Logger la connexion réussie
        LoginSession.objects.create(
            user=user,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=True
        )
        
        # Mettre à jour last_login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Connecter l'utilisateur
        login(request, user)
        
        return Response({
            'message': 'Connexion réussie',
            'user': UserSerializer(user).data
        }, status=status.HTTP_200_OK)
    
    # Logger l'échec de connexion
    username = request.data.get('username', '')
    if username:
        try:
            user = TestUserManager.objects.get(username=username)
        except TestUserManager.DoesNotExist:
            user = None
        
        LoginSession.objects.create(
            user=user,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=False,
            failure_reason=serializer.errors.get('error', 'Erreur inconnue')
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Déconnexion de l'utilisateur
    """
    logout(request)
    return Response({
        'message': 'Déconnexion réussie'
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    """
    Récupère les informations de l'utilisateur connecté
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_access_code(request):
    """
    Changement du code d'accès
    """
    serializer = ChangeAccessCodeSerializer(
        data=request.data, 
        context={'request': request}
    )
    
    if serializer.is_valid():
        user = request.user
        new_code = serializer.validated_data['new_code']
        
        try:
            user.change_access_code(new_code)
            return Response({
                'message': 'Code d\'accès modifié avec succès'
            })
        except ValueError as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def login_history(request):
    """
    Historique des connexions de l'utilisateur
    """
    sessions = LoginSession.objects.filter(user=request.user).order_by('-login_time')[:50]
    
    history_data = []
    for session in sessions:
        history_data.append({
            'login_time': session.login_time,
            'ip_address': session.ip_address,
            'success': session.success,
            'failure_reason': session.failure_reason if not session.success else None
        })
    
    return Response(history_data)

# Vues d'administration (réservées aux staff)
@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def admin_create_user(request):
    """
    Création d'un utilisateur par l'administrateur
    """
    serializer = CreateUserSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            UserSerializer(user).data, 
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def admin_users_list(request):
    """
    Liste tous les utilisateurs (admin seulement)
    """
    users = TestUserManager.objects.all().order_by('username')
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)