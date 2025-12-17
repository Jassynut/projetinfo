# 🔧 Résolution de l'erreur de build Docker

## Problème
Erreur lors du build : `failed to resolve source metadata for docker.io/library/python:3.11-slim`

## Solutions par ordre de priorité

### ✅ Solution 1 : Démarrer Docker Desktop (OBLIGATOIRE)

1. **Ouvrez Docker Desktop** depuis le menu Démarrer Windows
2. **Attendez** que Docker Desktop soit complètement démarré
   - L'icône Docker dans la barre des tâches doit être **verte** (pas orange/rouge)
   - Cela peut prendre 1-2 minutes
3. **Vérifiez** que Docker fonctionne :
   ```powershell
   docker info
   ```
   Si cela fonctionne, vous verrez des informations sur Docker.

### ✅ Solution 2 : Vérifier la connexion Internet

```powershell
# Tester la connexion
ping google.com
ping registry-1.docker.io
```

Si le ping échoue, vous avez un problème de connexion réseau.

### ✅ Solution 3 : Configurer un proxy (si vous êtes derrière un proxy d'entreprise)

1. Ouvrez **Docker Desktop**
2. Cliquez sur l'icône ⚙️ **Settings** (Paramètres)
3. Allez dans **Resources** → **Proxies**
4. Activez **Manual proxy configuration**
5. Entrez les informations de votre proxy :
   - **HTTP proxy** : `http://proxy.example.com:8080`
   - **HTTPS proxy** : `http://proxy.example.com:8080`
   - **No proxy for** : `localhost,127.0.0.1`
6. Cliquez sur **Apply & Restart**
7. Attendez que Docker redémarre

### ✅ Solution 4 : Configurer des DNS personnalisés

1. Ouvrez **Docker Desktop**
2. Cliquez sur ⚙️ **Settings** → **Docker Engine**
3. Ajoutez/modifiez la configuration JSON :
   ```json
   {
     "dns": ["8.8.8.8", "8.8.4.4", "1.1.1.1"]
   }
   ```
4. Cliquez sur **Apply & Restart**

### ✅ Solution 5 : Utiliser un miroir Docker Hub (si Docker Hub est bloqué)

1. Ouvrez **Docker Desktop**
2. Cliquez sur ⚙️ **Settings** → **Docker Engine**
3. Ajoutez/modifiez la configuration JSON :
   ```json
   {
     "registry-mirrors": [
       "https://docker.mirrors.ustc.edu.cn",
       "https://hub-mirror.c.163.com"
     ]
   }
   ```
4. Cliquez sur **Apply & Restart**

### ✅ Solution 6 : Vérifier le pare-feu Windows

1. Ouvrez **Pare-feu Windows Defender**
2. Vérifiez que **Docker Desktop** est autorisé
3. Si nécessaire, ajoutez une exception pour Docker Desktop

### ✅ Solution 7 : Télécharger l'image manuellement

Une fois Docker Desktop démarré et la connexion OK :

```powershell
# Télécharger l'image Python
docker pull python:3.11-slim

# Si cela fonctionne, relancer le build
docker-compose build backend
```

### ✅ Solution 8 : Utiliser un autre réseau

- Si vous êtes sur un réseau d'entreprise qui bloque Docker Hub :
  - Connectez-vous à un réseau WiFi personnel
  - Ou utilisez le partage de connexion de votre téléphone
  - Ou utilisez un VPN

## Étapes de vérification

Après avoir appliqué une solution, vérifiez :

```powershell
# 1. Vérifier que Docker fonctionne
docker info

# 2. Tester le téléchargement d'une image
docker pull hello-world

# 3. Si cela fonctionne, relancer le build
docker-compose build backend
```

## Si rien ne fonctionne

1. **Redémarrez Docker Desktop** complètement :
   - Clic droit sur l'icône Docker → **Quit Docker Desktop**
   - Attendez 10 secondes
   - Relancez Docker Desktop

2. **Redémarrez votre ordinateur**

3. **Vérifiez les logs Docker Desktop** :
   - Clic droit sur l'icône Docker → **Troubleshoot**

## Commandes utiles

```powershell
# Vérifier le statut de Docker
docker info

# Voir les images téléchargées
docker images

# Nettoyer le cache Docker
docker system prune -a

# Relancer le build
docker-compose build backend

# Build et démarrer tous les services
docker-compose up -d --build
```

