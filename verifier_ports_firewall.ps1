# Script pour vérifier et ouvrir les ports 3000 et 8000 dans le firewall Windows
# À exécuter en tant qu'administrateur

Write-Host "=== Vérification des ports dans le firewall Windows ===" -ForegroundColor Cyan
Write-Host ""

# Vérifier les ports 3000 et 8000
$ports = @(3000, 8000)

foreach ($port in $ports) {
    Write-Host "Vérification du port $port..." -ForegroundColor Yellow
    
    # Chercher les règles existantes pour ce port
    $rules = Get-NetFirewallPortFilter | Where-Object {$_.LocalPort -eq $port} | Get-NetFirewallRule
    
    if ($rules) {
        Write-Host "  ✓ Règles trouvées pour le port $port :" -ForegroundColor Green
        foreach ($rule in $rules) {
            $status = if ($rule.Enabled) { "ACTIVÉE" } else { "DÉSACTIVÉE" }
            $color = if ($rule.Enabled) { "Green" } else { "Red" }
            Write-Host "    - $($rule.DisplayName): $status ($($rule.Direction), $($rule.Action))" -ForegroundColor $color
        }
    } else {
        Write-Host "  ✗ Aucune règle trouvée pour le port $port" -ForegroundColor Red
    }
    Write-Host ""
}

# Vérifier les règles HSE spécifiques
Write-Host "Vérification des règles HSE..." -ForegroundColor Yellow
$hseRules = Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*HSE*"}
if ($hseRules) {
    Write-Host "  ✓ Règles HSE trouvées :" -ForegroundColor Green
    foreach ($rule in $hseRules) {
        $status = if ($rule.Enabled) { "ACTIVÉE" } else { "DÉSACTIVÉE" }
        $color = if ($rule.Enabled) { "Green" } else { "Red" }
        Write-Host "    - $($rule.DisplayName): $status" -ForegroundColor $color
    }
} else {
    Write-Host "  ✗ Aucune règle HSE trouvée" -ForegroundColor Red
}
Write-Host ""

# Demander si on veut créer les règles
Write-Host "=== Création des règles (si nécessaire) ===" -ForegroundColor Cyan
$create = Read-Host "Voulez-vous créer/activer les règles pour les ports 3000 et 8000 ? (O/N)"

if ($create -eq "O" -or $create -eq "o") {
    Write-Host ""
    Write-Host "Création des règles..." -ForegroundColor Yellow
    
    # Port 3000
    try {
        $existingRule3000 = Get-NetFirewallRule -DisplayName "HSE App Port 3000" -ErrorAction SilentlyContinue
        if ($existingRule3000) {
            Write-Host "  Règle existante pour le port 3000 trouvée, activation..." -ForegroundColor Yellow
            Enable-NetFirewallRule -DisplayName "HSE App Port 3000"
        } else {
            New-NetFirewallRule -DisplayName "HSE App Port 3000" -Direction Inbound -LocalPort 3000 -Protocol TCP -Action Allow -Profile Any
            Write-Host "  ✓ Règle créée pour le port 3000" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ✗ Erreur lors de la création de la règle pour le port 3000: $_" -ForegroundColor Red
    }
    
    # Port 8000
    try {
        $existingRule8000 = Get-NetFirewallRule -DisplayName "HSE App Port 8000" -ErrorAction SilentlyContinue
        if ($existingRule8000) {
            Write-Host "  Règle existante pour le port 8000 trouvée, activation..." -ForegroundColor Yellow
            Enable-NetFirewallRule -DisplayName "HSE App Port 8000"
        } else {
            New-NetFirewallRule -DisplayName "HSE App Port 8000" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow -Profile Any
            Write-Host "  ✓ Règle créée pour le port 8000" -ForegroundColor Green
        }
    } catch {
        Write-Host "  ✗ Erreur lors de la création de la règle pour le port 8000: $_" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "=== Vérification finale ===" -ForegroundColor Cyan
    foreach ($port in $ports) {
        $rules = Get-NetFirewallPortFilter | Where-Object {$_.LocalPort -eq $port} | Get-NetFirewallRule | Where-Object {$_.Enabled -eq $true}
        if ($rules) {
            Write-Host "  ✓ Port $port : RÈGLE ACTIVE" -ForegroundColor Green
        } else {
            Write-Host "  ✗ Port $port : AUCUNE RÈGLE ACTIVE" -ForegroundColor Red
        }
    }
} else {
    Write-Host "Aucune modification effectuée." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Instructions manuelles ===" -ForegroundColor Cyan
Write-Host "Si vous préférez créer les règles manuellement :" -ForegroundColor White
Write-Host "1. Ouvrez 'Pare-feu Windows Defender avec sécurité avancée'" -ForegroundColor White
Write-Host "2. Cliquez sur 'Règles de trafic entrant' → 'Nouvelle règle'" -ForegroundColor White
Write-Host "3. Sélectionnez 'Port' → Suivant" -ForegroundColor White
Write-Host "4. TCP, ports spécifiques : 3000, 8000 → Suivant" -ForegroundColor White
Write-Host "5. Autoriser la connexion → Suivant" -ForegroundColor White
Write-Host "6. Cochez tous les profils → Suivant" -ForegroundColor White
Write-Host "7. Nom : 'HSE App Ports' → Terminer" -ForegroundColor White
Write-Host ""

