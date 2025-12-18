# Guide : Vérifier et Ouvrir les Ports 3000 et 8000 dans le Firewall Windows

## 🔍 Méthode 1 : Vérification Rapide (PowerShell)

### Vérifier si les ports sont ouverts

Ouvrez PowerShell **en tant qu'administrateur** et exécutez :

```powershell
# Vérifier les règles pour le port 3000
Get-NetFirewallPortFilter | Where-Object {$_.LocalPort -eq 3000} | Get-NetFirewallRule | Select-Object DisplayName, Enabled, Direction, Action

# Vérifier les règles pour le port 8000
Get-NetFirewallPortFilter | Where-Object {$_.LocalPort -eq 8000} | Get-NetFirewallRule | Select-Object DisplayName, Enabled, Direction, Action
```

**Résultat attendu :**
- Si vous voyez des règles avec `Enabled = True` → ✅ Les ports sont ouverts
- Si vous ne voyez rien ou `Enabled = False` → ❌ Les ports sont fermés

### Ouvrir les ports (si fermés)

Exécutez ces commandes dans PowerShell **en tant qu'administrateur** :

```powershell
# Port 3000 (Frontend)
New-NetFirewallRule -DisplayName "HSE App Port 3000" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow -Profile Any

# Port 8000 (Backend)
New-NetFirewallRule -DisplayName "HSE App Port 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow -Profile Any
```

### Vérifier après création

```powershell
Get-NetFirewallRule -DisplayName "HSE App Port*" | Select-Object DisplayName, Enabled, Direction, Action
```

---

## 🖱️ Méthode 2 : Interface Graphique (Recommandé)

### Étape 1 : Ouvrir le Pare-feu Windows

1. Appuyez sur `Windows + R`
2. Tapez : `wf.msc` et appuyez sur Entrée
3. Ou recherchez "Pare-feu Windows Defender avec sécurité avancée" dans le menu Démarrer

### Étape 2 : Créer une nouvelle règle

1. Dans le panneau de gauche, cliquez sur **"Règles de trafic entrant"**
2. Dans le panneau de droite, cliquez sur **"Nouvelle règle..."**

### Étape 3 : Configurer la règle

1. **Type de règle** : Sélectionnez **"Port"** → Cliquez sur **"Suivant"**
2. **Protocole et ports** :
   - Sélectionnez **"TCP"**
   - Sélectionnez **"Ports locaux spécifiques"**
   - Tapez : `3000, 8000` (les deux ports séparés par une virgule)
   - Cliquez sur **"Suivant"**
3. **Action** : Sélectionnez **"Autoriser la connexion"** → Cliquez sur **"Suivant"**
4. **Profil** : Cochez **tous les profils** (Domaine, Privé, Public) → Cliquez sur **"Suivant"**
5. **Nom** : Tapez `HSE App Ports` → Cliquez sur **"Terminer"**

### Étape 4 : Vérifier

Dans la liste des règles de trafic entrant, vous devriez voir :
- ✅ **HSE App Ports** avec l'état **"Activé"**

---

## 🚀 Méthode 3 : Utiliser le Script Automatique

Un script PowerShell a été créé pour automatiser la vérification et la création des règles.

### Exécuter le script

1. Ouvrez PowerShell **en tant qu'administrateur**
2. Naviguez vers le dossier du projet :
   ```powershell
   cd C:\Users\Yassmine\Desktop\projetinfo
   ```
3. Exécutez le script :
   ```powershell
   .\verifier_ports_firewall.ps1
   ```
4. Le script vous demandera si vous voulez créer les règles → Tapez `O` pour Oui

---

## ✅ Vérification Finale

### Test depuis un autre appareil (téléphone/tablette)

1. **Assurez-vous que votre téléphone est sur le même réseau Wi-Fi**
2. Ouvrez le navigateur sur votre téléphone
3. Tapez manuellement : `http://10.24.159.13:3000`
4. Si la page se charge → ✅ **Les ports sont ouverts et accessibles**
5. Si la page ne charge pas → ❌ **Vérifiez :**
   - Le firewall (voir ci-dessus)
   - Que l'IP `10.24.159.13` est correcte (exécutez `ipconfig` sur votre PC)
   - Que Docker est en cours d'exécution (`docker-compose ps`)

### Vérifier l'IP de votre machine

```powershell
ipconfig
```

Cherchez **"IPv4 Address"** sous votre connexion Wi-Fi/Ethernet active. Si ce n'est pas `10.24.159.13`, mettez à jour :
- `docker-compose.yml` : variable `FRONTEND_URL`
- `frontend/src/pages/CommencerTest.jsx` : IP par défaut

---

## 🔧 Dépannage

### Problème : "Accès refusé" lors de l'exécution des commandes PowerShell

**Solution :** Exécutez PowerShell **en tant qu'administrateur** :
1. Cliquez droit sur PowerShell
2. Sélectionnez **"Exécuter en tant qu'administrateur"**

### Problème : Les règles existent mais les ports sont toujours fermés

**Solution :** Vérifiez que les règles sont activées :
```powershell
# Activer les règles HSE
Enable-NetFirewallRule -DisplayName "HSE App Port 3000"
Enable-NetFirewallRule -DisplayName "HSE App Port 8000"
```

### Problème : Le téléphone ne peut toujours pas accéder

**Vérifications supplémentaires :**
1. ✅ Firewall Windows : Ports 3000 et 8000 ouverts
2. ✅ Docker : Conteneurs en cours d'exécution (`docker-compose ps`)
3. ✅ IP correcte : Vérifiez avec `ipconfig`
4. ✅ Même réseau : Téléphone et PC sur le même Wi-Fi
5. ✅ Antivirus : Certains antivirus bloquent aussi les ports (ajoutez une exception)

---

## 📝 Commandes Utiles

### Lister toutes les règles de firewall
```powershell
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*HSE*" -or $_.DisplayName -like "*3000*" -or $_.DisplayName -like "*8000*"} | Format-Table DisplayName, Enabled, Direction, Action
```

### Supprimer une règle (si nécessaire)
```powershell
Remove-NetFirewallRule -DisplayName "HSE App Port 3000"
Remove-NetFirewallRule -DisplayName "HSE App Port 8000"
```

### Vérifier l'état du firewall
```powershell
Get-NetFirewallProfile | Select-Object Name, Enabled
```

---

## 🎯 Résumé Rapide

**Pour ouvrir les ports rapidement :**

1. Ouvrez PowerShell **en tant qu'administrateur**
2. Exécutez :
   ```powershell
   New-NetFirewallRule -DisplayName "HSE App Port 3000" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow -Profile Any
   New-NetFirewallRule -DisplayName "HSE App Port 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow -Profile Any
   ```
3. Testez depuis votre téléphone : `http://10.24.159.13:3000`

**C'est tout !** 🎉

