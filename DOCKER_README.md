# Guide de Déploiement Docker - Application HSE

Ce guide explique comment déployer l'application HSE en utilisant Docker.

## Prérequis

- Docker Desktop installé (Windows/Mac) ou Docker Engine (Linux)
- Docker Compose (inclus avec Docker Desktop)
- Au moins 4 Go de RAM disponibles
- Ports 3000, 8000 et 3306 disponibles

## Démarrage Rapide

1. **Cloner ou télécharger le projet** dans un dossier sur votre machine

2. **Ouvrir un terminal** dans le dossier du projet

3. **Lancer l'application** :
   ```bash
   docker-compose up -d
   ```

4. **Accéder à l'application** :
   - Frontend (Interface utilisateur) : http://localhost:3000
   - Backend (API) : http://localhost:8000
   - Admin Django : http://localhost:8000/admin

## Configuration pour les QR Codes

Pour que les apprenants puissent scanner les QR codes depuis leurs téléphones :

1. **Trouver l'adresse IP locale de votre machine** :
   - Windows : Ouvrir CMD et taper `ipconfig`, chercher "IPv4 Address"
   - Mac/Linux : Ouvrir Terminal et taper `ifconfig` ou `ip addr`

2. **Modifier le fichier `docker-compose.yml`** :
   - Remplacer `localhost` par votre IP locale dans la section `frontend` > `environment` > `REACT_APP_API_URL`
   - Exemple : `REACT_APP_API_URL=http://192.168.1.100:8000`

3. **Redémarrer les conteneurs** :
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

## Commandes Utiles

### Démarrer l'application
```bash
docker-compose up -d
```

### Arrêter l'application
```bash
docker-compose down
```

### Voir les logs
```bash
# Tous les services
docker-compose logs -f

# Un service spécifique
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
```

### Redémarrer un service
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Reconstruire les images
```bash
docker-compose build --no-cache
docker-compose up -d
```

### Accéder au shell du backend
```bash
docker-compose exec backend bash
```

### Créer un superutilisateur Django
```bash
docker-compose exec backend python manage.py createsuperuser
```

### Exécuter les migrations
```bash
docker-compose exec backend python manage.py migrate
```

### Collecter les fichiers statiques
```bash
docker-compose exec backend python manage.py collectstatic --noinput
```

## Structure des Services

- **db** : Base de données MySQL (port 3306)
- **backend** : API Django (port 8000)
- **frontend** : Interface React avec Nginx (port 3000)

## Volumes Persistants

Les données suivantes sont sauvegardées dans des volumes Docker :
- Base de données MySQL
- Fichiers statiques Django
- Médias (images, certificats)
- Questions et images HSE

## Dépannage

### Le backend ne démarre pas
```bash
# Vérifier les logs
docker-compose logs backend

# Vérifier que la base de données est prête
docker-compose exec db mysqladmin ping -h localhost -u root -proot_password
```

### Le frontend ne se connecte pas au backend
- Vérifier que le backend est accessible sur http://localhost:8000
- Vérifier les logs : `docker-compose logs frontend`

### Les QR codes ne fonctionnent pas
- Vérifier que l'IP dans `REACT_APP_API_URL` est correcte
- S'assurer que le téléphone est sur le même réseau Wi-Fi
- Vérifier que le firewall n'bloque pas les ports 3000 et 8000

### Réinitialiser complètement
```bash
# ATTENTION : Cela supprimera toutes les données !
docker-compose down -v
docker-compose up -d --build
```

## Accès à l'Application

### Pour les Apprenants
1. Scanner le QR code généré par le gestionnaire
2. Entrer le CIN sur la page de connexion
3. Choisir la langue (FR/AR/EN)
4. Passer le test

### Pour les Gestionnaires
1. Accéder à http://localhost:3000
2. Se connecter avec les identifiants admin
3. Gérer les questions, versions et générer les QR codes

## Support

En cas de problème, vérifier :
1. Les logs Docker : `docker-compose logs`
2. L'état des conteneurs : `docker-compose ps`
3. L'utilisation des ressources : `docker stats`

