from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, username, code_acces):
        if not username:
            raise ValueError('Le nom d\'utilisateur est obligatoire')
        if not code_acces:
            raise ValueError('Le code d\'accès est obligatoire')
        
        user = self.model(
            username=username,
            code_acces=code_acces,
        )
        user.set_unusable_password()  # On n'utilise pas de mot de passe traditionnel
        user.save(using=self._db)
        return user

    def create_superuser(self, username,code_acces):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(username, code_acces)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    
    # Champs d'authentification
    username = models.CharField(max_length=50, unique=True, verbose_name="Nom d'utilisateur")
    code_acces = models.CharField(max_length=20, verbose_name="Code d'accès")
    
    # Informations professionnelles
    poste = models.CharField(max_length=100, blank=True, verbose_name="Poste occupé")
    
    # Statut et permissions
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Dates
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Gestionnaire personnalisé
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['code_acces', 'departement']
    
    class Meta:
        verbose_name = "Utilisateur HSE"
        verbose_name_plural = "Utilisateurs HSE"
    
    def __str__(self):
        return f"{self.username}"

    def authenticate(self, code_acces):
        """Méthode d'authentification personnalisée"""
        return self.code_acces == code_acces and self.is_active

class LoginSession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='login_sessions')
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    success = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-login_time']
        verbose_name = "Session de connexion"
        verbose_name_plural = "Sessions de connexion"
    
    def __str__(self):
        status = "Réussie" if self.success else "Échouée"
        return f"{self.user.username} - {self.login_time.strftime('%d/%m/%Y %H:%M')} - {status}"

class TestVersion(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nom de la version")
    code = models.CharField(max_length=50, unique=True, verbose_name="Code version")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    created_at = models.DateTimeField(auto_now_add=True)
    passing_score = models.IntegerField(default=80, verbose_name="Score de passage (%)")
    duree_minutes = models.IntegerField(default=30, verbose_name="Durée (minutes)")
    
    class Meta:
        verbose_name = "Version de test"
        verbose_name_plural = "Versions de test"
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Question(models.Model):
    QUESTION_TYPES = [
        ('single', 'Choix unique'),
        ('multiple', 'Choix multiple'),
        ('true_false', 'Vrai/Faux'),
    ]
    
    test_version = models.ForeignKey(TestVersion, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(verbose_name="Question")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='single')
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    points = models.PositiveIntegerField(default=1, verbose_name="Points")
    
    class Meta:
        ordering = ['order']
        verbose_name = "Question"
        verbose_name_plural = "Questions"
    
    def __str__(self):
        return f"Q{self.order}: {self.text[:50]}..."

class AnswerOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.TextField(verbose_name="Réponse")
    is_correct = models.BooleanField(default=False, verbose_name="Correcte")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordre")
    
    class Meta:
        ordering = ['order']
        verbose_name = "Option de réponse"
        verbose_name_plural = "Options de réponse"
    
    def __str__(self):
        return f"{self.text[:30]}... ({'✓' if self.is_correct else '✗'})"

class TestSession(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('passed', 'Réussi'),
        ('failed', 'Échoué'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='test_sessions')
    test_version = models.ForeignKey(TestVersion, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    score = models.FloatField(null=True, blank=True, verbose_name="Score (%)")
    time_spent = models.DurationField(null=True, blank=True, verbose_name="Temps passé")
    
    class Meta:
        ordering = ['-start_time']
        verbose_name = "Session de test"
        verbose_name_plural = "Sessions de test"
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.test_version.code} - {self.status}"

class UserAnswer(models.Model):
    test_session = models.ForeignKey(TestSession, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_options = models.ManyToManyField(AnswerOption)
    is_correct = models.BooleanField(default=False)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Réponse utilisateur"
        verbose_name_plural = "Réponses utilisateur"
    
    def __str__(self):
        return f"{self.test_session.user.username} - Q{self.question.order}"