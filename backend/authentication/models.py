# authentication/models.py
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from django.core.validators import MinLengthValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, username, code_acces):
        """
        Crée et enregistre un utilisateur avec le username et code d'accès
        """
        if not username:
            raise ValueError('Le nom d\'utilisateur est obligatoire')
        if not code_acces:
            raise ValueError('Le code d\'accès est obligatoire')
        
        # Normaliser le username
        username = self.normalize_email(username) if '@' in username else username.lower()
        
        user = self.model(
            username=username,
            code_acces=code_acces,
            
        )
        
        # Pas de mot de passe traditionnel - on utilise le code d'accès
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, username, code_acces, **extra_fields):
        """
        Crée et enregistre un superutilisateur
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')
        
        return self.create_user(username, code_acces, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    DEPARTEMENT_CHOICES = [
        ('manager_hse', 'Manager HSE'),
        ('superviseur', 'Superviseur HSE'),
        ('agent', 'Agent HSE'),
        ('direction', 'Direction'),
        ('contractant', 'Contractant'),
    ]
    
    # === CHAMPS D'AUTHENTIFICATION ===
    username = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Nom d'utilisateur",
        help_text="ex: hse.manager, ahmed.alaoui"
    )
    code_acces = models.CharField(
        max_length=20, 
        verbose_name="Code d'accès",
        validators=[MinLengthValidator(4)],
        help_text="Code personnel à 4 caractères minimum"
    )
    
    poste = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Poste occupé"
    )
    
    # === STATUT ET PERMISSIONS ===
    is_active = models.BooleanField(
        default=True,
        verbose_name="Compte actif"
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Accès administration"
    )
    is_superuser = models.BooleanField(
        default=False,
        verbose_name="Superutilisateur"
    )
    
    # === DATES ===
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name="Date d'inscription"
    )
    last_login = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Dernière connexion"
    )
    last_code_change = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Dernier changement de code"
    )
    
    # === CONFIGURATION ===
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['code_acces']
    
    class Meta:
        verbose_name = "Utilisateur HSE"
        verbose_name_plural = "Utilisateurs HSE"
    
    def __str__(self):
        return self.username
    
    
    def authenticate(self, code_acces_saisi):
        """Authentifie l'utilisateur avec le code d'accès"""
        return self.code_acces == code_acces_saisi and self.is_active
    
    def change_access_code(self, new_code):
        """Change le code d'accès"""
        if len(new_code) < 4:
            raise ValueError("Le code doit contenir au moins 4 caractères")
        self.code_acces = new_code
        self.last_code_change = timezone.now()
        self.save()
    
    @property
    def is_manager(self):
        """Vérifie si l'utilisateur est un manager HSE"""
        return self.departement == 'manager_hse'
    
    @property
    def is_direction(self):
        """Vérifie si l'utilisateur est de la direction"""
        return self.departement == 'direction'

class LoginSession(models.Model):
    """Historique des connexions"""
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='login_sessions',
        verbose_name="Utilisateur"
    )
    login_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Heure de connexion"
    )
    ip_address = models.GenericIPAddressField(
        null=True, 
        blank=True,
        verbose_name="Adresse IP"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="Navigateur utilisé"
    )
    success = models.BooleanField(
        default=False,
        verbose_name="Connexion réussie"
    )
    failure_reason = models.CharField(
        max_length=100, 
        blank=True,
        verbose_name="Raison de l'échec"
    )
    
    class Meta:
        verbose_name = "Session de connexion"
        verbose_name_plural = "Sessions de connexion"
        ordering = ['-login_time']
    
    def __str__(self):
        status = "✅ Réussie" if self.success else "❌ Échouée"
        return f"{self.user.username} - {self.login_time.strftime('%d/%m/%Y %H:%M')} - {status}"

class AccessCodeHistory(models.Model):
    """Historique des changements de code d'accès"""
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='code_history'
    )
    old_code = models.CharField(max_length=20)
    new_code = models.CharField(max_length=20)
    changed_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='code_changes_made'
    )
    
    class Meta:
        verbose_name = "Historique des codes"
        verbose_name_plural = "Historiques des codes"
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.changed_at.strftime('%d/%m/%Y %H:%M')}"