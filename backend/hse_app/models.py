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
        validators=[MinValueValidator(1)]
    )
    passing_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="Score de passage (%)"
    )
    
    # Ordre des questions pour cette version
    ordre_questions = models.JSONField(
        verbose_name="Ordre des questions",
        help_text="Liste des IDs de questions dans l'ordre spécifique à cette version"
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
        result = self.testattempt_set.filter(
            completed_at__isnull=False
        ).aggregate(avg_score=models.Avg('score'))
        return round(result['avg_score'] or 0, 1)


class HSEQuestion(models.Model):
    """Question individuelle pour les tests HSE (Vrai/Faux uniquement)"""
    
    DIFFICULTY_CHOICES = [
        ('facile', 'Facile'),
        ('moyen', 'Moyen'),
        ('difficile', 'Difficile'),
    ]
    
    CATEGORY_CHOICES = [
        ('securite', 'Sécurité'),
        ('sante', 'Santé'),
        ('environnement', 'Environnement'),
        ('general', 'Général'),
    ]
    
    # Énoncé de la question en trois langues
    enonce_fr = models.TextField(verbose_name="Énoncé (Français)")
    enonce_en = models.TextField(verbose_name="Énoncé (Anglais)", blank=True)
    enonce_es = models.TextField(verbose_name="Énoncé (Espagnol)", blank=True)
    
    # Réponse correcte (Vrai/Faux)
    reponse_correcte = models.BooleanField(
        verbose_name="Réponse correcte",
        help_text="Cochez si la réponse correcte est VRAI"
    )
    
    # Catégorie et difficulté
    categorie = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general',
        verbose_name="Catégorie"
    )
    niveau_difficulte = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='moyen',
        verbose_name="Niveau de difficulté"
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
    
    # Explication en trois langues
    explanation_fr = models.TextField(
        verbose_name="Explication (Français)",
        blank=True,
        help_text="Explication de la réponse correcte"
    )
    explanation_en = models.TextField(
        verbose_name="Explication (Anglais)",
        blank=True,
        help_text="Explication de la réponse correcte"
    )
    explanation_es = models.TextField(
        verbose_name="Explication (Espagnol)",
        blank=True,
        help_text="Explication de la réponse correcte"
    )
    
    # Métadonnées
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    
    # Relation avec les tests
    tests = models.ManyToManyField(
        HSETest,
        through='TestQuestionOrder',
        related_name='questions',
        blank=True
    )
    
    class Meta:
        verbose_name = "Question HSE"
        verbose_name_plural = "Questions HSE"
        ordering = ['categorie', 'niveau_difficulte', 'created_at']
        indexes = [
            models.Index(fields=['categorie']),
            models.Index(fields=['niveau_difficulte']),
            models.Index(fields=['is_active']),
            models.Index(fields=['reponse_correcte']),
        ]
    
    def __str__(self):
        return f"Q{self.id}: {self.enonce_fr[:50]}... ({self.get_categorie_display()})"
    
    def get_enonce(self, langue='fr'):
        """Retourne l'énoncé dans la langue spécifiée"""
        lang_map = {
            'fr': self.enonce_fr,
            'en': self.enonce_en,
            'es': self.enonce_es
        }
        return lang_map.get(langue, self.enonce_fr)
    
    def get_explanation(self, langue='fr'):
        """Retourne l'explication dans la langue spécifiée"""
        lang_map = {
            'fr': self.explanation_fr,
            'en': self.explanation_en,
            'es': self.explanation_es
        }
        return lang_map.get(langue, self.explanation_fr)
    
    def check_answer(self, user_answer):
        """Vérifie si la réponse de l'utilisateur est correcte"""
        # Convertir la réponse de l'utilisateur en booléen
        if isinstance(user_answer, str):
            user_answer = user_answer.lower().strip()
            if user_answer in ['vrai', 'true', 'verdadero', '1', 'yes', 'oui']:
                user_bool = True
            elif user_answer in ['faux', 'false', 'falso', '0', 'no', 'non']:
                user_bool = False
            else:
                # Si on ne peut pas convertir, retourner False
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


class TestQuestionOrder(models.Model):
    """Table intermédiaire pour gérer l'ordre des questions dans chaque test"""
    
    test = models.ForeignKey(HSETest, on_delete=models.CASCADE)
    question = models.ForeignKey(HSEQuestion, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )
    
    class Meta:
        ordering = ['test', 'order']
        unique_together = ['test', 'question']
        verbose_name = "Ordre des questions"
        verbose_name_plural = "Ordres des questions"
    
    def __str__(self):
        return f"Version {self.test.version} - Question {self.order}: Q{self.question.id}"


class TestAttempt(models.Model):
    """Tentative de test par un utilisateur"""
    
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
            ('fr', 'Français'),
            ('en', 'Anglais'),
            ('es', 'Espagnol'),
        ],
        default='fr',
        verbose_name="Langue du test"
    )
    
    # Résultats
    score = models.FloatField(
        default=0,
        verbose_name="Score obtenu"
    )
    max_score = models.FloatField(
        verbose_name="Score maximum possible"
    )
    percentage = models.FloatField(
        verbose_name="Pourcentage",
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    passed = models.BooleanField(default=False, verbose_name="Réussi")
    
    # Détail des réponses
    correct_answers = models.IntegerField(
        default=0,
        verbose_name="Nombre de bonnes réponses"
    )
    wrong_answers = models.IntegerField(
        default=0,
        verbose_name="Nombre de mauvaises réponses"
    )
    
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
        help_text="Format: {question_id: réponse_vrai_faux, ...}"
    )
    
    class Meta:
        verbose_name = "Tentative de test"
        verbose_name_plural = "Tentatives de test"
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'test']),
            models.Index(fields=['completed_at']),
            models.Index(fields=['passed']),
            models.Index(fields=['langue']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - Version {self.test.version} ({self.percentage}%)"
    
    def calculate_score(self):
        """Calcule le score basé sur les réponses"""
        total_points = 0
        earned_points = 0
        correct = 0
        wrong = 0
        
        for qid, user_answer in self.user_answers.items():
            try:
                question = HSEQuestion.objects.get(id=qid)
                total_points += question.points
                
                if question.check_answer(user_answer):
                    earned_points += question.points
                    correct += 1
                else:
                    wrong += 1
            except HSEQuestion.DoesNotExist:
                continue
        
        self.score = earned_points
        self.max_score = total_points if total_points > 0 else 1
        self.percentage = round((earned_points / self.max_score) * 100, 2)
        self.passed = self.percentage >= self.test.passing_score
        self.correct_answers = correct
        self.wrong_answers = wrong
        
        self.save()
        return self.score, self.percentage
    
    def get_question_detail(self, question_id, language='fr'):
        """Récupère les détails d'une question avec la langue spécifiée"""
        try:
            question = HSEQuestion.objects.get(id=question_id)
            return {
                'id': question.id,
                'enonce': question.get_enonce(language),
                'explication': question.get_explanation(language),
                'reponse_correcte': question.reponse_correcte_display,
                'image_url': question.image.url if question.image else None,
            }
        except HSEQuestion.DoesNotExist:
            return None