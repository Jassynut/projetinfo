from django.db import models
from django.conf import settings
from tests.models import TestAttempt
import uuid
from datetime import datetime, timedelta

class Certificate(models.Model):
    """Certificat généré après la réussite d'un test"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Lien vers la tentative de test
    test_attempt = models.OneToOneField(
        TestAttempt,
        on_delete=models.CASCADE,
        related_name='certificate',
        verbose_name="Tentative de test"
    )
    
    # Données du certificat
    certificate_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Numéro du certificat"
    )
    
    user_full_name = models.CharField(
        max_length=255,
        verbose_name="Nom complet (au moment du certificat)"
    )
    
    user_cin = models.CharField(
        max_length=20,
        verbose_name="CIN (au moment du certificat)"
    )
    
    test_version = models.IntegerField(
        verbose_name="Version du test réussi"
    )
    
    score = models.IntegerField(
        verbose_name="Score obtenu (/21)"
    )
    
    issued_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'émission"
    )
    
    expiry_date = models.DateField(
        verbose_name="Date d'expiration",
        help_text="Généralement 1 an après l'émission"
    )
    
    # Fichier PDF stocké
    pdf_file = models.FileField(
        upload_to='certificates/',
        null=True,
        blank=True,
        verbose_name="Fichier PDF du certificat"
    )
    
    class Meta:
        verbose_name = "Certificat"
        verbose_name_plural = "Certificats"
        ordering = ['-issued_date']
        indexes = [
            models.Index(fields=['user_cin']),
            models.Index(fields=['test_attempt']),
            models.Index(fields=['issued_date']),
        ]
    
    def __str__(self):
        return f"Cert #{self.certificate_number} - {self.user_full_name}"
    
    @property
    def is_expired(self):
        """Vérifier si le certificat est expiré"""
        return self.expiry_date < datetime.now().date()
    
    @property
    def days_until_expiry(self):
        """Jours avant expiration"""
        delta = self.expiry_date - datetime.now().date()
        return max(0, delta.days)
