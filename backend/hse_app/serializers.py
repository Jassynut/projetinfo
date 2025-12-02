from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from .models import UserProfile, TestVersion, Question, AnswerOption, TestSession, UserAnswer

User = get_user_model()

# =============================================================================
# SERIALIZERS D'AUTHENTIFICATION
# =============================================================================

class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50, required=True)
    code_acces = serializers.CharField(max_length=20, write_only=True, required=True)

    def validate(self, data):
        username = data.get('username')
        code_acces = data.get('code_acces')

        if not username or not code_acces:
            raise serializers.ValidationError("Nom d'utilisateur et code d'accès requis")

        try:
            user = User.objects.get(username=username, is_active=True)

            # Vérifier le profil admin
            if not hasattr(user, 'profile') or not user.profile.is_admin:
                raise serializers.ValidationError("Utilisateur non admin")

            if not user.profile.authenticate(code_acces):
                raise serializers.ValidationError("Code d'accès incorrect")

            data['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError("Nom d'utilisateur incorrect ou compte désactivé")

        return data


class TestUserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50, required=True)
    code_acces = serializers.CharField(max_length=20, write_only=True, required=True)

    def validate(self, data):
        username = data.get('username')
        code_acces = data.get('code_acces')

        if not username or not code_acces:
            raise serializers.ValidationError("Nom d'utilisateur et code d'accès requis")

        try:
            user = User.objects.get(username=username, is_active=True)

            # Vérifier le profil test user
            if not hasattr(user, 'profile') or user.profile.is_admin:
                raise serializers.ValidationError("Utilisateur non autorisé à passer le test")

            if not user.profile.authenticate(code_acces):
                raise serializers.ValidationError("Code d'accès incorrect")

            data['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError("Nom d'utilisateur incorrect ou compte désactivé")

        return data


# =============================================================================
# SERIALIZERS DES UTILISATEURS
# =============================================================================

class AdminUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['code_acces', 'poste']  # Seul admin a besoin de ces champs
        extra_kwargs = {
            'code_acces': {'write_only': True}
        }


class TestUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'entite', 'entreprise', 'chef_projet_ocp', 'nom', 'prenom',
            'cin', 'email', 'poste'
        ]
        extra_kwargs = {
            'cin': {'write_only': True}
        }


class AdminUserSerializer(serializers.ModelSerializer):
    profile = AdminUserProfileSerializer()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'profile']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class TestUserSerializer(serializers.ModelSerializer):
    profile = TestUserProfileSerializer()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'profile']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


# =============================================================================
# SERIALIZERS POUR LES TESTS ET QUESTIONS
# =============================================================================

class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = ['id', 'text', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    options = AnswerOptionSerializer(many=True, read_only=True)
    has_image = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'order', 'points', 'options', 'has_image']

    def get_has_image(self, obj):
        return bool(obj.image)


class TestVersionListSerializer(serializers.ModelSerializer):
    questions_count = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()

    class Meta:
        model = TestVersion
        fields = ['id', 'name', 'code', 'description', 'is_active', 'passing_score', 'questions_count', 'is_available', 'created_at']

    def get_questions_count(self, obj):
        return obj.questions.count()

    def get_is_available(self, obj):
        return obj.is_active


class TestVersionDetailSerializer(TestVersionListSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    class Meta(TestVersionListSerializer.Meta):
        fields = TestVersionListSerializer.Meta.fields + ['questions']


# =============================================================================
# SERIALIZERS DE SESSIONS DE TEST
# =============================================================================

class UserAnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(source='question.text', read_only=True)
    question_id = serializers.IntegerField(source='question.id', read_only=True)

    class Meta:
        model = UserAnswer
        fields = ['id', 'question_id', 'question_text', 'is_correct']


class TestSessionListSerializer(serializers.ModelSerializer):
    test_version_name = serializers.CharField(source='test_version.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = TestSession
        fields = ['id', 'test_version_name', 'user_name', 'start_time', 'end_time', 'status', 'score', 'time_spent']


class TestSessionDetailSerializer(TestSessionListSerializer):
    user_answers = UserAnswerSerializer(many=True, read_only=True)
    test_version = TestVersionListSerializer(read_only=True)

    class Meta(TestSessionListSerializer.Meta):
        fields = TestSessionListSerializer.Meta.fields + ['user_answers', 'test_version']
