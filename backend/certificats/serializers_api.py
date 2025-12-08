from rest_framework import serializers
from .models import Certificate
from tests.models import TestAttempt

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
