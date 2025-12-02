from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
import re


class TestUserManager(BaseUserManager):
    """Manager pour TestUser avec username basé sur full_name."""

    def create_user(self, cin, username=None, full_name=None):
        if not cin:
            raise ValueError("Le cin est requis")
        
        # Générer le username si non fourni
        if not username:
            if full_name:
                username = self.generate_username_from_full_name(full_name)
            else:
                username = f"user_{cin}"
        
        user = self.model(
            cin=cin,
            username=username,
            full_name=full_name or username
        )
        
        # Utiliser le cin comme mot de passe
        user.set_password(cin)
        user.save(using=self._db)
        return user
    
    def generate_username_from_full_name(self, full_name):
        """Générer un username unique à partir du full_name."""
        if not full_name:
            return f"user_{uuid.uuid4().hex[:8]}"
        
        # Nettoyer le nom
        username = full_name.strip().lower()
        
        # Remplacer les caractères spéciaux et espaces
        username = re.sub(r'[^\w\s-]', '', username)
        username = re.sub(r'[-\s]+', '_', username)
        username = username.strip('_')
        
        # Limiter la longueur
        if len(username) > 150:
            username = username[:150]
        
        # Si vide après nettoyage
        if not username:
            username = f"user_{uuid.uuid4().hex[:8]}"
        
        # Vérifier l'unicité
        base_username = username
        counter = 1
        while self.model.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        
        return username

    def create_superuser(self, cin, username=None, full_name=None):
        if not username:
            username = f"admin_{cin}"
        
        user = self.create_user(
            cin=cin,
            username=username,
            full_name=full_name or username
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    
    def get_or_create_by_cin(self, cin):
        """
        Récupérer ou créer un utilisateur par cin.
        Utilisé pour l'authentification QR.
        """
        try:
            return self.get(cin=cin), False
        except self.model.DoesNotExist:
            # Essayer de récupérer les infos depuis hse_app si disponible
            full_name = None
            try:
                from hse_app.models import HSEmanager
                HSEmanager = HSEmanager.objects.get(cin=cin)
                full_name = HSEmanager.full_name
            except (ImportError, HSEmanager.DoesNotExist):
                pass
            
            user = self.create_user(cin=cin, full_name=full_name)
            return user, True


class TestUser(AbstractBaseUser, PermissionsMixin):
    """
    Modèle utilisateur pour les tests.
    Authentication normale: username/mot de passe (cin)
    Authentication QR: cin seulement
    """
    
    # Champs principaux
    cin = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="cin",
        help_text="Numéro de carte d'identité nationale"
    )
    
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name="Nom d'utilisateur"
    )
    
    full_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Nom complet"
    )
    
    # Champs requis par Django
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects = TestUserManager()
    
    # IMPORTANT: USERNAME_FIELD pour l'admin Django
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["cin"]  # Pour la commande createsuperuser
    
    class Meta:
        verbose_name = "Utilisateur Test"
        verbose_name_plural = "Utilisateurs Test"
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        return self.full_name or self.username
    
    def get_short_name(self):
        return self.username