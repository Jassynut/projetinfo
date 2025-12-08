from rest_framework import serializers
from .models import Test, Question, TestAttempt
from hse_app.serializers import QuestionSimpleSerializer, QuestionDetailSerializer

# Ceci évite les conflits avec les serializers existants

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
