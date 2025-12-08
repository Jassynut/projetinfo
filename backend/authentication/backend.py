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
    """Authentification des utilisateurs HSE via CIN uniquement."""

    def authenticate(self, request, cin=None, **kwargs):
        if cin is None:
            return None
        try:
            user, _created = TestUser.objects.authenticate_hse_user(cin)
            return user
        except Exception:
            return None

    def get_user(self, user_id):
        try:
            return TestUser.objects.get(pk=user_id)
        except TestUser.DoesNotExist:
            return None


class HSEManagerBackend(BaseBackend):
    """Authentification des managers HSE via nom complet + CIN."""

    def authenticate(self, request, full_name=None, cin=None, **kwargs):
        if not full_name or not cin:
            return None
        try:
            return TestUser.objects.authenticate_manager(full_name, cin)
        except Exception:
            return None

    def get_user(self, user_id):
        try:
            return TestUser.objects.get(pk=user_id)
        except TestUser.DoesNotExist:
            return None
