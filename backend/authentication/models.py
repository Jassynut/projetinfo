# authentication/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import MinLengthValidator
# ==================== TEST USER (AUTH PAR CIN) ====================

class TestUserManager(BaseUserManager):
    """Manager pour les utilisateurs Test (Auth par CIN)"""
    
    def create_user(self, cin, **extra_fields):
        if not cin:
            raise ValueError("Le CIN est requis")
        
        user = self.model(cin=cin, **extra_fields)
        user.set_unusable_password()  # Pas de mot de passe classique
        user.generate_qr_code()
        user.save(using=self._db)
        return user


class TestUser(AbstractBaseUser, PermissionsMixin):
    """Utilisateur pour passer les tests - Authentification uniquement par CIN"""
    
    cin = models.CharField(
        max_length=20,
        unique=True,
        primary_key=True,
        verbose_name="CIN"
    )

    full_name = models.CharField(max_length=200)
    department = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)

    qr_code = models.ImageField(upload_to='qrcodes/', blank=True)

    USERNAME_FIELD = 'cin'
    REQUIRED_FIELDS = []

    objects = TestUserManager()

    def __str__(self):
        return f"{self.full_name} - {self.cin}"
