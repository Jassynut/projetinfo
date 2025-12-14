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
# FONCTIONS HELPER
# =============================================================================

def get_today_date():
    """Retourne la date du jour pour le champ date_ajout"""
    return timezone.now().date()

# =============================================================================
# MODÈLES PRINCIPAUX HSE
# =============================================================================

class HSEUser(models.Model):
    """Utilisateur HSE (participant aux tests)"""
    
    # Informations personnelles
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prénom = models.CharField(max_length=100, verbose_name="Prénom")
    cin = models.CharField(max_length=20, unique=True, verbose_name="CIN")    
    
    # Informations professionnelles
    entite = models.CharField(max_length=100, verbose_name="Entité")
    entreprise = models.CharField(max_length=100, verbose_name="Entreprise")
    chef_projet_ocp = models.CharField(max_length=100, blank=True, verbose_name="Chef de projet OCP")
    
    # Statut
    presence = models.BooleanField(default=False, verbose_name="Présence")
    sensibilise_avec_succes = models.BooleanField(default=False, verbose_name="Sensibilisé avec succès")
    
    # Date d'ajout
    date_ajout = models.DateField(default=get_today_date, verbose_name="Date d'ajout")
    
    class Meta:
        verbose_name = "Utilisateur HSE"
        verbose_name_plural = "Utilisateurs HSE"
        ordering = ['nom', 'prénom']
        indexes = [
            models.Index(fields=['nom', 'prénom']),
            models.Index(fields=['entite']),
            models.Index(fields=['entreprise']),
            models.Index(fields=['cin']),  # Ajouter index pour recherche rapide par CIN
            models.Index(fields=['date_ajout']),  # Index pour filtrage par date
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
    full_name = models.CharField(max_length=100, verbose_name="Nom complet")
    cin = models.CharField(max_length=50, unique=True, verbose_name="CIN")    
    
    class Meta:
        verbose_name = "Manager HSE"
        verbose_name_plural = "Managers HSE"
        ordering = ['full_name']
    
    def __str__(self):
        return f"{self.full_name} ({self.cin})"
