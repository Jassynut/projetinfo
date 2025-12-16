from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from xhtml2pdf import pisa
from authentication.models import TestUser
from tests.models import TestAttempt
from hse_app.models import HSEUser
from .models import Certificate
from datetime import datetime, timedelta
import json
import uuid
from io import BytesIO

def download_certificate(request, user_id, test_id):
    """Télécharger un certificat existant (ancien endpoint)"""
    try:
        user = TestUser.objects.get(id=user_id)
        attempt = TestAttempt.objects.get(user=user, test_id=test_id)

        html_string = render_to_string('certificate.html', {
            'full_name': user.get_full_name(),
            'score': attempt.overall_score_percentage,
            'total': 100,
            'custom_text': "Félicitations pour votre réussite au test HSE !"
        })

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=certificat_{user.username}.pdf'

        pisa.CreatePDF(html_string, response)
        return response

    except TestUser.DoesNotExist:
        return HttpResponse("Utilisateur non trouvé", status=404)
    except TestAttempt.DoesNotExist:
        return HttpResponse("Tentative de test non trouvée", status=404)


@login_required
def generate_certificate(request, attempt_id):
    """
    Générer un certificat après la réussite d'un test
    GET: /api/certificates/generate/{attempt_id}/
    """
    try:
        attempt = TestAttempt.objects.get(id=attempt_id)
        
        # Vérifier que le test est réussi
        if not attempt.passed:
            return JsonResponse({
                'success': False,
                'error': 'Le test n\'a pas été réussi'
            }, status=400)
        
        # Vérifier si un certificat existe déjà
        if hasattr(attempt, 'certificate'):
            return JsonResponse({
                'success': True,
                'certificate': {
                    'id': str(attempt.certificate.id),
                    'certificate_number': attempt.certificate.certificate_number,
                    'user_full_name': attempt.certificate.user_full_name,
                    'user_cin': attempt.certificate.user_cin,
                    'test_version': attempt.certificate.test_version,
                    'score': attempt.certificate.score,
                    'issued_date': attempt.certificate.issued_date.isoformat(),
                    'expiry_date': attempt.certificate.expiry_date.isoformat(),
                    'is_expired': attempt.certificate.is_expired,
                    'download_url': f'/api/certificates/{attempt.certificate.id}/download/'
                },
                'message': 'Certificat trouvé'
            })
        
        # Créer un nouveau certificat
        user_full_name = attempt.user.full_name or attempt.user.username
        user_cin = attempt.user.cin
        
        certificate_number = f"HSE-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        expiry_date = (datetime.now() + timedelta(days=365)).date()
        
        certificate = Certificate.objects.create(
            test_attempt=attempt,
            certificate_number=certificate_number,
            user_full_name=user_full_name,
            user_cin=user_cin,
            test_version=attempt.test.version,
            score=int(attempt.overall_score_percentage),
            expiry_date=expiry_date
        )
        
        return JsonResponse({
            'success': True,
            'certificate': {
                'id': str(certificate.id),
                'certificate_number': certificate.certificate_number,
                'user_full_name': certificate.user_full_name,
                'user_cin': certificate.user_cin,
                'test_version': certificate.test_version,
                'score': certificate.score,
                'issued_date': certificate.issued_date.isoformat(),
                'expiry_date': certificate.expiry_date.isoformat(),
                'download_url': f'/api/certificates/{certificate.id}/download/'
            },
            'message': 'Certificat généré avec succès'
        })
        
    except TestAttempt.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Tentative non trouvée'
        }, status=404)


@csrf_exempt
def download_certificate_by_id(request, certificate_id):
    """
    Télécharger un certificat en PDF
    GET: /api/certificates/{certificate_id}/download/
    """
    try:
        certificate = Certificate.objects.get(id=certificate_id)
        
        # Vérifier si le certificat est expiré
        if certificate.is_expired:
            return JsonResponse({
                'success': False,
                'error': 'Le certificat a expiré'
            }, status=410)
        
        # Récupérer les informations détaillées de l'utilisateur depuis HSEUser
        user_nom = ""
        user_prenom = ""
        user_entite = ""
        user_chef_projet = ""
        test_date = certificate.issued_date.strftime('%d/%m/%Y')
        
        try:
            from hse_app.models import HSEUser
            hse_user = HSEUser.objects.get(cin=certificate.user_cin)
            user_nom = hse_user.nom
            user_prenom = hse_user.prénom
            user_entite = hse_user.entite or ""
            user_chef_projet = hse_user.chef_projet_ocp or ""
            
            # Si on a une tentative de test, utiliser sa date de complétion
            if certificate.test_attempt and certificate.test_attempt.completed_at:
                test_date = certificate.test_attempt.completed_at.strftime('%d/%m/%Y')
        except HSEUser.DoesNotExist:
            # Si l'utilisateur HSE n'existe pas, extraire nom/prénom du full_name
            name_parts = certificate.user_full_name.split(' ', 1)
            if len(name_parts) >= 2:
                user_prenom = name_parts[0]
                user_nom = name_parts[1]
            else:
                user_nom = certificate.user_full_name
        
        # Chemin absolu du logo pour xhtml2pdf
        from django.conf import settings
        import os
        logo_path = os.path.join(settings.BASE_DIR, 'backend', 'public', 'logo_ocp.webp')
        # Si le fichier webp n'existe pas, essayer png
        if not os.path.exists(logo_path):
            logo_path = os.path.join(settings.BASE_DIR, 'backend', 'public', 'ocp-logo.png')
        # Si toujours pas trouvé, utiliser placeholder
        if not os.path.exists(logo_path):
            logo_path = os.path.join(settings.BASE_DIR, 'backend', 'public', 'placeholder-logo.png')
        
        html_string = render_to_string('certificats/certificate.html', {
            'user_nom': user_nom,
            'user_prenom': user_prenom,
            'user_cin': certificate.user_cin,
            'user_entite': user_entite,
            'user_chef_projet': user_chef_projet,
            'test_date': test_date,
            'logo_path': logo_path
        })
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=certificat_{certificate.certificate_number}.pdf'
        
        pisa.CreatePDF(html_string, response)
        return response
        
    except Certificate.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Certificat non trouvé'
        }, status=404)


