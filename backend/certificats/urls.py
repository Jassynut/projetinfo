from django.urls import path
from . import views

urlpatterns = [
    # Ancien endpoint (toujours supporté)
    path('download-certificate/<int:user_id>/<int:test_id>/', 
         views.download_certificate, name='download_certificate'),
    
    # Nouveaux endpoints
    path('generate/<int:attempt_id>/', 
         views.generate_certificate, name='generate_certificate'),
    path('<uuid:certificate_id>/download/', 
         views.download_certificate_by_id, name='download_certificate_by_id'),
    path('search/', 
         views.search_certificate_by_name, name='search_certificate'),
]
