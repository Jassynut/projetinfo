from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from backend.authentication.models import CustomUser

# =============================================================================
# MODÈLES PRINCIPAUX HSE
# =============================================================================

class HSEUser(models.Model):
    """Utilisateur HSE (participant aux tests)"""
    
    # Informations personnelles
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prénom = models.CharField(max_length=100, verbose_name="Prénom")
    email = models.EmailField(verbose_name="Adresse email")
    CIN = models.CharField(max_length=20, unique=True, verbose_name="CIN")
    téléphone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    
    # Informations professionnelles
    entite = models.CharField(max_length=100, verbose_name="Entité")
    entreprise = models.CharField(max_length=100, verbose_name="Entreprise")
    position = models.CharField(max_length=100, verbose_name="Poste/Fonction")
    chef_projet_ocp = models.CharField(max_length=100, blank=True, verbose_name="Chef de projet OCP")
    
    # Statut et performance
    presence = models.BooleanField(default=False, verbose_name="Présent")
    score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Score global (%)"
    )
    
    
    # Métadonnées
    est_actif = models.BooleanField(default=True, verbose_name="Actif")
    notes = models.TextField(blank=True, verbose_name="Notes supplémentaires")
    
    class Meta:
        verbose_name = "Utilisateur HSE"
        verbose_name_plural = "Utilisateurs HSE"
        ordering = ['nom', 'prénom']
        indexes = [
            models.Index(fields=['nom', 'prénom']),
            models.Index(fields=['entite']),
            models.Index(fields=['entreprise']),
        ]
    
    def __str__(self):
        return f"{self.nom} {self.prénom} - {self.entreprise}"
    
    def get_full_name(self):
        return f"{self.prénom} {self.nom}"
    
    @property
    def tests_completes(self):
        """Nombre de tests complétés par cet utilisateur"""
        return self.testattempt_set.filter(completed_at__isnull=False).count()
    
    @property
    def taux_reussite(self):
        """Taux de réussite global de l'utilisateur"""
        attempts = self.testattempt_set.filter(completed_at__isnull=False)
        if not attempts:
            return 0
        reussis = attempts.filter(passed=True).count()
        return round((reussis / attempts.count()) * 100, 1)


class HSETest(models.Model):
    """Test HSE avec questions et paramètres"""
    
    # Informations de base
    title = models.CharField(max_length=200, verbose_name="Titre du test")
    description = models.TextField(verbose_name="Description")
    
    # Paramètres du test
    duration_minutes = models.IntegerField(
        default=30,
        validators=[MinValueValidator(5), MaxValueValidator(180)],
        verbose_name="Durée (minutes)"
    )
    passing_score = models.IntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Score de passage (%)"
    )
    
    
    # Statut et visibilité
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    
    class Meta:
        verbose_name = "Test HSE"
        verbose_name_plural = "Tests HSE"
        ordering = ['ordre_affichage', 'title']
        indexes = [
            models.Index(fields=['categorie']),
            models.Index(fields=['niveau_difficulte']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_categorie_display()})"
    
    @property
    def questions_count(self):
        """Nombre de questions dans ce test"""
        return self.questions.count()
    
    @property
    def taux_reussite_global(self):
        """Taux de réussite global pour ce test"""
        attempts = self.testattempt_set.filter(completed_at__isnull=False)
        if not attempts:
            return 0
        reussis = attempts.filter(passed=True).count()
        return round((reussis / attempts.count()) * 100, 1)
    
    @property
    def score_moyen(self):
        """Score moyen des participants"""
        from django.db.models import Avg
        result = self.testattempt_set.filter(
            completed_at__isnull=False
        ).aggregate(avg_score=Avg('score'))
        return round(result['avg_score'] or 0, 1)


