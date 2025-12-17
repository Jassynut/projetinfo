#!/usr/bin/env python
"""
Script pour ajouter un manager HSE dans la base de données
"""
import os
import sys
import django

# Configuration de l'environnement Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from hse_app.models import HSEManager

def add_manager():
    full_name = "yassmine aalla"
    cin = "V389500"
    
    try:
        # Vérifier si le manager existe déjà
        manager, created = HSEManager.objects.get_or_create(
            cin=cin.upper(),
            defaults={'full_name': full_name}
        )
        
        if created:
            print(f"✅ Manager créé avec succès: {manager.full_name} ({manager.cin})")
        else:
            # Mettre à jour le nom si le manager existe déjà
            manager.full_name = full_name
            manager.save()
            print(f"✅ Manager mis à jour: {manager.full_name} ({manager.cin})")
        
        return manager
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout du manager: {str(e)}")
        return None

if __name__ == '__main__':
    add_manager()

