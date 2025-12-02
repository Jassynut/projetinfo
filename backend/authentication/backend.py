from django.contrib.auth.backends import BaseBackend
from .models import TestUser


class HSEUserBackend(BaseBackend):
    """
    Authentification pour les utilisateurs HSE.
    UN SEUL CHAMP: CIN (après scan QR).
    """

    def authenticate(self, request, cin=None, **kwargs):
        if cin is None:
            return None

        try:
            user = TestUser.objects.get(cin=cin, user_type='user')
            return user
        except TestUser.DoesNotExist:
            # Auto-créer depuis HSEUser si existe
            try:
                from hse_app.models import HSEUser as HSEUserModel
                hse_user = HSEUserModel.objects.get(cin=cin)
                return TestUser.objects.create_hse_user(
                    cin=cin,
                    full_name=hse_user.full_name
                )
            except Exception:
                return None

    def get_user(self, user_id):
        try:
            return TestUser.objects.get(pk=user_id)
        except TestUser.DoesNotExist:
            return None


class HSEManagerBackend(BaseBackend):
    """
    Authentification pour les managers HSE.
    - Username: full_name
    - Mot de passe: CIN
    """

    def authenticate(self, request, full_name=None, cin=None, **kwargs):
        if full_name is None or cin is None:
            return None

        try:
            user = TestUser.objects.get(
                full_name__iexact=full_name.strip(),
                user_type='manager'
            )
            if user.check_password(cin):
                return user
            return None
        except TestUser.DoesNotExist:
            # Auto-créer depuis HSEManager si existe
            try:
                from hse_app.models import HSEManager as HSEManagerModel
                manager = HSEManagerModel.objects.get(
                    full_name__iexact=full_name.strip(),
                    cin=cin
                )
                return TestUser.objects.create_manager(
                    cin=cin,
                    full_name=manager.full_name
                )
            except Exception:
                return None

    def get_user(self, user_id):
        try:
            return TestUser.objects.get(pk=user_id)
        except TestUser.DoesNotExist:
            return None