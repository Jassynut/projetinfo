from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('api/', views.accueil_api, name='accueil_api'),
]