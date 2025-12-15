from django.core.management.base import BaseCommand
from hse_app.models import HSEUser

class Command(BaseCommand):
    help = 'Lister tous les CIN dans la base de données'

    def add_arguments(self, parser):
        parser.add_argument('--limit', type=int, default=50, help='Nombre maximum de CIN à afficher')

    def handle(self, *args, **options):
        limit = options['limit']
        users = HSEUser.objects.all()[:limit]
        total = HSEUser.objects.count()
        
        self.stdout.write(f"\n=== Liste des CIN dans la base de données ===")
        self.stdout.write(f"Total: {total} utilisateurs (affichage des {min(limit, total)} premiers)\n")
        
        for u in users:
            cin_normalized = str(u.cin).replace(' ', '').replace('-', '').replace('_', '').strip().upper()
            self.stdout.write(f"  CIN: '{u.cin}' (normalisé: '{cin_normalized}') | ID: {u.id} | {u.nom} {u.prénom}")

