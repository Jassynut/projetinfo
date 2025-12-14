"""
Script pour réinitialiser les migrations de hse_app
ATTENTION: Ce script supprime toutes les données de la table hse_app_hseuser et hse_app_hsemanager
"""
import os
import sys
import django

# Configuration du chemin Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.conf import settings

def reset_migrations():
    """Supprime les migrations et recrée les tables"""
    
    print("=" * 60)
    print("RÉINITIALISATION DES MIGRATIONS HSE_APP")
    print("=" * 60)
    
    # Étape 1: Supprimer les fichiers de migration (sauf __init__.py)
    migrations_dir = os.path.join(BASE_DIR, 'backend', 'hse_app', 'migrations')
    if os.path.exists(migrations_dir):
        print(f"\n1. Suppression des fichiers de migration dans {migrations_dir}...")
        for file in os.listdir(migrations_dir):
            if file.endswith('.py') and file != '__init__.py':
                file_path = os.path.join(migrations_dir, file)
                os.remove(file_path)
                print(f"   ✓ Supprimé: {file}")
    
    # Étape 2: Supprimer les tables de la base de données
    print("\n2. Suppression des tables de la base de données...")
    with connection.cursor() as cursor:
        try:
            # Supprimer les tables si elles existent
            cursor.execute("DROP TABLE IF EXISTS hse_app_hseuser CASCADE;")
            print("   ✓ Table hse_app_hseuser supprimée")
            
            cursor.execute("DROP TABLE IF EXISTS hse_app_hsemanager CASCADE;")
            print("   ✓ Table hse_app_hsemanager supprimée")
            
            # Supprimer les entrées de migration dans django_migrations
            cursor.execute("DELETE FROM django_migrations WHERE app = 'hse_app';")
            print("   ✓ Entrées de migration supprimées de django_migrations")
            
        except Exception as e:
            print(f"   ⚠ Erreur lors de la suppression: {e}")
            print("   (Les tables n'existent peut-être pas encore)")
    
    # Étape 3: Créer les nouvelles migrations
    print("\n3. Création des nouvelles migrations...")
    try:
        # Changer vers le répertoire racine où se trouve manage.py
        original_dir = os.getcwd()
        os.chdir(BASE_DIR)
        
        # Utiliser le bon format pour execute_from_command_line
        execute_from_command_line(['manage.py', 'makemigrations', 'hse_app'])
        print("   ✓ Migrations créées avec succès")
        
        os.chdir(original_dir)
    except Exception as e:
        print(f"   ✗ Erreur lors de la création des migrations: {e}")
        import traceback
        traceback.print_exc()
        if 'original_dir' in locals():
            os.chdir(original_dir)
        return False
    
    # Étape 4: Appliquer les migrations
    print("\n4. Application des migrations...")
    try:
        # Changer vers le répertoire racine où se trouve manage.py
        original_dir = os.getcwd()
        os.chdir(BASE_DIR)
        
        # Utiliser le bon format pour execute_from_command_line
        execute_from_command_line(['manage.py', 'migrate', 'hse_app'])
        print("   ✓ Migrations appliquées avec succès")
        
        os.chdir(original_dir)
    except Exception as e:
        print(f"   ✗ Erreur lors de l'application des migrations: {e}")
        import traceback
        traceback.print_exc()
        if 'original_dir' in locals():
            os.chdir(original_dir)
        return False
    
    print("\n" + "=" * 60)
    print("RÉINITIALISATION TERMINÉE AVEC SUCCÈS!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    response = input("\n⚠️  ATTENTION: Ce script va supprimer TOUTES les données des tables HSEUser et HSEManager.\nVoulez-vous continuer? (oui/non): ")
    
    if response.lower() in ['oui', 'yes', 'o', 'y']:
        reset_migrations()
    else:
        print("Opération annulée.")

