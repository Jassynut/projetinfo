from rest_framework import serializers
from .models import Certificate

class CertificateSerializer(serializers.ModelSerializer):
    is_expired = serializers.ReadOnlyField()
    days_until_expiry = serializers.ReadOnlyField()
    
    class Meta:
        model = Certificate
        fields = [
            'id',
            'certificate_number',
            'user_full_name',
            'user_cin',
            'test_version',
            'score',
            'issued_date',
            'expiry_date',
            'is_expired',
            'days_until_expiry'
        ]
