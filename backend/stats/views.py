from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json

# Vue pour la page principale
def hse_dashboard(request):
    """
    Vue principale pour le portail HSE
    """
    context = {
        'page_title': 'Induction HSE - Jorf Lasfar',
        'year': 2025
    }
    return render(request, 'hse/stats.html', context)

# API views pour les données
@method_decorator(csrf_exempt, name='dispatch')
class HSEApiView(View):
    """
    Vue API pour gérer les opérations HSE
    """
    
    def get(self, request, *args, **kwargs):
        """
        Récupérer les données HSE (questionnaires, certificats, etc.)
        """
        # Données simulées pour les questionnaires
        questionnaires = [
            {
                'id': 1,
                'titre': 'Test HSE Basique',
                'description': 'Questionnaire de base sur la sécurité',
                'duree': 30,
                'questions_count': 20
            },
            {
                'id': 2,
                'titre': 'Formation Avancée',
                'description': 'Test avancé sur les procédures HSE',
                'duree': 45,
                'questions_count': 30
            }
        ]
        
        return JsonResponse({
            'questionnaires': questionnaires,
            'statistiques': {
                'tests_completes': 0,
                'certificats_generes': 0
            }
        })
    
    def post(self, request, *args, **kwargs):
        """
        Commencer un test ou générer un certificat
        """
        try:
            data = json.loads(request.body)
            action = data.get('action')
            
            if action == 'commencer_test':
                questionnaire_id = data.get('questionnaire_id')
                # Logique pour commencer un test
                return JsonResponse({
                    'success': True,
                    'message': 'Test démarré avec succès',
                    'test_id': f"test_{questionnaire_id}_{request.user.id}"
                })
                
            elif action == 'generer_certificat':
                # Logique pour générer un certificat
                return JsonResponse({
                    'success': True,
                    'message': 'Certificat généré avec succès',
                    'certificat_url': '/certificats/certificat_12345.pdf'
                })
                
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Action non reconnue'
                }, status=400)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Données JSON invalides'
            }, status=400)

# Vue pour la gestion des questionnaires
def gestion_questionnaires(request):
    """
    Vue pour la gestion des questionnaires
    """
    return render(request, 'hse/gestion_questionnaires.html')

# Vue pour la génération de certificats
def generation_certificats(request):
    """
    Vue pour la génération de certificats
    """
    return render(request, 'hse/generation_certificats.html')