class TestSession(models.Model):
    """Session de test avec QR Code"""
    STATUT_SESSION = [
        ('planifiee', 'Planifiée'),
        ('en_cours', 'En cours'),
        ('terminee', 'Terminée'),
        ('annulee', 'Annulée'),
    ]
    
    # Identification
    session_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Code de session"
    )
    
    # QR Code
    qr_code = models.ImageField(
        upload_to='qr_codes/',
        blank=True,
        null=True,
        verbose_name="QR Code"
    )
    qr_code_data = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="Données du QR Code"
    )
    
    # Paramètres temporels
    start_time = models.DateTimeField(
        default=timezone.now,
        verbose_name="Heure de début"
    )
    end_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Heure de fin"
    )
    
    # Relations
    test_id = models.ForeignKey(
        HSETest,
        on_delete=models.CASCADE,
        verbose_name="Test associé"
    )
    

    
    
    class Meta:
        verbose_name = "Session de test"
        verbose_name_plural = "Sessions de test"
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['session_code']),
            models.Index(fields=['start_time']),
            models.Index(fields=['statut']),
        ]
    
    def __str__(self):
        return f"Session {self.session_code} - {self.test.title}"
    
    def save(self, *args, **kwargs):
        """Génère un code de session unique si non fourni"""
        if not self.session_code:
            self.session_code = f"SES-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def duree_reelle(self):
        """Calcule la durée réelle de la session"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    @property
    def participants_actuels(self):
        """Nombre de participants ayant commencé le test"""
        return self.testattempt_set.count()
    
    @property
    def est_en_cours(self):
        """Vérifie si la session est en cours"""
        return self.statut == 'en_cours'


class TestQuestion(models.Model):
    """Question d'un test HSE"""
    TYPE_QUESTION = [
        ('multiple_choice', 'Choix multiple'),
        ('single_choice', 'Choix unique'),
        ('true_false', 'Vrai/Faux'),
        ('short_answer', 'Réponse courte'),
        ('matching', 'Appariement'),
    ]
    
    # Contenu de la question
    test = models.ForeignKey(
        HSETest,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Test"
    )
    question_text = models.TextField(verbose_name="Question")
    question_type = models.CharField(
        max_length=20,
        choices=TYPE_QUESTION,
        default='multiple_choice',
        verbose_name="Type de question"
    )
    # Métadonnées
    image_question = models.ImageField(
        upload_to='questions/',
        blank=True,
        null=True,
        verbose_name="Image illustrative"
    )
    
    tags = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Tags"
    )
    
    class Meta:
        verbose_name = "Question de test"
        verbose_name_plural = "Questions de test"
        ordering = ['test', 'ordre']
        unique_together = ['test', 'ordre']
    
    def __str__(self):
        return f"Q{self.ordre}: {self.question_text[:50]}..."


class QuestionOption(models.Model):
    """Option de réponse pour une question"""
    question = models.ForeignKey(
        TestQuestion,
        on_delete=models.CASCADE,
        related_name='options',
        verbose_name="Question"
    )
    option_text = models.CharField(max_length=500, verbose_name="Option")
    is_correct = models.BooleanField(default=False, verbose_name="Correcte")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    
    # Pour les questions d'appariement
    option_groupe = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Groupe d'option"
    )
    
    class Meta:
        verbose_name = "Option de question"
        verbose_name_plural = "Options de question"
        ordering = ['question', 'ordre']
    
    def __str__(self):
        statut = "✓" if self.is_correct else "✗"
        return f"{statut} {self.option_text[:30]}..."


