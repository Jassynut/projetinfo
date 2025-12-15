from django.contrib.auth.backends import BaseBackend
from authentication.models import TestUser


class AdminBackend(BaseBackend):
    """Auth pour /admin : username + password"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            user = TestUser.objects.get(username=username)
            if user.check_password(password) and user.is_staff:
                return user
            return None
        except TestUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return TestUser.objects.get(pk=user_id)
        except TestUser.DoesNotExist:
            return None


class HSEUserBackend(BaseBackend):
    """Authentification des utilisateurs HSE via CIN uniquement depuis la table HSEUser."""

    def authenticate(self, request, cin=None, **kwargs):
        if cin is None:
            return None
        try:
            from hse_app.models import HSEUser
            # Vérifier que le CIN existe dans la table HSEUser
            hse_user = HSEUser.objects.get(cin=cin.strip().upper())
            # Créer ou récupérer le TestUser correspondant pour la session Django
            user, _created = TestUser.objects.get_or_create(
                cin=hse_user.cin,
                user_type='user',
                defaults={
                    'username': f"user_{hse_user.cin}",
                    'full_name': hse_user.get_full_name(),
                    'is_staff': False
                }
            )
            # Mettre à jour le nom complet si nécessaire
            if not _created and user.full_name != hse_user.get_full_name():
                user.full_name = hse_user.get_full_name()
                user.save()
            return user
        except Exception:
            return None

    def get_user(self, user_id):
        try:
            return TestUser.objects.get(pk=user_id)
        except TestUser.DoesNotExist:
            return None


class HSEManagerBackend(BaseBackend):
    """Authentification des managers HSE via nom complet + CIN depuis la table HSEManager."""

    def authenticate(self, request, full_name=None, cin=None, **kwargs):
        if not full_name or not cin:
            return None
        try:
            from hse_app.models import HSEManager
            # Vérifier dans la table HSEManager directement
            manager = HSEManager.objects.get(
                full_name__iexact=full_name.strip(),
                cin=cin.strip().upper()
            )
            # Créer ou récupérer le TestUser correspondant pour la session Django
            user, _created = TestUser.objects.get_or_create(
                cin=manager.cin,
                user_type='manager',
                defaults={
                    'username': manager.full_name.lower().replace(' ', '_'),
                    'full_name': manager.full_name,
                    'is_staff': True
                }
            )
            # Mettre à jour le mot de passe avec le CIN
            if not user.has_usable_password() or _created:
                user.set_password(manager.cin)
                user.save()
            # Vérifier que le mot de passe correspond au CIN
            if user.check_password(manager.cin):
                return user
            return None
        except Exception:
            return None

    def get_user(self, user_id):
        try:
            return TestUser.objects.get(pk=user_id)
        except TestUser.DoesNotExist:
            return None
