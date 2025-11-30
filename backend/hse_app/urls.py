from django.urls import path
from . import views

urlpatterns = [
    # Exemple : une route qui appelle une view
    path('', views.home, name='hse_home'),
    # tu peux ajouter d'autres routes ici
    # path('liste/', views.liste, name='hse_liste'),
]