class TestAttempt(models.Model):
    """Tentative de test par un utilisateur"""
    STATUT_TENTATIVE = [
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('abandonne', 'Abandonné'),
        ('expire', 'Expiré'),
    ]
    
    # Relations
    user = models.ForeignKey(
        HSEUser,
        on_delete=models.CASCADE,
        verbose_name="Utilisateur"
    )
    session = models.ForeignKey(
        TestSession,
        on_delete=models.CASCADE,
        verbose_name="Session"
    )
    
    # Performance
    score = models.FloatField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Score (%)"
    )
    points_obtenus = models.IntegerField(default=0, verbose_name="Points obtenus")
    points_max = models.IntegerField(default=0, verbose_name="Points maximum")
    
    # Statut
    passed = models.BooleanField(default=False, verbose_name="Réussi")
    statut = models.CharField(
        max_length=20,
        choices=STATUT_TENTATIVE,
        default='en_cours',
        verbose_name="Statut"
    )
    
    # Temps
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Débuté à")
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Terminé à"
    )
    temps_passe = models.DurationField(
        blank=True,
        null=True,
        verbose_name="Temps passé"
    )
    
    # Certificat
    certificate_generated = models.BooleanField(
        default=False,
        verbose_name="Certificat généré"
    )
    certificate_file = models.FileField(
        upload_to='certificats/',
        blank=True,
        null=True,
        verbose_name="Fichier du certificat"
    )
    numero_certificat = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Numéro de certificat"
    )
    
    # Métadonnées
    ip_address = models.GenericIPAddressField(
        blank=True,
        null=True,
        verbose_name="Adresse IP"
    )
    user_agent = models.TextField(blank=True, verbose_name="Navigateur")
    
    class Meta:
        verbose_name = "Tentative de test"
        verbose_name_plural = "Tentatives de test"
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'session']),
            models.Index(fields=['started_at']),
            models.Index(fields=['passed']),
        ]
    
    def __str__(self):
        return f"Tentative {self.id} - {self.user} - {self.session.test.title}"
    
    def calculer_score(self):
        """Calcule le score basé sur les réponses"""
        reponses = self.answers.filter(is_correct=True)
        total_points = sum(reponse.question.points for reponse in reponses)
        points_max = sum(question.points for question in self.session.test.questions.all())
        
        if points_max > 0:
            self.points_obtenus = total_points
            self.points_max = points_max
            self.score = (total_points / points_max) * 100
            self.passed = self.score >= self.session.test.passing_score
    
    @property
    def duree_totale(self):
        """Calcule la durée totale de la tentative"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None
    
    @property
    def pourcentage_reussite(self):
        """Pourcentage de réponses correctes"""
        total_reponses = self.answers.count()
        if total_reponses == 0:
            return 0
        reponses_correctes = self.answers.filter(is_correct=True).count()
        return round((reponses_correctes / total_reponses) * 100, 1)


class Answer(models.Model):
    """Réponse d'un utilisateur à une question"""
    test_attempt = models.ForeignKey(
        TestAttempt,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Tentative de test"
    )
    question = models.ForeignKey(
        TestQuestion,
        on_delete=models.CASCADE,
        verbose_name="Question"
    )
    
    # Réponse
    answer_text = models.TextField(
        blank=True,
        null=True,
        verbose_name="Réponse texte"
    )
    selected_options = models.ManyToManyField(
        QuestionOption,
        blank=True,
        verbose_name="Options sélectionnées"
    )
    
    # Évaluation
    is_correct = models.BooleanField(default=False, verbose_name="Correcte")
    points_obtenus = models.IntegerField(default=0, verbose_name="Points obtenus")
    
    # Temps
    temps_reponse = models.DurationField(
        blank=True,
        null=True,
        verbose_name="Temps de réponse"
    )
    
    class Meta:
        verbose_name = "Réponse"
        verbose_name_plural = "Réponses"
        ordering = ['test_attempt']
        unique_together = ['test_attempt', 'question']
    
    def __str__(self):
        return f"Réponse {self.id} - {self.question.question_text[:30]}..."
    
    def evaluer_reponse(self):
        """Évalue si la réponse est correcte"""
        if self.question.question_type in ['multiple_choice', 'single_choice']:
            reponses_correctes = set(self.question.options.filter(is_correct=True))
            reponses_utilisateur = set(self.selected_options.all())
            self.is_correct = reponses_correctes == reponses_utilisateur
        elif self.question.question_type == 'true_false':
            # Implémentation pour Vrai/Faux
            pass
        
        if self.is_correct:
            self.points_obtenus = self.question.points
        else:
            self.points_obtenus = 0


# =============================================================================
# MODÈLES DE SUPPORT
# =============================================================================

class TestCategory(models.Model):
    """Catégories de tests HSE"""
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    couleur = models.CharField(max_length=7, default='#007bff', verbose_name="Couleur")
    icone = models.CharField(max_length=50, blank=True, verbose_name="Icône")
    ordre = models.IntegerField(default=0, verbose_name="Ordre")
    
    class Meta:
        verbose_name = "Catégorie de test"
        verbose_name_plural = "Catégories de test"
        ordering = ['ordre', 'nom']
    
    def __str__(self):
        return self.nom


class TestTag(models.Model):
    """Tags pour organiser les tests"""
    nom = models.CharField(max_length=50, unique=True, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    
    class Meta:
        verbose_name = "Tag de test"
        verbose_name_plural = "Tags de test"
    
    def __str__(self):
        return self.nom


class UserProgress(models.Model):
    """Suivi de progression des utilisateurs"""
    user = models.ForeignKey(
        HSEUser,
        on_delete=models.CASCADE,
        verbose_name="Utilisateur"
    )
    test = models.ForeignKey(
        HSETest,
        on_delete=models.CASCADE,
        verbose_name="Test"
    )
    dernier_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Dernier score"
    )
    meilleur_score = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Meilleur score"
    )
    tentatives = models.IntegerField(default=0, verbose_name="Nombre de tentatives")
    termine = models.BooleanField(default=False, verbose_name="Terminé")
    date_derniere_tentative = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière tentative"
    )
    
    class Meta:
        verbose_name = "Progression utilisateur"
        verbose_name_plural = "Progressions utilisateur"
        unique_together = ['user', 'test']
    
    def __str__(self):
        return f"Progression {self.user} - {self.test}"