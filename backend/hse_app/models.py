from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from backend.authentication.models import CustomUser
import qrcode
from django.core.files import File
from io import BytesIO
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
        verbose_name="Score global (%)"
    )
    
    
    # Métadonnées    
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
    def taux_reussite(self):
        """Taux de réussite global de l'utilisateur"""
        attempts = self.testattempt_set.filter(completed_at__isnull=False)
        if not attempts:
            return 0
        reussis = attempts.filter(passed=True).count()
        return round((reussis / attempts.count()) * 100, 1)

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class HSETest(models.Model):
    """Test HSE avec questions et paramètres"""
    
    # Version du test (1 à 6)
    VERSION_CHOICES = [
        (1, 'Version 1'),
        (2, 'Version 2'),
        (3, 'Version 3'),
        (4, 'Version 4'),
        (5, 'Version 5'),
        (6, 'Version 6'),
    ]
    
    version = models.IntegerField(
        choices=VERSION_CHOICES,
        verbose_name="Version du test",
        unique=True,
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    
    description = models.TextField(verbose_name="Description", blank=True)
    
    # Paramètres du test
    duration_minutes = models.IntegerField(
        default=10,
        verbose_name="Durée (minutes)",
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    
    # Nombre de questions
    total_questions = models.IntegerField(
        default=21,
        verbose_name="Nombre total de questions",
        validators=[MinValueValidator(1)]
    )
    
    # Questions obligatoires (9 questions)
    mandatory_questions_count = models.IntegerField(
        default=9,
        verbose_name="Nombre de questions obligatoires",
        validators=[MinValueValidator(1), MaxValueValidator(21)]
    )
    
    # Score de passage pour les questions optionnelles (si les obligatoires sont réussies)
    passing_score_optional = models.IntegerField(
        default=9,
        validators=[MinValueValidator(0), MaxValueValidator(21)],
        verbose_name="Score de passage questions optionnelles (%)",
        help_text="Score minimum pour les questions optionnelles si les obligatoires sont réussies"
    )
    
    # Ordre des questions pour cette version
    ordre_questions = models.JSONField(
        verbose_name="Ordre des questions",
        help_text="Liste des IDs de questions dans l'ordre spécifique à cette version"
    )
    
    # Questions obligatoires spécifiques à cette version
    mandatory_questions = models.JSONField(
        verbose_name="Questions obligatoires",
        default=list,
        help_text="Liste des IDs des questions obligatoires"
    )
    
    # Métadonnées
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Test HSE"
        verbose_name_plural = "Tests HSE"
        ordering = ['version']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['version']),
        ]
    
    def __str__(self):
        return f"Test HSE - Version {self.version}"
    
    @property
    def questions_count(self):
        """Nombre de questions dans ce test"""
        return len(self.ordre_questions) if self.ordre_questions else 0
    
    @property
    def optional_questions_count(self):
        """Nombre de questions optionnelles"""
        return self.total_questions - self.mandatory_questions_count
    
    def get_questions_in_order(self):
        """Récupère les questions dans l'ordre spécifié"""
        if not self.ordre_questions:
            return HSEQuestion.objects.none()
        
        # Crée un dictionnaire pour préserver l'ordre
        question_dict = {}
        questions = HSEQuestion.objects.filter(id__in=self.ordre_questions)
        
        for question in questions:
            question_dict[str(question.id)] = question
        
        # Retourne les questions dans l'ordre spécifié
        ordered_questions = []
        for qid in self.ordre_questions:
            if str(qid) in question_dict:
                ordered_questions.append(question_dict[str(qid)])
        
        return ordered_questions
    
    def get_mandatory_questions(self):
        """Récupère les questions obligatoires"""
        if not self.mandatory_questions:
            return HSEQuestion.objects.none()
        
        mandatory_questions_list = []
        for qid in self.mandatory_questions:
            try:
                question = HSEQuestion.objects.get(id=qid)
                mandatory_questions_list.append(question)
            except HSEQuestion.DoesNotExist:
                continue
        
        return mandatory_questions_list
    
    def get_optional_questions(self):
        """Récupère les questions optionnelles"""
        if not self.ordre_questions:
            return HSEQuestion.objects.none()
        
        mandatory_ids = set(self.mandatory_questions)
        optional_ids = [qid for qid in self.ordre_questions if qid not in mandatory_ids]
        
        optional_questions_list = []
        for qid in optional_ids:
            try:
                question = HSEQuestion.objects.get(id=qid)
                optional_questions_list.append(question)
            except HSEQuestion.DoesNotExist:
                continue
        
        return optional_questions_list


