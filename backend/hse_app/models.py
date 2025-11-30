# backend/hse_app/models.py

from django.db import models
import uuid

# -----------------------------
# Utilisateur HSE
# -----------------------------
class HSEUser(models.Model):
    employee_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# -----------------------------
# Tests HSE
# -----------------------------
class HSETest(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration_minutes = models.IntegerField(default=30)
    passing_score = models.IntegerField(default=80)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# -----------------------------
# Session de test
# -----------------------------
class TestSession(models.Model):
    session_code = models.CharField(max_length=50, unique=True, default='')
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    qr_code_data = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=False)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    test = models.ForeignKey(HSETest, on_delete=models.CASCADE)

    def __str__(self):
        return self.session_code


# -----------------------------
# Question de test
# -----------------------------
class TestQuestion(models.Model):
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
    ]

    test = models.ForeignKey(HSETest, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default='multiple_choice')
    points = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.question_text[:50]}..."


# -----------------------------
# Options pour les questions
# -----------------------------
class QuestionOption(models.Model):
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.option_text


# -----------------------------
# Tentative de test par utilisateur
# -----------------------------
class TestAttempt(models.Model):
    user = models.ForeignKey(HSEUser, on_delete=models.CASCADE)
    session = models.ForeignKey(TestSession, on_delete=models.CASCADE)
    score = models.FloatField(default=0)
    passed = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    certificate_generated = models.BooleanField(default=False)
    certificate_file = models.FileField(upload_to='certificates/', blank=True, null=True)

    def __str__(self):
        return f"Attempt {self.id} by {self.user}"


# -----------------------------
# Réponses aux questions
# -----------------------------
class Answer(models.Model):
    test_attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(TestQuestion, on_delete=models.CASCADE)
    answer_text = models.TextField(blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    selected_options = models.ManyToManyField(QuestionOption, blank=True)

    def __str__(self):
        return f"Answer {self.id} for question {self.question.id}"
