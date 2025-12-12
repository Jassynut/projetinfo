from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import FileResponse
from .models import Certificate


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def search_certificate_public_fr(request):
    """Alias /api/certificats/recherche (sans auth)"""
    user_cin = request.data.get('cni', '').strip().upper()
    if not user_cin:
        return Response({'success': False, 'error': 'CNI requis'}, status=status.HTTP_400_BAD_REQUEST)

    qs = Certificate.objects.filter(user_cin=user_cin).order_by('-issued_date')[:5]
    if not qs.exists():
        return Response({'success': False, 'error': 'Aucun certificat trouvé'}, status=status.HTTP_404_NOT_FOUND)

    data = []
    for cert in qs:
        data.append({
            'id': cert.id,
            'user_full_name': cert.user_full_name,
            'user_cin': cert.user_cin,
            'test_version': cert.test_version,
            'score': cert.score,
            'issued_date': cert.issued_date,
            'certificate_number': cert.certificate_number,
        })
    return Response({'success': True, 'certificats': data})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def download_certificate_public_fr(request, pk):
    try:
        cert = Certificate.objects.get(id=pk)
    except Certificate.DoesNotExist:
        return Response({'success': False, 'error': 'Certificat introuvable'}, status=status.HTTP_404_NOT_FOUND)

    if cert.is_expired:
        return Response({'success': False, 'error': 'Certificat expiré'}, status=status.HTTP_410_GONE)

    if cert.pdf_file:
        return FileResponse(
            cert.pdf_file.open('rb'),
            as_attachment=True,
            filename=f"certificat_{cert.certificate_number}.pdf"
        )
    return Response({'success': False, 'error': 'PDF non disponible'}, status=status.HTTP_404_NOT_FOUND)

