from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# =========================
# UTILISATEUR QUI PASSE LE TEST
# =========================

class TestUserManager(BaseUserManager):
    """Manager pour les utilisateurs Test (Auth par CIN)"""
    
    def create_user(self, cin, full_name=None):
        if not cin:
            raise ValueError("Le CIN est requis")
        user = self.model(cin=cin, full_name=full_name, email=email, **extra_fields)
        user.set_unusable_password()  # Auth uniquement via CIN
        user.save(using=self._db)
        return user

    def create_superuser(self, cin, full_name=None, email=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(cin, full_name, email, **extra_fields)

class TestUser(AbstractBaseUser, PermissionsMixin):
    """Utilisateur qui passe le test - Auth par CIN uniquement"""
    cin = models.CharField(max_length=20, unique=True, primary_key=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'cin'  # Auth uniquement via CIN
    REQUIRED_FIELDS = []

    objects = TestUserManager()

    def __str__(self):
        return f"{self.full_name} - {self.cin}"

