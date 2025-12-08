from django.db import models
import json
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

# Create your models here.
   
class Test(models.Model):
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
            return Question.objects.none()
        
        # Crée un dictionnaire pour préserver l'ordre
        question_dict = {}
        questions = Question.objects.filter(id__in=self.ordre_questions)
        
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
            return Question.objects.none()
        
        mandatory_questions_list = []
        for qid in self.mandatory_questions:
            try:
                question = Question.objects.get(id=qid)
                mandatory_questions_list.append(question)
            except Question.DoesNotExist:
                continue
        
        return mandatory_questions_list
    
    def get_optional_questions(self):
        """Récupère les questions optionnelles"""
        if not self.ordre_questions:
            return Question.objects.none()
        
        mandatory_ids = set(self.mandatory_questions)
        optional_ids = [qid for qid in self.ordre_questions if qid not in mandatory_ids]
        
        optional_questions_list = []
        for qid in optional_ids:
            try:
                question = Question.objects.get(id=qid)
                optional_questions_list.append(question)
            except Question.DoesNotExist:
                continue
        
        return optional_questions_list


class Question(models.Model):
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
    enonce_ar = models.TextField(verbose_name="Énoncé (Arabe)", blank=True)
    
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
        
        # user_answer sera maintenant un booléen direct (True/False)
        # provenant des boutons cliqués
        
        # Si c'est déjà un booléen, utiliser directement
        if isinstance(user_answer, bool):
            return user_answer == self.reponse_correcte
        
        # Si c'est une chaîne "true"/"false" (venant du frontend)
        if isinstance(user_answer, str):
            user_answer = user_answer.lower().strip()
            if user_answer in ['true', 'vrai', '1', 'yes', 'oui', 't']:
                user_bool = True
            elif user_answer in ['false', 'faux', '0', 'no', 'non', 'f']:
                user_bool = False
            else:
                return False
            return user_bool == self.reponse_correcte
        
        # Si c'est un entier (0/1)
        if isinstance(user_answer, int):
            user_bool = bool(user_answer)
            return user_bool == self.reponse_correcte
        
        return False
    
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
    
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
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
    
    def calculate_scores(self):
        """Calculer tous les scores d'une tentative"""
        if not self.user_answers:
            return {
                'total': 0,
                'mandatory': 0,
                'optional': 0,
                'passed': False
            }
        
        mandatory_correct = 0
        optional_correct = 0
        
        mandatory_ids = set(self.test.mandatory_questions)
        
        for question_id_str, user_answer in self.user_answers.items():
            try:
                question_id = int(question_id_str)
                question = Question.objects.get(id=question_id)
                
                # Gérer le format des réponses
                if isinstance(user_answer, dict):
                    user_answer = user_answer.get('answer')
                
                if user_answer is None:
                    continue
                
                is_correct = question.check_answer(user_answer)
                
                if question_id in mandatory_ids:
                    if is_correct:
                        mandatory_correct += 1
                else:
                    if is_correct:
                        optional_correct += 1
                        
            except (Question.DoesNotExist, ValueError):
                continue
        
        # Réussite: toutes les questions obligatoires correctes
        passed = (mandatory_correct == self.mandatory_total)
        
        return {
            'total': mandatory_correct + optional_correct,
            'mandatory': mandatory_correct,
            'optional': optional_correct,
            'passed': passed
        }
