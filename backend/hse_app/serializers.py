from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import HSEUser, HSEManager
from tests.models import Test, Question, TestAttempt
from certificats.models import Certificate
from authentication.models import TestUser

# =============================================================================
# SERIALIZERS HSE USERS
# =============================================================================

class HSEUserListSerializer(serializers.ModelSerializer):
    """Sérializer simplifié pour lister les utilisateurs HSE"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = HSEUser
        fields = [
            'id', 'nom', 'prénom', 'full_name', 'cin', 
            'entite', 'entreprise', 'presence', 'taux_reussite'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class HSEUserDetailSerializer(serializers.ModelSerializer):
    """Sérializer complet pour détails utilisateur HSE"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = HSEUser
        fields = [
            'id', 'nom', 'prénom', 'full_name', 'cin',
            'entite', 'entreprise', 'chef_projet_ocp',
            'presence', 'taux_reussite'
        ]
        read_only_fields = ['taux_reussite']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class HSEUserCreateUpdateSerializer(serializers.ModelSerializer):
    """Sérializer pour création/modification d'utilisateur HSE"""
    
    class Meta:
        model = HSEUser
        fields = [
            'nom', 'prénom', 'cin',
            'entite', 'entreprise', 'chef_projet_ocp',
            'presence'
        ]
        extra_kwargs = {
            'cin': {'validators': []}  # Retirer la validation d'unicité lors de la mise à jour
        }
    
    def validate_cin(self, value):
        if not value or len(value) < 3:
            raise serializers.ValidationError("CIN invalide")
        return value.upper()




# =============================================================================
# SERIALIZERS TESTS HSE
# =============================================================================

class QuestionSimpleSerializer(serializers.ModelSerializer):
    """Sérializer simplifié pour les questions (sans réponse correcte)"""
    
    class Meta:
        model = Question
        fields = [
            'id', 'question_code', 'enonce_fr', 'enonce_en', 'enonce_ar',
            'is_mandatory', 'points', 'has_image'
        ]


