# Test du QR Code - Guide Rapide

## ✅ Vérifications avant de scanner

### 1. Vérifier que les services sont actifs
```powershell
docker-compose ps
```
Tous les conteneurs doivent être "Up" (pas "Restarting")

### 2. Vérifier l'URL du QR code
1. Ouvrez votre navigateur sur : `http://localhost:3000` (ou `http://10.24.159.19:3000`)
2. Allez sur la page "Commencer le test"
3. **L'URL affichée sous le QR code doit être** : `http://10.24.159.19:3000/test/{versionId}/passer`
4. Ouvrez la console du navigateur (F12) pour voir les logs de débogage

### 3. Tester l'accessibilité depuis votre téléphone

**IMPORTANT** : Votre téléphone doit être sur le **même réseau Wi-Fi** que votre PC.

1. Sur votre téléphone, ouvrez le navigateur (Chrome/Safari)
2. Tapez manuellement : `http://10.24.159.19:3000`
3. Si la page se charge → ✅ Le réseau fonctionne
4. Si la page ne charge pas → ❌ Vérifiez le firewall (voir ci-dessous)

### 4. Autoriser le Firewall Windows

Le firewall peut bloquer les connexions. Exécutez cette commande dans PowerShell **en tant qu'administrateur** :

```powershell
New-NetFirewallRule -DisplayName "HSE App Port 3000" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "HSE App Port 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### 5. Scanner le QR code

1. Ouvrez l'application de scan QR de votre téléphone (appareil photo, Google Lens, etc.)
2. Scannez le QR code affiché sur l'écran
3. Le téléphone doit ouvrir l'URL dans le navigateur
4. Vous devriez voir la page de connexion avec le champ CIN

## 🔍 Dépannage

### Problème : "Site inaccessible" ou "Impossible de se connecter"
- ✅ Vérifiez que le téléphone est sur le même Wi-Fi
- ✅ Vérifiez le firewall Windows
- ✅ Vérifiez que l'IP `10.24.159.19` est correcte (exécutez `ipconfig`)

### Problème : "404 Not Found"
- ✅ Vérifiez que l'URL dans le QR code contient bien `/test/{versionId}/passer`
- ✅ Vérifiez que vous avez bien sélectionné une version de test

### Problème : La page charge mais reste blanche
- ✅ Vérifiez les logs du frontend : `docker-compose logs frontend`
- ✅ Vérifiez la console du navigateur sur le téléphone (F12)

### Problème : Le QR code ne s'affiche pas
- ✅ Vérifiez que vous avez sélectionné une version de test
- ✅ Vérifiez la console du navigateur pour les erreurs

## 📱 Test manuel de l'URL

Pour tester sans scanner, copiez l'URL affichée sous le QR code et collez-la dans le navigateur de votre téléphone.

L'URL devrait ressembler à :
```
http://10.24.159.19:3000/test/1/passer
```

Remplacez `1` par l'ID de votre version de test.

