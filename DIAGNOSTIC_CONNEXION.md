# Diagnostic et Correction - ERR_CONNECTION_TIMED_OUT

## Problème
Le frontend React (localhost:3000 ou 10.24.159.13:3000) ne peut pas se connecter au backend Django (10.24.159.13:8000) avec l'erreur `ERR_CONNECTION_TIMED_OUT`.

## Solution Appliquée

### 1. Configuration Nginx (nginx.conf)
Le frontend utilise nginx comme proxy pour toutes les requêtes vers le backend. Toutes les routes sont proxifiées vers le service Docker `backend:8000`.

**Routes proxifiées :**
- `/api/*` → `http://backend:8000/api/*`
- `/manager/*` → `http://backend:8000/manager/*`
- `/user/*` → `http://backend:8000/user/*`
- `/logout/*` → `http://backend:8000/logout/*`
- `/static/*` → `http://backend:8000/static/*`
- `/media/*` → `http://backend:8000/media/*`

### 2. Configuration Frontend (frontend/src/config.js)
Le frontend utilise maintenant le même hostname et port que celui utilisé pour accéder à l'application. Les requêtes sont faites relativement au frontend, et nginx les proxifie automatiquement vers le backend.

**Avant (❌):**
```javascript
return 'http://10.24.159.13:8000';  // Tentative de connexion directe
```

**Après (✅):**
```javascript
const baseUrl = `${protocol}//${hostname}${port ? ':' + port : ''}`;
return baseUrl;  // Utilise le proxy nginx
```

### 3. Configuration CORS Django (backend/settings.py)
Les origines suivantes sont autorisées :
- `http://localhost:3000`
- `http://127.0.0.1:3000`
- `http://10.24.159.13:3000`
- `http://localhost:80` (nginx dans Docker)
- `http://frontend:80` (service Docker frontend)

## Architecture Docker

```
Browser → http://10.24.159.13:3000 (ou localhost:3000)
         ↓
    [Nginx Frontend Container]
         ↓ (proxy)
    [Django Backend Container] → http://backend:8000
         ↓
    [MySQL Container]
```

## Étapes pour Appliquer les Corrections

1. **Reconstruire le frontend avec la nouvelle configuration nginx :**
   ```bash
   docker-compose build frontend
   ```

2. **Redémarrer les services :**
   ```bash
   docker-compose up -d
   ```

3. **Vérifier que les containers sont en cours d'exécution :**
   ```bash
   docker-compose ps
   ```

4. **Vérifier les logs du backend :**
   ```bash
   docker logs hse_backend --tail=50
   ```

5. **Vérifier les logs du frontend :**
   ```bash
   docker logs hse_frontend --tail=50
   ```

6. **Tester la connexion :**
   - Accéder à `http://localhost:3000` ou `http://10.24.159.13:3000`
   - Essayer de se connecter comme manager
   - Vérifier dans la console du navigateur (F12) que les requêtes passent bien par nginx

## Vérifications Complémentaires

### Si le problème persiste :

1. **Vérifier que les containers sont sur le même réseau :**
   ```bash
   docker network inspect projetinfo_hse_network
   ```
   Les containers `hse_backend` et `hse_frontend` doivent être dans la même liste.

2. **Tester la communication entre containers :**
   ```bash
   docker exec hse_frontend ping -c 2 backend
   ```

3. **Vérifier que nginx proxifie correctement :**
   ```bash
   docker exec hse_frontend curl -I http://backend:8000/api/
   ```

4. **Vérifier les logs nginx :**
   ```bash
   docker exec hse_frontend cat /var/log/nginx/error.log
   ```

## Points Importants

- ❌ **Ne pas** utiliser directement `http://10.24.159.13:8000` depuis le frontend
- ✅ **Utiliser** le même hostname/port que le frontend (nginx proxifie automatiquement)
- ✅ Les requêtes `/api/*` et `/manager/login/` passent par nginx
- ✅ Les containers communiquent via le réseau Docker `hse_network` avec les noms de service (`backend`, `frontend`)

