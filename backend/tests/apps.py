from django.apps import AppConfig

class TestsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.tests'
    verbose_name = "Tests"
