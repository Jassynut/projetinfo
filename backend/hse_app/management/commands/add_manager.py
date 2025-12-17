"""
Commande Django pour ajouter un manager HSE
Usage: python manage.py add_manager "yassmine aalla" "V389500"
"""
from django.core.management.base import BaseCommand
from hse_app.models import HSEManager
from authentication.models import TestUser, TestUserManager


class Command(BaseCommand):
    help = 'Ajouter un manager HSE dans la base de données'

    def add_arguments(self, parser):
        parser.add_argument('full_name', type=str, help='Nom complet du manager')
        parser.add_argument('cin', type=str, help='CIN du manager')

    def handle(self, *args, **options):
        full_name = options['full_name']
        cin = options['cin'].upper()
        
        try:
            # Créer ou mettre à jour le HSEManager
            manager, created = HSEManager.objects.get_or_create(
                cin=cin,
                defaults={'full_name': full_name}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ HSEManager créé: {manager.full_name} ({manager.cin})')
                )
            else:
                manager.full_name = full_name
                manager.save()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ HSEManager mis à jour: {manager.full_name} ({manager.cin})')
                )
            
            # Créer ou mettre à jour le TestUser pour l'authentification
            try:
                test_user = TestUser.objects.get(cin=cin, user_type='manager')
                # Mettre à jour le full_name si nécessaire
                if test_user.full_name != full_name:
                    test_user.full_name = full_name
                    test_user.set_password(cin)  # Réinitialiser le mot de passe
                    test_user.save()
                    self.stdout.write(
                        self.style.WARNING(f'ℹ️  TestUser mis à jour: {test_user.full_name} ({test_user.cin})')
                    )
                else:
                    # S'assurer que le mot de passe est correct
                    test_user.set_password(cin)
                    test_user.save()
                    self.stdout.write(
                        self.style.WARNING(f'ℹ️  TestUser existe déjà: {test_user.full_name} ({test_user.cin})')
                    )
            except TestUser.DoesNotExist:
                # Créer le TestUser manuellement en utilisant le manager avec le modèle
                user_manager = TestUserManager()
                user_manager.model = TestUser  # Définir le modèle explicitement
                test_user = user_manager.create_manager(cin=cin, full_name=full_name)
                self.stdout.write(
                    self.style.SUCCESS(f'✅ TestUser créé: {test_user.full_name} ({test_user.cin})')
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Manager prêt pour la connexion!')
            )
            self.stdout.write(f'   Nom complet: {full_name}')
            self.stdout.write(f'   CIN: {cin}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur: {str(e)}')
            )
            import traceback
            self.stdout.write(traceback.format_exc())

