from django.contrib.auth.backends import BaseBackend
from authentication.models import TestUser


class HSEUserBackend(BaseBackend):
    """Auth HSE User: CIN uniquement"""

    def authenticate(self, request, cin=None, **kwargs):
        if cin is None:
            return None

        try:
            # Chercher un user existant
            user = TestUser.objects.get(cin=cin, user_type='user')
            return user
        except TestUser.DoesNotExist:
            # Auto-créer depuis HSEUser
            try:
                from hse_app.models import HSEUser
                hse_user = HSEUser.objects.get(cin=cin)
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
    """Auth Manager: full_name + CIN comme mot de passe"""

    def authenticate(self, request, full_name=None, cin=None, **kwargs):
        if full_name is None or cin is None:
            return None

        try:
            # Chercher manager existant dans TestUser
            user = TestUser.objects.get(
                full_name__iexact=full_name.strip(),
                user_type='manager'
            )
            if user.check_password(cin):
                return user
            return None
        except TestUser.DoesNotExist:
            # Auto-créer depuis HSEmanager
            try:
                from hse_app.models import HSEmanager
                manager = HSEmanager.objects.get(
                    full_name__iexact=full_name.strip(),
                    cin=cin
                )
                # Créer dans TestUser avec CIN comme mot de passe
                return TestUser.objects.create_manager(
                    cin=manager.cin,
                    full_name=manager.full_name
                )
            except Exception as e:
                print(f"[DEBUG] Erreur création manager: {e}")
                return None

    def get_user(self, user_id):
        try:
            return TestUser.objects.get(pk=user_id)
        except TestUser.DoesNotExist:
            return None