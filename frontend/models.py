from django.db import models

class Agent(models.Model):
    entite = models.CharField(max_length=255)
    entreprise = models.CharField(max_length=255)
    chef_projet_ocp = models.CharField(max_length=255)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    cin = models.CharField(max_length=50, unique=True)  # unique si nécessaire
    email_coordinateur = models.EmailField()
    fonction_agent = models.CharField(max_length=255)
    date_import = models.DateField(auto_now_add=True)  # pour savoir quel jour le fichier a été importé

    def __str__(self):
        return f"{self.nom} {self.prenom}"
