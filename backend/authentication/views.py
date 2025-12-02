# views.py (pour le Manager sur PC)
import qrcode
import io
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

@login_required
@csrf_exempt
def generate_test_qr(request, test_id):
    """
    Génère un QR code pour un test spécifique.
    Appelé par le Manager sur son PC.
    """
    if request.method == 'POST':
        # URL vers laquelle rediriger l'utilisateur
        login_url = f"https://votre-domaine.com/test/{test_id}/login/"
        
        # Générer QR code
        qr = qrcode.make(login_url)
        
        # Convertir en base64 pour l'affichage
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return JsonResponse({
            'success': True,
            'qr_code': f"data:image/png;base64,{qr_base64}",
            'test_id': test_id,
            'login_url': login_url
        })
    
    return JsonResponse({'success': False}, status=405)