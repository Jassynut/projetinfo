# Guide de Dépannage - QR Code

## Problème : Le QR code ne fonctionne pas après scan

### Vérifications à faire

#### 1. Vérifier l'URL dans le QR code
- Ouvrez la page "Commencer le test" dans votre navigateur
- L'URL du QR code est affichée sous le code
- Elle doit être : `http://10.24.159.19:3000/test/{versionId}/passer`
- Si elle contient `localhost` ou `127.0.0.1`, c'est le problème

#### 2. Vérifier que le frontend est accessible
Sur votre téléphone (connecté au même Wi-Fi), ouvrez le navigateur et testez :
```
http://10.24.159.19:3000
```

Si la page ne charge pas :
- Vérifiez que le téléphone est sur le même réseau Wi-Fi que votre PC
- Vérifiez le firewall Windows (voir ci-dessous)

#### 3. Vérifier le Firewall Windows

Le firewall Windows peut bloquer les connexions entrantes. Pour autoriser :

**Option A : Via l'interface graphique**
1. Ouvrez "Pare-feu Windows Defender"
2. Cliquez sur "Paramètres avancés"
3. Cliquez sur "Règles de trafic entrant" → "Nouvelle règle"
4. Sélectionnez "Port" → Suivant
5. TCP, ports spécifiques : `3000, 8000` → Suivant
6. Autoriser la connexion → Suivant
7. Cochez tous les profils → Suivant
8. Nom : "HSE App Ports" → Terminer

**Option B : Via PowerShell (en administrateur)**
```powershell
New-NetFirewallRule -DisplayName "HSE App Port 3000" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "HSE App Port 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

#### 4. Vérifier l'IP de votre machine
```powershell
ipconfig
```
Cherchez "IPv4 Address" sous votre connexion Wi-Fi/Ethernet active.
Si ce n'est pas `10.24.159.19`, mettez à jour :
- `docker-compose.yml` : variable `FRONTEND_URL`
- `frontend/src/config.js` : IP par défaut
- `backend/authentication/views.py` : variable d'environnement `FRONTEND_URL`

#### 5. Tester l'accessibilité depuis le téléphone

**Sur Android :**
1. Ouvrez Chrome
2. Tapez : `http://10.24.159.19:3000`
3. La page doit se charger

**Sur iPhone :**
1. Ouvrez Safari
2. Tapez : `http://10.24.159.19:3000`
3. La page doit se charger

#### 6. Vérifier les conteneurs Docker
```powershell
docker-compose ps
```

Tous les conteneurs doivent être "Up" (pas "Restarting")

### Solutions rapides

#### Reconstruire le frontend avec la bonne IP
```powershell
docker-compose down
docker-compose build --no-cache frontend
docker-compose up -d
```

#### Vérifier les logs
```powershell
docker-compose logs frontend
docker-compose logs backend
```

### Test manuel

1. Sur votre PC, ouvrez : http://10.24.159.19:3000
2. Sur votre téléphone (même Wi-Fi), ouvrez : http://10.24.159.19:3000
3. Si les deux fonctionnent, le QR code devrait fonctionner aussi

### Message d'erreur courant

**"Impossible de se connecter" ou "Site inaccessible"**
→ Le firewall bloque les connexions ou le téléphone n'est pas sur le même réseau

**"404 Not Found"**
→ L'URL dans le QR code est incorrecte (vérifiez qu'elle contient bien `/test/{id}/passer`)

**La page charge mais reste blanche**
→ Vérifiez les logs du frontend : `docker-compose logs frontend`