class HSEQuestion(models.Model):
    """Question individuelle pour les tests HSE (Vrai/Faux uniquement)"""

    # Identification
    question_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Code de la question",
        help_text="Ex: Q1, Q2, ..."
    )
    
    # Énoncé de la question en trois langues
    enonce_fr = models.TextField(verbose_name="Énoncé (Français)")
    enonce_en = models.TextField(verbose_name="Énoncé (Anglais)", blank=True)
    enonce_es = models.TextField(verbose_name="Énoncé (Arabe)", blank=True)
    
    # Réponse correcte (Vrai/Faux)
    reponse_correcte = models.BooleanField(
        verbose_name="Réponse correcte",
        help_text="Cochez si la réponse correcte est VRAI"
    )
    

    # Importance de la question
    is_mandatory = models.BooleanField(
        default=False,
        verbose_name="Question obligatoire",
        help_text="Question qui doit être obligatoirement réussie"
    )
    
    # Points
    points = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Points pour bonne réponse"
    )
    
    # Image optionnelle
    image = models.ImageField(
        upload_to='questions/hse/',
        verbose_name="Image d'illustration",
        blank=True,
        null=True,
        help_text="Image optionnelle pour illustrer la question"
    )
    
    # Métadonnées
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    class Meta:
        verbose_name = "Question HSE"
        verbose_name_plural = "Questions HSE"
        ordering = ['question_code']
        indexes = [
            models.Index(fields=['categorie']),
            models.Index(fields=['niveau_difficulte']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_mandatory']),
            models.Index(fields=['reponse_correcte']),
        ]
    
    def __str__(self):
        return f"{self.question_code}: {self.enonce_fr[:50]}..."
    
    def get_enonce(self, langue='fr'):
        """Retourne l'énoncé dans la langue spécifiée"""
        lang_map = {
            'fr': self.enonce_fr,
            'en': self.enonce_en or self.enonce_fr,
            'ar': self.enonce_ar or self.enonce_fr
        }
        return lang_map.get(langue, self.enonce_fr)

    def check_answer(self, user_answer):
        """Vérifie si la réponse de l'utilisateur est correcte"""
        if user_answer is None:
            return False
            
        # Convertir la réponse de l'utilisateur en booléen
        if isinstance(user_answer, str):
            user_answer = user_answer.lower().strip()
            if user_answer in ['vrai', 'true', 'verdadero', '1', 'yes', 'oui', 'v', 't']:
                user_bool = True
            elif user_answer in ['faux', 'false', 'falso', '0', 'no', 'non', 'f']:
                user_bool = False
            else:
                return False
        elif isinstance(user_answer, int):
            user_bool = bool(user_answer)
        else:
            user_bool = bool(user_answer)
        
        return user_bool == self.reponse_correcte
    
    @property
    def reponse_correcte_display(self):
        """Retourne la réponse correcte sous forme de texte"""
        return "Vrai" if self.reponse_correcte else "Faux"
    
    @property
    def has_image(self):
        """Vérifie si la question a une image"""
        return bool(self.image)


class TestAttempt(models.Model):
    """Tentative de test par un utilisateur"""
    
    STATUS_CHOICES = [
        ('in_progress', 'En cours'),
        ('passed', 'Réussi'),
        ('failed', 'Échoué'),
    ]
    
    test = models.ForeignKey(HSETest, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Utilisateur"
    )
    
    # Langue utilisée pour passer le test
    langue = models.CharField(
        max_length=2,
        choices=[
            ('ar', 'Arabe'),
            ('fr', 'Français'),
            ('en', 'Anglais'),
        ],
        default='ar',
        verbose_name="Langue du test"
    )
    
    # Statut de la tentative
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='in_progress',
        verbose_name="Statut"
    )
    
    # Résultats détaillés
    # Questions obligatoires
    mandatory_correct = models.IntegerField(
        default=0,
        verbose_name="Questions obligatoires correctes"
    )
    mandatory_wrong = models.IntegerField(
        default=0,
        verbose_name="Questions obligatoires incorrectes"
    )
    mandatory_total = models.IntegerField(
        default=9,
        verbose_name="Total questions obligatoires"
    )
    
    # Questions optionnelles
    optional_correct = models.IntegerField(
        default=0,
        verbose_name="Questions optionnelles correctes"
    )
    optional_wrong = models.IntegerField(
        default=0,
        verbose_name="Questions optionnelles incorrectes"
    )
    optional_total = models.IntegerField(
        default=12,
        verbose_name="Total questions optionnelles"
    )
    
    # Scores
    mandatory_score_percentage = models.FloatField(
        default=0,
        verbose_name="Score questions obligatoires"
    )
    optional_score_percentage = models.FloatField(
        default=0,
        verbose_name="Score questions optionnelles"
    )
    overall_score_percentage = models.FloatField(
        default=0,
        verbose_name="Score global"
    )
    

    passed = models.BooleanField(default=False, verbose_name="Test réussi")
    
    # Métadonnées de la tentative
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Débuté à")
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Terminé à"
    )
    time_taken_seconds = models.IntegerField(
        default=0,
        verbose_name="Temps pris (secondes)"
    )
    
    # Réponses de l'utilisateur
    user_answers = models.JSONField(
        verbose_name="Réponses de l'utilisateur",
        default=dict,
        help_text="Format: {question_id: {'answer': bool, 'is_mandatory': bool}}"
    )
    qr_code = models.ImageField(
        upload_to='attempt_qrcodes/',
        null=True,
        blank=True,
        verbose_name="QR Code de la session"
    )
    
    class Meta:
        verbose_name = "Tentative de test"
        verbose_name_plural = "Tentatives de test"
        ordering = ['-started_at']
        unique_together = ['user', 'test']
        indexes = [
            models.Index(fields=['user', 'test']),
            models.Index(fields=['completed_at']),
            models.Index(fields=['passed']),
            models.Index(fields=['status']),
            models.Index(fields=['langue']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - V{self.test.version} - {self.get_status_display()}"
    def generate_qr_code(self):
        """Génère un QR code contenant les infos de cette tentative"""
        qr_content = f"attempt:{self.id}|user:{self.user_id}|test:{self.test_id}"

        qr_image = qrcode.make(qr_content)

        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        file_name = f"attempt_{self.id}.png"

        self.qr_code.save(file_name, File(buffer), save=False)
def calculate_scores_simple(self):
    """Version ultra-simple : scores bruts seulement"""
    mandatory_correct = 0
    optional_correct = 0
    
    mandatory_ids = set(self.test.mandatory_questions)
    
    for question_id, user_answer in self.user_answers.items():
        try:
            question = HSEQuestion.objects.get(id=question_id)
            
            # Convertir la réponse utilisateur si nécessaire
            if isinstance(user_answer, dict):
                user_answer = user_answer.get('answer')
            
            is_correct = question.check_answer(user_answer)
            
            if question_id in mandatory_ids:
                if is_correct:
                    mandatory_correct += 1
            else:
                if is_correct:
                    optional_correct += 1
                    
        except (HSEQuestion.DoesNotExist, ValueError):
            continue
    
    # 1. SCORES BRUTS
    self.mandatory_score = mandatory_correct  # /9
    self.optional_score = optional_correct    # /12
    self.total_score = mandatory_correct + optional_correct  # /21
    
    # 2. RÉUSSITE
    self.passed = (mandatory_correct == 9)
    
    # 3. SAUVEGARDER
    self.save()
    
    return {
        'total': self.total_score,
        'mandatory': self.mandatory_score,
        'optional': self.optional_score,
        'passed': self.passed
    }