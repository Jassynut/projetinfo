# Guide de Dépannage Docker

## Erreur : "docker client must be run with elevated privileges"

### Solution 1 : Démarrer Docker Desktop
1. Ouvrez **Docker Desktop** depuis le menu Démarrer
2. Attendez que Docker Desktop soit complètement démarré (icône Docker dans la barre des tâches)
3. Vérifiez que l'icône Docker est verte dans la barre des tâches

### Solution 2 : Exécuter avec des privilèges administrateur
1. Fermez votre terminal actuel
2. Cliquez droit sur **PowerShell** ou **Command Prompt**
3. Sélectionnez **"Exécuter en tant qu'administrateur"**
4. Naviguez vers votre projet : `cd C:\Users\Yassmine\Desktop\projetinfo`
5. Relancez les commandes Docker

### Solution 3 : Vérifier que Docker Desktop est en cours d'exécution
```powershell
# Vérifier le statut de Docker
docker info

# Si cela fonctionne, Docker est prêt
# Sinon, démarrez Docker Desktop
```

## Commandes utiles

### Démarrer l'application
```powershell
docker-compose up -d
```

### Voir les logs
```powershell
docker-compose logs -f
```

### Arrêter l'application
```powershell
docker-compose down
```

### Redémarrer un service spécifique
```powershell
docker-compose restart backend
docker-compose restart frontend
```

### Vérifier l'état des conteneurs
```powershell
docker-compose ps
```

## Problèmes courants

### Port déjà utilisé
Si vous obtenez une erreur "port already in use" :
```powershell
# Trouver le processus utilisant le port
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :3306

# Arrêter le processus (remplacez PID par le numéro trouvé)
taskkill /PID <PID> /F
```

### Réinitialiser complètement Docker
```powershell
# ATTENTION : Cela supprime toutes les données !
docker-compose down -v
docker system prune -a
docker-compose up -d --build
```

### Vérifier les logs d'erreur
```powershell
# Logs du backend
docker-compose logs backend

# Logs du frontend
docker-compose logs frontend

# Logs de la base de données
docker-compose logs db
```

## Erreur : "failed to resolve source metadata for docker.io/library/python"

### Problème de connectivité réseau avec Docker Hub

Cette erreur indique que Docker ne peut pas se connecter à Docker Hub pour télécharger les images.

### Solutions :

#### Solution 1 : Vérifier la connexion Internet
```powershell
# Tester la connectivité
ping google.com
ping registry-1.docker.io
```

#### Solution 2 : Configurer un proxy dans Docker Desktop (si vous êtes derrière un proxy)
1. Ouvrez **Docker Desktop**
2. Allez dans **Settings** (Paramètres)
3. Cliquez sur **Resources** → **Proxies**
4. Configurez votre proxy HTTP/HTTPS si nécessaire
5. Cliquez sur **Apply & Restart**

#### Solution 3 : Utiliser un miroir Docker Hub (si Docker Hub est bloqué)
Créez ou modifiez le fichier `C:\Users\<VotreNom>\.docker\daemon.json` :
```json
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
```
Puis redémarrez Docker Desktop.

#### Solution 4 : Vérifier les paramètres DNS
1. Ouvrez **Docker Desktop**
2. Allez dans **Settings** → **Docker Engine**
3. Ajoutez des DNS personnalisés :
```json
{
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```
4. Cliquez sur **Apply & Restart**

#### Solution 5 : Désactiver temporairement le pare-feu/antivirus
- Vérifiez si votre pare-feu Windows ou antivirus bloque Docker
- Ajoutez Docker Desktop aux exceptions du pare-feu

#### Solution 6 : Utiliser une image déjà téléchargée localement
Si vous avez déjà l'image Python sur votre machine :
```powershell
# Vérifier les images locales
docker images | findstr python

# Si l'image existe, le build devrait fonctionner
docker-compose build backend
```

#### Solution 7 : Télécharger l'image manuellement
```powershell
# Essayer de pull l'image directement
docker pull python:3.11-slim

# Si cela fonctionne, relancer le build
docker-compose build backend
```

#### Solution 8 : Utiliser un VPN ou changer de réseau
- Si vous êtes sur un réseau d'entreprise qui bloque Docker Hub, essayez un VPN
- Ou connectez-vous à un autre réseau (WiFi personnel, partage de connexion mobile)

