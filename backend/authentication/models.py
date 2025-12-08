from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
import re


class TestUserManager(BaseUserManager):
    """Manager pour TestUser avec deux types d'authentification."""

    def create_user(self, cin, username=None, full_name=None, user_type='user', password=None):
        if not cin:
            raise ValueError("Le CIN est requis")

        if not username:
            if user_type == 'manager' and full_name:
                username = self.generate_username_from_full_name(full_name)
            else:
                username = f"user_{cin}"

        user = self.model(
            cin=cin,
            username=username,
            full_name=full_name or username,
            user_type=user_type
        )

        # Mot de passe = CIN
        user.set_password(password or cin)
        user.save(using=self._db)
        return user

    def create_manager(self, cin, full_name):
        """Créer un manager HSE (auth: full_name + CIN)."""
        if not full_name:
            raise ValueError("Le nom complet est requis pour un manager")

        username = self.generate_username_from_full_name(full_name)
        return self.create_user(
            cin=cin,
            username=username,
            full_name=full_name,
            user_type='manager',
            password=cin  # CIN comme mot de passe
        )

    def create_hse_user(self, cin, full_name=None):
        """Créer un utilisateur HSE (auth: CIN uniquement)."""
        return self.create_user(
            cin=cin,
            full_name=full_name,
            user_type='user'
        )

    def generate_username_from_full_name(self, full_name):
        """Générer un username unique à partir du full_name."""
        if not full_name:
            return f"user_{uuid.uuid4().hex[:8]}"

        username = full_name.strip().lower()
        username = re.sub(r'[^\w\s-]', '', username)
        username = re.sub(r'[-\s]+', '_', username)
        username = username.strip('_')

        if len(username) > 150:
            username = username[:150]

        if not username:
            username = f"user_{uuid.uuid4().hex[:8]}"

        base_username = username
        counter = 1
        while self.model.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        return username

    def create_superuser(self, cin, username=None, full_name=None, password=None):
        if not username:
            username = f"admin_{cin}"

        user = self.create_user(
            cin=cin,
            username=username,
            full_name=full_name or username,
            user_type='manager',
            password=password or cin
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    # ==========================================
    # AUTHENTIFICATION HSE USER (CIN uniquement)
    # ==========================================
    def authenticate_hse_user(self, cin):
        """
        Authentification pour les utilisateurs qui passent le test.
        UN SEUL CHAMP: le CIN (après scan QR).
        """
        try:
            return self.get(cin=cin, user_type='user'), False
        except self.model.DoesNotExist:
            # Auto-créer depuis la table HSEUser si existe
            full_name = None
            try:
                from hse_app.models import HSEUser as HSEUserModel
                hse_user = HSEUserModel.objects.get(cin=cin)
                full_name = hse_user.full_name
            except (ImportError, Exception):
                pass
            user = self.create_hse_user(cin=cin, full_name=full_name)
            return user, True

    # ==========================================
    # AUTHENTIFICATION MANAGER (full_name + CIN)
    # ==========================================
    def authenticate_manager(self, full_name, cin):
        """
        Authentification pour les managers HSE.
        - Username: full_name (depuis la table HSEManager)
        - Mot de passe: CIN
        """
        # Chercher par full_name (insensible à la casse)
        try:
            user = self.get(
                full_name__iexact=full_name.strip(),
                user_type='manager'
            )
            # Vérifier le mot de passe (CIN)
            if user.check_password(cin):
                return user
            return None
        except self.model.DoesNotExist:
            # Auto-créer depuis la table HSEManager si existe
            try:
                from hse_app.models import HSEManager as HSEManagerModel
                manager = HSEManagerModel.objects.get(
                    full_name__iexact=full_name.strip(),
                    cin=cin
                )
                return self.create_manager(cin=cin, full_name=manager.full_name)
            except (ImportError, Exception):
                return None


class TestUser(AbstractBaseUser, PermissionsMixin):
    """
    Modèle utilisateur unifié.
    
    HSE Users (passent le test):
        - Authentification: CIN uniquement (1 seul champ)
        
    HSE Managers:
        - Authentification: full_name (username) + CIN (mot de passe)
    """

    USER_TYPE_CHOICES = [
        ('user', 'Utilisateur HSE'),
        ('manager', 'Manager HSE'),
    ]

    cin = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="CIN"
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
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='user',
        verbose_name="Type d'utilisateur"
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = TestUserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["cin"]

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return f"{self.full_name or self.username} ({self.get_user_type_display()})"

    def get_full_name(self):
        return self.full_name or self.username

    def get_short_name(self):
        return self.username

    @property
    def is_manager(self):
        return self.user_type == 'manager'

    @property
    def is_hse_user(self):
        return self.user_type == 'user'
