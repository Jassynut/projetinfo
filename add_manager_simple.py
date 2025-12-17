"""
Script simple pour ajouter un manager - À exécuter dans le shell Django
Copiez-collez ce code dans le shell Django
"""
from hse_app.models import HSEManager
from authentication.models import TestUser, TestUserManager

full_name = "yassmine aalla"
cin = "V389500"

# Créer le HSEManager
manager, created = HSEManager.objects.get_or_create(
    cin=cin.upper(),
    defaults={'full_name': full_name}
)
if created:
    print(f"✅ HSEManager créé: {manager.full_name} ({manager.cin})")
else:
    manager.full_name = full_name
    manager.save()
    print(f"✅ HSEManager mis à jour: {manager.full_name} ({manager.cin})")

# Créer le TestUser pour l'authentification
user_manager = TestUserManager()
try:
    test_user = TestUser.objects.get(cin=cin.upper(), user_type='manager')
    print(f"ℹ️  TestUser existe déjà: {test_user.full_name} ({test_user.cin})")
except TestUser.DoesNotExist:
    test_user = user_manager.create_manager(cin=cin.upper(), full_name=full_name)
    print(f"✅ TestUser créé: {test_user.full_name} ({test_user.cin})")

print(f"\n✅ Manager prêt pour la connexion!")
print(f"   Nom complet: {full_name}")
print(f"   CIN: {cin.upper()}")

