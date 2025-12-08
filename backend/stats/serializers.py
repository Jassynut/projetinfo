# serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import TestUserManager

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    code_acces = serializers.CharField()
    
    def validate(self, data):
        username = data.get('username')
        code_acces = data.get('code_acces')
        
        if username and code_acces:
            try:
                user = TestUserManager.objects.get(username=username, is_active=True)
                if user.authenticate(code_acces):
                    data['user'] = user
                else:
                    raise serializers.ValidationError("Code d'accès incorrect")
            except TestUserManager.DoesNotExist:
                raise serializers.ValidationError("Nom d'utilisateur incorrect")
        else:
            raise serializers.ValidationError("Must include username and code_acces")
        
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestUserManager
        fields = ('id', 'username', 'poste')
