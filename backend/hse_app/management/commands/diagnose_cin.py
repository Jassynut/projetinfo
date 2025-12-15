from django.core.management.base import BaseCommand
from hse_app.models import HSEUser
import sys

class Command(BaseCommand):
    help = 'Diagnostiquer la recherche de CIN dans la base de données'

    def add_arguments(self, parser):
        parser.add_argument('cin', type=str, help='CIN à rechercher')

    def handle(self, *args, **options):
        cin_to_search = options['cin'].strip().upper()
        cin_normalized = cin_to_search.replace(' ', '').replace('-', '').replace('_', '').strip()
        
        self.stdout.write(f"\n=== Diagnostic CIN ===")
        self.stdout.write(f"CIN recherché (original): '{cin_to_search}'")
        self.stdout.write(f"CIN recherché (normalisé): '{cin_normalized}'")
        self.stdout.write(f"\n=== Recherche dans la base ===")
        
        # 1. Recherche exacte
        try:
            user = HSEUser.objects.get(cin=cin_to_search)
            self.stdout.write(self.style.SUCCESS(f"✓ Trouvé avec recherche exacte: {user.cin}"))
            self.stdout.write(f"  ID: {user.id}, Nom: {user.nom} {user.prénom}")
            return
        except HSEUser.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"✗ Non trouvé avec recherche exacte"))
        
        # 2. Recherche insensible à la casse
        try:
            user = HSEUser.objects.get(cin__iexact=cin_to_search)
            self.stdout.write(self.style.SUCCESS(f"✓ Trouvé avec recherche insensible à la casse: {user.cin}"))
            self.stdout.write(f"  ID: {user.id}, Nom: {user.nom} {user.prénom}")
            return
        except HSEUser.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"✗ Non trouvé avec recherche insensible à la casse"))
        
        # 3. Recherche avec normalisation
        all_users = HSEUser.objects.all()
        found = False
        for u in all_users:
            db_cin = str(u.cin)
            db_cin_normalized = db_cin.replace(' ', '').replace('-', '').replace('_', '').strip().upper()
            if db_cin_normalized == cin_normalized:
                self.stdout.write(self.style.SUCCESS(f"✓ Trouvé avec normalisation: {u.cin}"))
                self.stdout.write(f"  ID: {u.id}, Nom: {u.nom} {u.prénom}")
                self.stdout.write(f"  CIN en base (original): '{db_cin}'")
                self.stdout.write(f"  CIN en base (normalisé): '{db_cin_normalized}'")
                found = True
                break
        
        if not found:
            self.stdout.write(self.style.ERROR(f"✗ CIN non trouvé avec toutes les méthodes"))
            self.stdout.write(f"\n=== Exemples de CIN dans la base ===")
            sample_users = HSEUser.objects.all()[:10]
            for u in sample_users:
                self.stdout.write(f"  - '{u.cin}' (ID: {u.id}, {u.nom} {u.prénom})")
            
            # Chercher des CIN similaires
            self.stdout.write(f"\n=== CIN similaires (contenant '{cin_normalized[:3]}') ===")
            similar = HSEUser.objects.filter(cin__icontains=cin_normalized[:3])[:5]
            for u in similar:
                self.stdout.write(f"  - '{u.cin}' (ID: {u.id})")

