import openpyxl
from authentication.models import Apprenant

def import_apprenants_from_excel(file):
    wb = openpyxl.load_workbook(file)
    ws = wb.active

    count = 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        nom, prenom, cin, email = row

        Apprenant.objects.get_or_create(
            cin=cin,
            defaults={
                "nom": nom,
                "prenom": prenom,
                "email": email
            }
        )
        count += 1

    return count
