#!/usr/bin/env python
"""
Script pour ajouter un manager HSE dans la base de données
"""
import os
import sys
import django

# Configuration de l'environnement Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from hse_app.models import HSEManager
from authentication.models import TestUser, TestUserManager

def add_manager():
    full_name = "yassmine aalla"
    cin = "V389500"
    
    try:
        # Vérifier si le manager existe déjà dans HSEManager
        manager, created = HSEManager.objects.get_or_create(
            cin=cin.upper(),
            defaults={'full_name': full_name}
        )
        
        if created:
            print(f"✅ Manager HSEManager créé: {manager.full_name} ({manager.cin})")
        else:
            # Mettre à jour le nom si le manager existe déjà
            manager.full_name = full_name
            manager.save()
            print(f"✅ Manager HSEManager mis à jour: {manager.full_name} ({manager.cin})")
        
        # Créer aussi le TestUser correspondant pour l'authentification
        user_manager = TestUserManager()
        try:
            test_user = TestUser.objects.get(cin=cin.upper(), user_type='manager')
            print(f"ℹ️  TestUser existe déjà: {test_user.full_name} ({test_user.cin})")
        except TestUser.DoesNotExist:
            test_user = user_manager.create_manager(cin=cin.upper(), full_name=full_name)
            print(f"✅ TestUser créé: {test_user.full_name} ({test_user.cin})")
        
        print(f"\n✅ Manager prêt pour la connexion:")
        print(f"   Nom complet: {full_name}")
        print(f"   CIN: {cin.upper()}")
        
        return manager
    except Exception as e:
        import traceback
        print(f"❌ Erreur lors de l'ajout du manager: {str(e)}")
        print(traceback.format_exc())
        return None

if __name__ == '__main__':
    add_manager()

