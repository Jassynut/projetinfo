# authentication/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate as django_authenticate
from .models import TestUserManager, LoginSession

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=50,
        required=True,
        trim_whitespace=True,
        label="Nom d'utilisateur"
    )
    code_acces = serializers.CharField(
        max_length=20,
        required=True,
        write_only=True,
        trim_whitespace=True,
        label="Code d'accès",
        help_text="Votre code d'accès personnel"
    )

    def validate(self, data):
        username = data.get('username').strip().lower()
        code_acces = data.get('code_acces').strip()
        
        if not username or not code_acces:
            raise serializers.ValidationError({
                'error': 'Le nom d\'utilisateur et le code d\'accès sont obligatoires'
            })
        
        try:
            user = TestUserManager.objects.get(username=username)
            
            if not user.is_active:
                raise serializers.ValidationError({
                    'error': 'Votre compte est désactivé. Contactez l\'administrateur.'
                })
            
            if not user.authenticate(code_acces):
                raise serializers.ValidationError({
                    'error': 'Code d\'accès incorrect'
                })
                
            data['user'] = user
            
        except TestUserManager.DoesNotExist:
            raise serializers.ValidationError({
                'error': 'Nom d\'utilisateur incorrect'
            })
        
        return data

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    departement_display = serializers.SerializerMethodField()
    site_display = serializers.SerializerMethodField()
    
    class Meta:
        model = TestUserManager
        fields = [
            'id',
            'username',
            'poste',
            'is_active',
            'is_staff',
            'date_joined',
            'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_departement_display(self, obj):
        return obj.get_departement_display()
    
    def get_site_display(self, obj):
        return obj.get_site_display()

class ChangeAccessCodeSerializer(serializers.Serializer):
    current_code = serializers.CharField(required=True, write_only=True)
    new_code = serializers.CharField(
        required=True, 
        write_only=True,
        min_length=4,
        max_length=20
    )
    confirm_new_code = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        current_code = data.get('current_code')
        new_code = data.get('new_code')
        confirm_new_code = data.get('confirm_new_code')
        
        user = self.context['request'].user
        
        # Vérifier le code actuel
        if not user.authenticate(current_code):
            raise serializers.ValidationError({
                'current_code': 'Le code actuel est incorrect'
            })
        
        # Vérifier la confirmation
        if new_code != confirm_new_code:
            raise serializers.ValidationError({
                'confirm_new_code': 'Les nouveaux codes ne correspondent pas'
            })
        
        # Vérifier que le nouveau code est différent
        if new_code == current_code:
            raise serializers.ValidationError({
                'new_code': 'Le nouveau code doit être différent de l\'ancien'
            })
        
        return data

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestUserManager
        fields = [
            'username', 
            'code_acces',
            'site', 
            'poste', 
            'is_staff',
            'is_active'
        ]
        extra_kwargs = {
            'code_acces': {'write_only': True}
        }
    
    def validate_username(self, value):
        if TestUserManager.objects.filter(username=value.lower()).exists():
            raise serializers.ValidationError("Ce nom d'utilisateur est déjà utilisé")
        return value.lower()