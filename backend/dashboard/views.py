from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def accueil_api(request):
    """API qui renvoie les données du dashboard"""
    return JsonResponse({
        'message': 'Bienvenue sur la plateforme HSE',
        'liens_rapides': [
            {
                'titre': 'Gestion des questionnaires',
                'description': 'Créez et gérez vos tests HSE',
                'url': '/api/tests/gestion/',
                'icone': '📋'
            },
            {
                'titre': 'Commencer le test', 
                'description': 'Passez un examen de certification',
                'url': '/api/tests/choisir/',
                'icone': '🎯'
            },
            {
                'titre': 'Générer un certificat',
                'description': 'Téléchargez vos attestations',
                'url': '/api/certificats/',
                'icone': '📄'
            },
            {
                'titre': 'Base de donnée',
                'description': 'Gérer la base des utilisateurs',
                'url': '/api/certificats/',
                'icone': '📄'
            },
            {
                'titre': 'Tableau de bord',
                'description': 'Statistiques',
                'url': '/api/certificats/',
                'icone': '📄'
            }

        ]
    })
