#!/usr/bin/env python
"""
Script pour vérifier les managers dans la base de données
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from hse_app.models import HSEManager
from authentication.models import TestUser

print("=== Managers HSEManager ===")
for manager in HSEManager.objects.all():
    print(f"  - {manager.full_name} ({manager.cin})")

print("\n=== Managers TestUser ===")
for user in TestUser.objects.filter(user_type='manager'):
    print(f"  - {user.full_name} ({user.cin}) - username: {user.username}")

print("\n=== Recherche spécifique ===")
cin = "V389500"
full_name = "yassmine aalla"

try:
    hse_mgr = HSEManager.objects.get(cin=cin.upper())
    print(f"✅ HSEManager trouvé: {hse_mgr.full_name} ({hse_mgr.cin})")
except HSEManager.DoesNotExist:
    print(f"❌ HSEManager non trouvé pour CIN: {cin}")

try:
    test_user = TestUser.objects.get(cin=cin.upper(), user_type='manager')
    print(f"✅ TestUser trouvé: {test_user.full_name} ({test_user.cin})")
    print(f"   Username: {test_user.username}")
    print(f"   Password usable: {test_user.has_usable_password()}")
except TestUser.DoesNotExist:
    print(f"❌ TestUser non trouvé pour CIN: {cin}")

