from django.urls import path
from . import views

urlpatterns = [
    path('hse/', views.hse_dashboard, name='hse_dashboard'),
    path('hse/api/', views.HSEApiView.as_view(), name='hse_api'),
    path('hse/questionnaires/', views.gestion_questionnaires, name='gestion_questionnaires'),
    path('hse/certificats/', views.generation_certificats, name='generation_certificats'),
]
