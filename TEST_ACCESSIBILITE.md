# Test d'Accessibilité - Ports 3000 et 8000

## ✅ Statut des Règles Firewall

Les règles de firewall ont été créées avec succès :
- ✅ **HSE App Port 3000** : Activé (Enabled: True)
- ✅ **HSE App Port 8000** : Activé (Enabled: True)

## 🧪 Tests à Effectuer

### Test 1 : Vérifier depuis votre PC

1. **Ouvrez votre navigateur** sur votre PC
2. **Testez l'accès au frontend** :
   - URL : `http://localhost:3000`
   - URL alternative : `http://10.24.159.13:3000`
   - ✅ Si la page se charge → Le frontend est accessible

3. **Testez l'accès au backend** :
   - URL : `http://localhost:8000/api/`
   - URL alternative : `http://10.24.159.13:8000/api/`
   - ✅ Si vous voyez une réponse JSON ou une erreur Django → Le backend est accessible

### Test 2 : Vérifier depuis votre Téléphone (IMPORTANT)

**Prérequis :**
- ✅ Votre téléphone doit être sur le **même réseau Wi-Fi** que votre PC
- ✅ Docker doit être en cours d'exécution (`docker-compose ps`)

**Étapes :**

1. **Vérifiez l'IP de votre PC** :
   ```powershell
   ipconfig
   ```
   Cherchez "IPv4 Address" sous votre connexion Wi-Fi/Ethernet active.
   Notez cette IP (ex: `10.24.159.13`)

2. **Sur votre téléphone** :
   - Ouvrez le navigateur (Chrome, Safari, etc.)
   - Tapez manuellement : `http://10.24.159.13:3000`
   - ✅ Si la page se charge → **Les ports sont ouverts et accessibles !**
   - ❌ Si la page ne charge pas → Voir la section "Dépannage" ci-dessous

3. **Testez le QR code** :
   - Allez sur la page "Commencer le test" sur votre PC
   - Scannez le QR code avec votre téléphone
   - ✅ Si la page du test s'ouvre → **Tout fonctionne !**
   - ❌ Si rien ne se passe → Voir la section "Dépannage" ci-dessous

### Test 3 : Vérifier avec Docker

1. **Vérifiez que Docker est en cours d'exécution** :
   ```powershell
   docker-compose ps
   ```
   Tous les conteneurs doivent être "Up" (pas "Restarting" ou "Exited")

2. **Vérifiez les logs** :
   ```powershell
   docker-compose logs frontend
   docker-compose logs backend
   ```

## 🔍 Dépannage

### Problème : Le téléphone ne peut pas accéder à `http://10.24.159.13:3000`

**Vérifications :**

1. ✅ **Firewall** : Les règles sont créées (déjà fait ✓)
2. ✅ **IP correcte** : Vérifiez avec `ipconfig` que l'IP est bien `10.24.159.13`
3. ✅ **Même réseau** : Téléphone et PC sur le même Wi-Fi
4. ✅ **Docker actif** : `docker-compose ps` montre tous les conteneurs "Up"
5. ⚠️ **Antivirus** : Certains antivirus bloquent aussi les ports (ajoutez une exception)

**Solution si l'IP est différente :**

Si votre IP n'est pas `10.24.159.13`, mettez à jour :
- `docker-compose.yml` : variable `FRONTEND_URL`
- `frontend/src/pages/CommencerTest.jsx` : IP par défaut dans `getFrontendUrl()`

### Problème : "Site inaccessible" ou "Impossible de se connecter"

**Solutions :**

1. **Vérifiez que les conteneurs Docker sont actifs** :
   ```powershell
   docker-compose ps
   ```
   Si un conteneur est "Exited" ou "Restarting", redémarrez :
   ```powershell
   docker-compose restart
   ```

2. **Vérifiez les logs pour les erreurs** :
   ```powershell
   docker-compose logs frontend --tail=50
   docker-compose logs backend --tail=50
   ```

3. **Testez depuis le PC d'abord** :
   - Si `http://localhost:3000` fonctionne sur le PC mais pas depuis le téléphone
   - → Problème de réseau/firewall
   - Si `http://localhost:3000` ne fonctionne pas non plus
   - → Problème avec Docker ou l'application

### Problème : Le QR code scanne mais la page reste blanche

**Vérifications :**

1. **Console du navigateur** (sur le téléphone) :
   - Ouvrez les outils de développement (si possible)
   - Ou utilisez Chrome Remote Debugging
   - Vérifiez les erreurs JavaScript

2. **Logs du frontend** :
   ```powershell
   docker-compose logs frontend --tail=100
   ```

3. **Vérifiez l'URL dans le QR code** :
   - L'URL doit être : `http://10.24.159.13:3000/test/{versionId}/passer`
   - Pas `localhost` ou `127.0.0.1`

## ✅ Checklist de Vérification

Avant de tester le QR code, assurez-vous que :

- [x] Les règles de firewall sont créées et activées
- [ ] Docker est en cours d'exécution (`docker-compose ps`)
- [ ] L'IP de votre PC est correcte (`ipconfig`)
- [ ] Le frontend est accessible depuis le PC (`http://localhost:3000`)
- [ ] Le backend est accessible depuis le PC (`http://localhost:8000/api/`)
- [ ] Le téléphone est sur le même réseau Wi-Fi
- [ ] Le téléphone peut accéder à `http://10.24.159.13:3000` (remplacez par votre IP)

## 🎯 Prochaines Étapes

1. **Testez depuis votre téléphone** : `http://10.24.159.13:3000`
2. **Si ça fonctionne** : Testez le scan du QR code
3. **Si ça ne fonctionne pas** : Suivez la section "Dépannage" ci-dessus

## 📞 Commandes Utiles

```powershell
# Vérifier les règles de firewall
Get-NetFirewallRule -DisplayName "HSE App Port*" | Select-Object DisplayName, Enabled

# Vérifier l'IP de votre PC
ipconfig | findstr "IPv4"

# Vérifier l'état de Docker
docker-compose ps

# Redémarrer les conteneurs
docker-compose restart

# Voir les logs
docker-compose logs -f frontend
docker-compose logs -f backend
```

---

**Les ports sont maintenant ouverts !** 🎉

Testez depuis votre téléphone et dites-moi si ça fonctionne.

