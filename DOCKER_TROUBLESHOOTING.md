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

