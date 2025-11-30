from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import UserProfile, TestVersion, Question, AnswerOption, TestSession, UserAnswer

# =============================================================================
# SERIALIZERS D'AUTHENTIFICATION
# =============================================================================

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        max_length=50,
        required=True,
        label="Nom d'utilisateur",
        help_text="ex: hse.manager"
    )
    code_acces = serializers.CharField(
        max_length=20,
        required=True,
        write_only=True,
        label="Code d'accès",
        help_text="Code d'accès personnel"
    )

    def validate(self, data):
        username = data.get('username')
        code_acces = data.get('code_acces')
        
        if not username or not code_acces:
            raise serializers.ValidationError("Le nom d'utilisateur et le code d'accès sont obligatoires")
        
        try:
            user = User.objects.get(username=username, is_active=True)
            
            # Vérifier si le profil existe
            if not hasattr(user, 'profile'):
                raise serializers.ValidationError("Profil utilisateur non configuré")
            
            # Authentifier avec le code d'accès
            if not user.profile.authenticate(code_acces):
                raise serializers.ValidationError("Code d'accès incorrect")
                
            data['user'] = user
            
        except User.DoesNotExist:
            raise serializers.ValidationError("Nom d'utilisateur incorrect ou compte désactivé")
        
        return data

# =============================================================================
# SERIALIZERS D'UTILISATEURS
# =============================================================================

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'code_acces', 'departement', 'site', 'poste']
        extra_kwargs = {
            'code_acces': {'write_only': True}
        }

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    departement_display = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'first_name', 
            'last_name', 
            'full_name',
            'email', 
            'profile',
            'departement_display'
        ]
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    def get_departement_display(self, obj):
        if hasattr(obj, 'profile'):
            return obj.profile.get_departement_display()
        return "Non défini"

class CreateUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'profile']
    
    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password', None)
        
        # Créer l'utilisateur
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()  # Pas de mot de passe traditionnel
        user.save()
        
        # Créer le profil
        UserProfile.objects.create(user=user, **profile_data)
        
        return user

# =============================================================================
# SERIALIZERS DE TESTS ET QUESTIONS
# =============================================================================

class AnswerOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerOption
        fields = ['id', 'text', 'order']
        # Note: on ne sérialise pas 'is_correct' pour éviter la triche

class QuestionSerializer(serializers.ModelSerializer):
    options = AnswerOptionSerializer(many=True, read_only=True)
    has_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Question
        fields = [
            'id', 
            'text', 
            'question_type', 
            'order', 
            'points', 
            'options',
            'has_image'
        ]
    
    def get_has_image(self, obj):
        return bool(obj.image)

class TestVersionListSerializer(serializers.ModelSerializer):
    questions_count = serializers.SerializerMethodField()
    duree_minutes = serializers.IntegerField()
    is_available = serializers.SerializerMethodField()
    
    class Meta:
        model = TestVersion
        fields = [
            'id', 
            'name', 
            'code', 
            'description', 
            'is_active', 
            'passing_score',
            'questions_count',
            'duree_minutes',
            'is_available',
            'created_at'
        ]
    
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
        fields = [
            'id', 
            'question_id',
            'question_text', 
            'is_correct', 
            'answered_at'
        ]

class TestSessionListSerializer(serializers.ModelSerializer):
    test_version_name = serializers.CharField(source='test_version.name', read_only=True)
    test_version_code = serializers.CharField(source='test_version.code', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    score_display = serializers.SerializerMethodField()
    duree_display = serializers.SerializerMethodField()
    
    class Meta:
        model = TestSession
        fields = [
            'id',
            'test_version_name',
            'test_version_code',
            'user_name',
            'start_time',
            'end_time',
            'status',
            'score',
            'score_display',
            'time_spent',
            'duree_display'
        ]
    
    def get_score_display(self, obj):
        if obj.score is not None:
            return f"{obj.score:.1f}%"
        return "N/A"
    
    def get_duree_display(self, obj):
        if obj.time_spent:
            total_seconds = int(obj.time_spent.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            seconds = total_seconds % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return "N/A"

class TestSessionDetailSerializer(TestSessionListSerializer):
    user_answers = UserAnswerSerializer(many=True, read_only=True)
    test_version = TestVersionListSerializer(read_only=True)
    
    class Meta(TestSessionListSerializer.Meta):
        fields = TestSessionListSerializer.Meta.fields + ['user_answers', 'test_version']

# =============================================================================
# SERIALIZERS POUR LES ACTIONS
# =============================================================================

class StartTestSerializer(serializers.Serializer):
    test_version_id = serializers.IntegerField(required=True)
    
    def validate_test_version_id(self, value):
        try:
            test_version = TestVersion.objects.get(id=value, is_active=True)
        except TestVersion.DoesNotExist:
            raise serializers.ValidationError("Version de test non trouvée ou inactive")
        return value

class SubmitAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField(required=True)
    selected_option_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    
    def validate_question_id(self, value):
        try:
            Question.objects.get(id=value)
        except Question.DoesNotExist:
            raise serializers.ValidationError("Question non trouvée")
        return value
    
    def validate_selected_option_ids(self, value):
        if not value:
            raise serializers.ValidationError("Au moins une option doit être sélectionnée")
        return value

class TestResultSerializer(serializers.Serializer):
    session_id = serializers.IntegerField(read_only=True)
    score = serializers.FloatField(read_only=True)
    correct_answers = serializers.IntegerField(read_only=True)
    total_questions = serializers.IntegerField(read_only=True)
    passing_score = serializers.IntegerField(read_only=True)
    status = serializers.CharField(read_only=True)
    time_spent = serializers.DurationField(read_only=True)
    passed = serializers.BooleanField(read_only=True)

# =============================================================================
# SERIALIZERS POUR STATISTIQUES
# =============================================================================

class UserStatsSerializer(serializers.Serializer):
    total_tests = serializers.IntegerField()
    tests_passed = serializers.IntegerField()
    tests_failed = serializers.IntegerField()
    success_rate = serializers.FloatField()
    average_score = serializers.FloatField()
    total_time_spent = serializers.DurationField()

class TestStatsSerializer(serializers.Serializer):
    test_version_name = serializers.CharField()
    total_sessions = serializers.IntegerField()
    success_rate = serializers.FloatField()
    average_score = serializers.FloatField()
    average_time = serializers.DurationField()

# =============================================================================
# SERIALIZERS POUR L'ADMIN
# =============================================================================

class AdminUserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    last_login = serializers.DateTimeField(format="%d/%m/%Y %H:%M", read_only=True)
    date_joined = serializers.DateTimeField(format="%d/%m/%Y %H:%M", read_only=True)
    test_sessions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'is_active', 'is_staff', 'last_login', 'date_joined',
            'profile', 'test_sessions_count'
        ]
    
    def get_test_sessions_count(self, obj):
        return obj.test_sessions.count()

class BulkCreateUsersSerializer(serializers.Serializer):
    users_data = serializers.ListField(
        child=serializers.DictField(),
        required=True
    )
    
    def validate_users_data(self, value):
        required_fields = ['username', 'first_name', 'last_name', 'code_acces', 'departement']
        
        for user_data in value:
            for field in required_fields:
                if field not in user_data or not user_data[field]:
                    raise serializers.ValidationError(
                        f"Le champ '{field}' est obligatoire pour tous les utilisateurs"
                    )
        
        return value