@csrf_exempt
def search_certificate_by_name(request):
    """
    Rechercher le certificat d'un utilisateur par son nom
    POST: /api/certificates/search/
    {
        "user_name": "Ahmed Mustafa",
        "user_cin": "AB123456"
    }
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_name = data.get('user_name', '').strip()
            user_cin = data.get('user_cin', '').strip().upper()
            
            if not user_name and not user_cin:
                return JsonResponse({
                    'success': False,
                    'error': 'Veuillez fournir un nom ou un CIN'
                }, status=400)
            
            # Vérifier que le CIN existe dans HSEUser et que sensibilise_avec_succes est True
            if user_cin:
                try:
                    from hse_app.models import HSEUser
                    hse_user = HSEUser.objects.get(cin=user_cin)
                    if not hse_user.sensibilise_avec_succes:
                        return JsonResponse({
                            'success': False,
                            'error': 'Cet utilisateur n\'a pas été sensibilisé avec succès. Impossible de générer un certificat.'
                        }, status=403)
                except HSEUser.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'CIN non trouvé dans la base de données HSE. Veuillez vérifier le numéro.'
                    }, status=404)
            
            # Rechercher les certificats existants
            query = Certificate.objects.all()
            
            if user_cin:
                query = query.filter(user_cin=user_cin)
            elif user_name:
                query = query.filter(user_full_name__icontains=user_name)
            
            query = query.order_by('-issued_date')
            
            # Si aucun certificat n'existe et que le CIN est fourni et sensibilisé, générer un nouveau certificat
            if not query.exists() and user_cin:
                try:
                    from hse_app.models import HSEUser
                    hse_user = HSEUser.objects.get(cin=user_cin)
                    if hse_user.sensibilise_avec_succes:
                        # Générer un nouveau certificat
                        from datetime import timedelta
                        certificate_number = f"HSE-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
                        expiry_date = (datetime.now() + timedelta(days=365)).date()
                        
                        # Créer un certificat sans TestAttempt (certificat de sensibilisation)
                        certificate = Certificate.objects.create(
                            certificate_number=certificate_number,
                            user_full_name=hse_user.get_full_name(),
                            user_cin=hse_user.cin,
                            test_version=0,  # Version 0 pour certificat de sensibilisation
                            score=100,  # Score par défaut pour sensibilisation
                            expiry_date=expiry_date
                        )
                        
                        return JsonResponse({
                            'success': True,
                            'certificates': [{
                                'id': str(certificate.id),
                                'certificate_number': certificate.certificate_number,
                                'user_full_name': certificate.user_full_name,
                                'user_cin': certificate.user_cin,
                                'test_version': certificate.test_version,
                                'score': certificate.score,
                                'issued_date': certificate.issued_date.isoformat(),
                                'expiry_date': certificate.expiry_date.isoformat(),
                                'is_expired': certificate.is_expired,
                                'days_until_expiry': certificate.days_until_expiry,
                                'download_url': f'/api/certificates/{certificate.id}/download/'
                            }],
                            'count': 1,
                            'message': 'Certificat généré avec succès'
                        })
                except HSEUser.DoesNotExist:
                    return JsonResponse({
                        'success': False,
                        'error': 'CIN non trouvé dans la base de données HSE'
                    }, status=404)
            
            if not query.exists():
                return JsonResponse({
                    'success': False,
                    'error': 'Aucun certificat trouvé'
                }, status=404)
            
            certificates = []
            for cert in query[:5]:
                certificates.append({
                    'id': str(cert.id),
                    'certificate_number': cert.certificate_number,
                    'user_full_name': cert.user_full_name,
                    'user_cin': cert.user_cin,
                    'test_version': cert.test_version,
                    'score': cert.score,
                    'issued_date': cert.issued_date.isoformat(),
                    'expiry_date': cert.expiry_date.isoformat(),
                    'is_expired': cert.is_expired,
                    'days_until_expiry': cert.days_until_expiry,
                    'download_url': f'/api/certificates/{cert.id}/download/'
                })
            
            return JsonResponse({
                'success': True,
                'certificates': certificates,
                'count': len(certificates)
            })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Format JSON invalide'
            }, status=400)
    
    return JsonResponse({
        'success': False,
        'error': 'Méthode non autorisée'
    }, status=405)