class QuestionDetailSerializer(serializers.ModelSerializer):
    """Sérializer complet pour les questions"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = [
            'id', 'question_code', 'enonce_fr', 'enonce_en', 'enonce_ar',
            'reponse_correcte', 'is_mandatory', 'points', 'image', 'image_url', 'has_image',
            'is_active', 'created_at', 'updated_at'
        ]
    
    def get_image_url(self, obj):
        if obj.image:
            # Retourner un chemin relatif pour que nginx puisse proxifier correctement
            # Le frontend construira l'URL complète avec API_BASE
            return obj.image.url  # Ex: /media/questions/hse/image.jpg
        return None


class TestListSerializer(serializers.ModelSerializer):
    """Sérializer simplifié pour lister les tests"""
    questions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Test
        fields = [
            'id', 'version', 'description', 'duration_minutes',
            'total_questions', 'mandatory_questions_count', 
            'passing_score_optional', 'questions_count',
            'is_active', 'created_at'
        ]
    
    def get_questions_count(self, obj):
        return obj.questions_count


class TestDetailSerializer(serializers.ModelSerializer):
    """Sérializer complet pour détails du test"""
    questions = serializers.SerializerMethodField()
    mandatory_questions_list = serializers.SerializerMethodField()
    optional_questions_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Test
        fields = [
            'id', 'version', 'description', 'duration_minutes',
            'total_questions', 'mandatory_questions_count',
            'passing_score_optional', 'questions_count',
            'optional_questions_count', 'is_active',
            'questions', 'mandatory_questions_list', 'optional_questions_list',
            'created_at', 'updated_at'
        ]
    
    def get_questions(self, obj):
        questions = obj.get_questions_in_order()
        return QuestionSimpleSerializer(questions, many=True).data
    
    def get_mandatory_questions_list(self, obj):
        questions = obj.get_mandatory_questions()
        return QuestionSimpleSerializer(questions, many=True).data
    
    def get_optional_questions_list(self, obj):
        questions = obj.get_optional_questions()
        return QuestionSimpleSerializer(questions, many=True).data


class TestCreateUpdateSerializer(serializers.ModelSerializer):
    """Sérializer pour création/modification de test"""
    
    class Meta:
        model = Test
        fields = [
            'version', 'description', 'duration_minutes',
            'total_questions', 'mandatory_questions_count',
            'passing_score_optional', 'ordre_questions',
            'mandatory_questions', 'is_active'
        ]
    
    def validate_version(self, value):
        if value < 1 or value > 6:
            raise serializers.ValidationError("Version doit être entre 1 et 6")
        return value


# =============================================================================
# SERIALIZERS TEST ATTEMPTS
# =============================================================================

class TestAttemptListSerializer(serializers.ModelSerializer):
    """Sérializer simplifié pour lister les tentatives"""
    test_version = serializers.IntegerField(source='test.version', read_only=True)
    user_cin = serializers.CharField(source='user.cin', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = TestAttempt
        fields = [
            'id', 'test_version', 'user_cin', 'user_name',
            'langue', 'status', 'mandatory_score_percentage',
            'optional_score_percentage', 'overall_score_percentage',
            'passed', 'started_at', 'completed_at', 'time_taken_seconds'
        ]
    
    def get_user_name(self, obj):
        return obj.user.full_name or obj.user.username


class TestAttemptDetailSerializer(serializers.ModelSerializer):
    """Sérializer complet pour détails de la tentative"""
    test_version = serializers.IntegerField(source='test.version', read_only=True)
    user_cin = serializers.CharField(source='user.cin', read_only=True)
    user_name = serializers.SerializerMethodField()
    test_details = serializers.SerializerMethodField()
    
    class Meta:
        model = TestAttempt
        fields = [
            'id', 'test_version', 'user_cin', 'user_name',
            'langue', 'status', 'mandatory_correct', 'mandatory_wrong',
            'mandatory_total', 'optional_correct', 'optional_wrong',
            'optional_total', 'mandatory_score_percentage',
            'optional_score_percentage', 'overall_score_percentage',
            'passed', 'started_at', 'completed_at', 'time_taken_seconds',
            'user_answers', 'test_details'
        ]
        read_only_fields = ['started_at', 'completed_at', 'user_answers']
    
    def get_user_name(self, obj):
        return obj.user.full_name or obj.user.username
    
    def get_test_details(self, obj):
        return {
            'version': obj.test.version,
            'total_questions': obj.test.total_questions,
            'duration_minutes': obj.test.duration_minutes
        }


class TestAttemptStartSerializer(serializers.Serializer):
    """Sérializer pour démarrer un test"""
    test_id = serializers.IntegerField()
    langue = serializers.ChoiceField(choices=[('ar', 'Arabe'), ('fr', 'Français'), ('en', 'Anglais')])


class TestAttemptSubmitSerializer(serializers.Serializer):
    """Sérializer pour soumettre les réponses"""
    user_answers = serializers.JSONField()
    time_taken_seconds = serializers.IntegerField(required=False, default=0)


# =============================================================================
# SERIALIZERS CERTIFICATS
# =============================================================================

class CertificateListSerializer(serializers.ModelSerializer):
    """Sérializer simplifié pour lister les certificats"""
    
    class Meta:
        model = Certificate
        fields = [
            'id', 'certificate_number', 'user_full_name', 'user_cin',
            'test_version', 'score', 'issued_date', 'expiry_date',
            'is_expired', 'days_until_expiry'
        ]


class CertificateDetailSerializer(serializers.ModelSerializer):
    """Sérializer complet pour détails du certificat"""
    attempt_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Certificate
        fields = [
            'id', 'certificate_number', 'user_full_name', 'user_cin',
            'test_version', 'score', 'issued_date', 'expiry_date',
            'is_expired', 'days_until_expiry', 'pdf_file', 'attempt_details'
        ]
        read_only_fields = ['issued_date']
    
    def get_attempt_details(self, obj):
        return {
            'attempt_id': obj.test_attempt.id,
            'completed_at': obj.test_attempt.completed_at.isoformat() if obj.test_attempt.completed_at else None,
            'overall_score': obj.test_attempt.overall_score_percentage
        }


class CertificateSearchSerializer(serializers.Serializer):
    """Sérializer pour rechercher un certificat"""
    user_name = serializers.CharField(required=False, allow_blank=True)
    user_cin = serializers.CharField(required=False, allow_blank=True)


# =============================================================================
# SERIALIZERS MANAGERS
# =============================================================================

class HSEManagerListSerializer(serializers.ModelSerializer):
    """Sérializer pour lister les managers"""
    
    class Meta:
        model = HSEManager
        fields = ['id', 'full_name', 'cin']


class HSEManagerDetailSerializer(serializers.ModelSerializer):
    """Sérializer complet pour manager"""
    managed_users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = HSEManager
        fields = ['id', 'full_name', 'cin', 'managed_users_count']
    
    def get_managed_users_count(self, obj):
        return HSEUser.objects.count()  # À adapter selon votre logique


class HSEManagerCreateUpdateSerializer(serializers.ModelSerializer):
    """Sérializer pour créer/modifier un manager"""
    
    class Meta:
        model = HSEManager
        fields = ['full_name', 'cin']
    
    def validate_cin(self, value):
        if not value or len(value) < 3:
            raise serializers.ValidationError("CIN invalide")
        return value.upper()
