# Instructions pour réinitialiser les migrations HSE

## ⚠️ ATTENTION
Cette opération va **SUPPRIMER TOUTES LES DONNÉES** des tables `hse_app_hseuser` et `hse_app_hsemanager`.

## Méthode 1 : Script Python (Recommandé)

```bash
# Activer l'environnement virtuel
venv\Scripts\activate

# Exécuter le script
python reset_hse_migrations.py
```

Le script va :
1. Supprimer les fichiers de migration (sauf `__init__.py`)
2. Supprimer les tables de la base de données
3. Créer de nouvelles migrations
4. Appliquer les migrations

## Méthode 2 : Commandes manuelles

### Étape 1 : Supprimer les fichiers de migration
```bash
# Supprimer tous les fichiers .py dans backend/hse_app/migrations/ sauf __init__.py
del backend\hse_app\migrations\*.py
# Puis recréer __init__.py si nécessaire
```

### Étape 2 : Supprimer les tables SQL
Exécuter le fichier `reset_hse_tables.sql` dans votre client MySQL :
```sql
DROP TABLE IF EXISTS hse_app_hseuser CASCADE;
DROP TABLE IF EXISTS hse_app_hsemanager CASCADE;
DELETE FROM django_migrations WHERE app = 'hse_app';
```

Ou via la ligne de commande MySQL :
```bash
mysql -u root -proot hse_database < reset_hse_tables.sql
```

### Étape 3 : Recréer les migrations
```bash
python manage.py makemigrations hse_app
```

### Étape 4 : Appliquer les migrations
```bash
python manage.py migrate hse_app
```

## Méthode 3 : Commandes PowerShell (Windows)

```powershell
# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1

# Supprimer les migrations (sauf __init__.py)
Get-ChildItem backend\hse_app\migrations\*.py | Where-Object { $_.Name -ne '__init__.py' } | Remove-Item

# Supprimer les tables via MySQL
mysql -u root -proot hse_database -e "DROP TABLE IF EXISTS hse_app_hseuser CASCADE; DROP TABLE IF EXISTS hse_app_hsemanager CASCADE; DELETE FROM django_migrations WHERE app = 'hse_app';"

# Recréer les migrations
python manage.py makemigrations hse_app

# Appliquer les migrations
python manage.py migrate hse_app
```

## Vérification

Après l'exécution, vérifiez que :
1. Les nouvelles migrations sont créées dans `backend/hse_app/migrations/`
2. Les tables sont recréées dans la base de données
3. Le modèle correspond aux nouveaux champs (sans email, presence, score, test_user)


