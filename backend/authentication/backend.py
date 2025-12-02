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
    """Auth HSE User: CIN uniquement"""
    # ... ton code existant ...


class HSEManagerBackend(BaseBackend):
    """Auth Manager: full_name + cin"""
    # ... ton code existant ...