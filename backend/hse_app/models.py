from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from authentication.models import TestUserManager
from django.core.files import File
from io import BytesIO
from django.conf import settings
from django.utils.translation import gettext_lazy as _

# =============================================================================
# MODÈLES PRINCIPAUX HSE
# =============================================================================

class HSEUser(models.Model):
    """Utilisateur HSE (participant aux tests)"""
    
    # Informations personnelles
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prénom = models.CharField(max_length=100, verbose_name="Prénom")
    email = models.EmailField(verbose_name="Adresse email")
    cin = models.CharField(max_length=20, unique=True, verbose_name="CIN")    
    
    # Informations professionnelles
    entite = models.CharField(max_length=100, verbose_name="Entité")
    entreprise = models.CharField(max_length=100, verbose_name="Entreprise")
    chef_projet_ocp = models.CharField(max_length=100, blank=True, verbose_name="Chef de projet OCP")
    
    # Statut et performance
    presence = models.BooleanField(default=False, verbose_name="Présent")
    reussite = models.BooleanField(default=False, verbose_name="Réussi(e)")
    score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(21)],
        verbose_name="Score global (/21)"
    )
    
    test_user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hse_user',
        verbose_name="Utilisateur d'authentification"
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Utilisateur HSE"
        verbose_name_plural = "Utilisateurs HSE"
        ordering = ['nom', 'prénom']
        indexes = [
            models.Index(fields=['nom', 'prénom']),
            models.Index(fields=['entite']),
            models.Index(fields=['entreprise']),
            models.Index(fields=['cin']),  # Ajouter index pour recherche rapide par CIN
        ]
    
    def __str__(self):
        return f"{self.nom} {self.prénom} - {self.entreprise}"
    
    def get_full_name(self):
        return f"{self.prénom} {self.nom}"

    @property
    def full_name(self):
        """Compatibilité avec le modèle TestUser"""
        return self.get_full_name()

    @property
    def taux_reussite(self):
        """Taux de réussite global de l'utilisateur"""
        attempts = self.testattempt_set.filter(completed_at__isnull=False)
        if not attempts:
            return 0
        reussis = attempts.filter(passed=True).count()
        return round((reussis / attempts.count()) * 100, 1)

class HSEManager(models.Model):
    """Manager pour les opérations HSE spécifiques"""
    name = models.CharField(max_length=100, verbose_name="Nom du manager")
    cin = models.CharField(max_length=50, unique=True, verbose_name="CIN")    
    class Meta:
        verbose_name = "Manager HSE"
        verbose_name_plural = "Managers HSE"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.cin})"
