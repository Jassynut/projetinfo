from django.urls import path
from . import views

urlpatterns = [
    path('download-certificate/<int:user_id>/<int:test_id>/', 
     views.download_certificate, name='download_certificate'),

]
