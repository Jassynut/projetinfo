from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from authentication.models import TestUser
from tests.models import TestAttempt

def download_certificate(request, user_id, test_id):
    try:
        user = TestUser.objects.get(id=user_id)
        attempt = TestAttempt.objects.get(user=user, test_id=test_id)

        html_string = render_to_string('certificate.html', {
            'full_name': user.get_full_name(),
            'score': attempt.overall_score_percentage,
            'total': 100,  # ou le total réel du test
            'custom_text': "Félicitations pour votre réussite au test HSE !"
        })

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=certificat_{user.username}.pdf'

        HTML(string=html_string).write_pdf(response)
        return response

    except TestUser.DoesNotExist:
        return HttpResponse("Utilisateur non trouvé", status=404)
    except TestAttempt.DoesNotExist:
        return HttpResponse("Tentative de test non trouvée", status=404)
