from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from hse_app.models import HSEUser
from tests.models import TestAttempt
from datetime import datetime, timedelta
import json
import uuid
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
def search_certificate_public_fr(request):
    """Alias /api/certificats/recherche (sans auth)"""
    try:
        if request.method != 'POST':
            return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
        
        try:
            data = json.loads(request.body) if request.body else {}
            user_cin = data.get('cni', '').strip().upper()
        except json.JSONDecodeError:
            user_cin = request.POST.get('cni', '').strip().upper()
        
        if not user_cin:
            return JsonResponse({'success': False, 'error': 'CNI requis'}, status=400)
        
        logger.info(f"Recherche certificat pour CIN: {user_cin}")

        # Vérifier si le CIN existe dans HSEUser (recherche case-insensitive)
        hse_user = None
        try:
            # Rechercher avec __iexact pour être insensible à la casse
            hse_user = HSEUser.objects.get(cin__iexact=user_cin)
            logger.info(f"Utilisateur HSE trouvé: {hse_user.get_full_name()}")
        except HSEUser.DoesNotExist:
            logger.warning(f"CIN non trouvé: {user_cin}")
            return JsonResponse({
                'success': False, 
                'error': 'CIN non trouvé dans la base de données HSE. Veuillez vérifier le numéro.'
            }, status=404)
        except HSEUser.MultipleObjectsReturned:
            # Si plusieurs utilisateurs ont le même CIN (ne devrait pas arriver), prendre le premier
            logger.warning(f"Plusieurs utilisateurs avec le même CIN: {user_cin}")
            hse_user = HSEUser.objects.filter(cin__iexact=user_cin).first()

        # Récupérer les informations de l'utilisateur
        user_info = {
            'full_name': hse_user.get_full_name(),
            'cin': hse_user.cin,
            'entreprise': hse_user.entreprise or '',
            'entite': hse_user.entite or '',
        }

        # Vérifier si l'utilisateur est sensibilisé
        if not hse_user.sensibilise_avec_succes:
            logger.warning(f"Utilisateur non sensibilisé: {user_cin}")
            return JsonResponse({
                'success': False,
                'error': 'Cet utilisateur n\'a pas été sensibilisé avec succès. Impossible de générer un certificat.'
            }, status=403)

        # Générer les certificats à la volée (sans les sauvegarder)
        data = []
        
        # Certificats basés sur les tests réussis uniquement
        try:
            # Chercher les tentatives de test réussies pour cet utilisateur
            from authentication.models import TestUser
            test_user = TestUser.objects.filter(cin__iexact=hse_user.cin).first()
            if test_user:
                # Ne chercher que les tentatives de test final réussies
                passed_attempts = TestAttempt.objects.filter(
                    user=test_user,
                    passed=True,
                    status='passed',
                    etat='test_final'
                ).order_by('-completed_at')[:5]
                
                for attempt in passed_attempts:
                    # Vérifier que completed_at existe
                    if not attempt.completed_at:
                        continue
                    
                    cert_number = f"HSE-{attempt.completed_at.strftime('%Y%m%d')}-{attempt.id}"
                    expiry = (attempt.completed_at + timedelta(days=365)).date()
                    
                    # Calculer la durée du test
                    # Si time_taken_seconds est 0 ou invalide, calculer depuis started_at et completed_at
                    if attempt.time_taken_seconds and attempt.time_taken_seconds > 0:
                        time_taken_seconds = attempt.time_taken_seconds
                    elif attempt.started_at and attempt.completed_at:
                        # Calculer la différence entre started_at et completed_at
                        time_delta = attempt.completed_at - attempt.started_at
                        time_taken_seconds = int(time_delta.total_seconds())
                    else:
                        time_taken_seconds = 0
                    
                    # Arrondir les minutes au lieu d'utiliser la division entière
                    # Utiliser round() pour arrondir correctement (ex: 30 secondes = 0.5 minute → 1 minute)
                    time_taken_minutes = round(time_taken_seconds / 60) if time_taken_seconds > 0 else 0
                    
                    # Calculer le score réel sur 21 (nombre de bonnes réponses)
                    score_sur_21 = attempt.mandatory_correct + attempt.optional_correct
                    
                    data.append({
                        'id': f"cert::{hse_user.cin}::test::{attempt.id}",
                        'user_full_name': hse_user.get_full_name(),
                        'user_cin': hse_user.cin,
                        'test_version': attempt.test.version,
                        'score': int(attempt.overall_score_percentage),
                        'date_test': attempt.completed_at.isoformat(),
                        'score_sur_21': score_sur_21,
                        'time_taken_minutes': time_taken_minutes,
                        'certificate_number': cert_number,
                        'issued_date': attempt.completed_at.isoformat(),
                        'expiry_date': expiry.isoformat(),
                        'attempt_id': attempt.id,
                    })
        except Exception as e:
            logger.warning(f"Erreur lors de la récupération des tentatives de test: {str(e)}")
        
        logger.info(f"Retour de {len(data)} certificats générés à la volée")
        return JsonResponse({
            'success': True,
            'user_info': user_info,
            'certificats': data
        })
    except Exception as e:
        import traceback
        logger.error(f"Erreur dans search_certificate_public_fr: {str(e)}\n{traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'error': f'Erreur serveur: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)


@csrf_exempt
def download_certificate_public_fr(request, pk):
    """
    Générer et télécharger un certificat PDF à la volée
    pk peut être: cert-{cin}-sensibilisation ou cert-{cin}-test-{attempt_id}
    """
    from django.template.loader import render_to_string
    from xhtml2pdf import pisa
    
    try:
        # Parser l'ID du certificat
        # Format: cert::{cin}::sensibilisation ou cert::{cin}::test::{attempt_id}
        if not pk.startswith('cert::'):
            return JsonResponse({'success': False, 'error': 'Format de certificat invalide'}, status=400)
        
        # Enlever le préfixe 'cert::'
        rest = pk[6:]  # 'cert::' = 6 caractères
        
        # Séparer par '::'
        parts = rest.split('::')
        if len(parts) < 2:
            return JsonResponse({'success': False, 'error': 'Format de certificat invalide'}, status=400)
        
        cin = parts[0]
        cert_type = parts[1]
        
        if cert_type == 'sensibilisation':
            attempt_id = None
        elif cert_type == 'test':
            if len(parts) < 3:
                return JsonResponse({'success': False, 'error': 'Format de certificat invalide - ID de tentative manquant'}, status=400)
            attempt_id = parts[2]
        else:
            return JsonResponse({'success': False, 'error': 'Type de certificat invalide'}, status=400)
        
        # Récupérer l'utilisateur HSE
        try:
            hse_user = HSEUser.objects.get(cin__iexact=cin)
        except HSEUser.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Utilisateur non trouvé'}, status=404)
        
        # Générer les données du certificat selon le type
        attempt_obj = None
        if cert_type == 'sensibilisation':
            if not hse_user.sensibilise_avec_succes:
                return JsonResponse({'success': False, 'error': 'Utilisateur non sensibilisé'}, status=403)
            
            certificate_number = f"HSE-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
            issued_date = datetime.now()
            expiry_date = (issued_date + timedelta(days=365)).date()
            test_version = 0
            score = 100
            is_sensibilisation = True
        elif cert_type == 'test' and attempt_id:
            # Certificat basé sur un test
            try:
                from authentication.models import TestUser
                test_user = TestUser.objects.filter(cin__iexact=cin).first()
                if not test_user:
                    return JsonResponse({'success': False, 'error': 'Utilisateur de test non trouvé'}, status=404)
                
                attempt_obj = TestAttempt.objects.get(id=attempt_id, user=test_user, passed=True, etat='test_final')
                
                # Vérifier que completed_at existe
                if not attempt_obj.completed_at:
                    return JsonResponse({'success': False, 'error': 'Tentative de test non complétée'}, status=400)
                
                certificate_number = f"HSE-{attempt_obj.completed_at.strftime('%Y%m%d')}-{attempt_obj.id}"
                issued_date = attempt_obj.completed_at
                expiry_date = (attempt_obj.completed_at + timedelta(days=365)).date()
                test_version = attempt_obj.test.version
                score = int(attempt_obj.overall_score_percentage)
                is_sensibilisation = False
            except TestAttempt.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Tentative de test non trouvée ou non réussie'}, status=404)
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'Erreur: {str(e)}'}, status=400)
        else:
            return JsonResponse({'success': False, 'error': 'Type de certificat invalide'}, status=400)
        
        # Vérifier l'expiration
        if expiry_date < datetime.now().date():
            return JsonResponse({'success': False, 'error': 'Certificat expiré'}, status=410)
        
        # Récupérer les informations de l'utilisateur
        user_nom = hse_user.nom
        user_prenom = hse_user.prénom
        user_entite = hse_user.entite or ""
        user_chef_projet = hse_user.chef_projet_ocp or ""
        
        # Utiliser la date de complétion du test si disponible, sinon la date d'émission
        if attempt_obj and attempt_obj.completed_at:
            test_date = attempt_obj.completed_at.strftime('%d/%m/%Y')
        else:
            test_date = issued_date.strftime('%d/%m/%Y')
        
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
        
        # Générer le PDF
        html_string = render_to_string('certificats/certificate.html', {
            'user_nom': user_nom,
            'user_prenom': user_prenom,
            'user_cin': hse_user.cin,
            'user_entite': user_entite,
            'user_chef_projet': user_chef_projet,
            'test_date': test_date,
            'logo_path': logo_path
        })
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=certificat_{certificate_number}.pdf'
        
        pisa.CreatePDF(html_string, response)
        return response
    except Exception as e:
        import traceback
        logger.error(f"Erreur génération PDF: {str(e)}\n{traceback.format_exc()}")
        return JsonResponse({'success': False, 'error': f'Erreur génération PDF: {str(e)}'}, status=500)
