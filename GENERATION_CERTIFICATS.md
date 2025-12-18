# 📄 Guide de Génération de Certificats

## 📚 Bibliothèque utilisée

Le projet utilise **`xhtml2pdf`** version **0.2.15** pour générer les certificats PDF.

### Installation

La bibliothèque est déjà dans `backend/requirements.txt` :
```txt
xhtml2pdf==0.2.15
Pillow==10.0.0
reportlab==4.0.7
```

Pour installer :
```bash
pip install -r backend/requirements.txt
```

## 🔧 Comment ça fonctionne

### 1. Principe général

La génération de certificats suit ce processus :

1. **Template HTML** → Un template Django (`certificats/certificate.html`) contient la structure HTML/CSS du certificat
2. **Remplissage des données** → Django remplit le template avec les données de l'utilisateur
3. **Conversion HTML → PDF** → `xhtml2pdf.pisa.CreatePDF()` convertit le HTML en PDF
4. **Téléchargement** → Le PDF est envoyé au client via `HttpResponse`

### 2. Code principal

**Fichier** : `backend/certificats/views_public.py`

```python
from django.template.loader import render_to_string
from xhtml2pdf import pisa

# 1. Remplir le template HTML avec les données
html_string = render_to_string('certificats/certificate.html', {
    'user_nom': user_nom,
    'user_prenom': user_prenom,
    'user_cin': hse_user.cin,
    'user_entite': user_entite,
    'user_chef_projet': user_chef_projet,
    'test_date': test_date,
    'logo_path': logo_path
})

# 2. Créer la réponse HTTP avec le type PDF
response = HttpResponse(content_type='application/pdf')
response['Content-Disposition'] = f'attachment; filename=certificat_{certificate_number}.pdf'

# 3. Convertir HTML en PDF
pisa.CreatePDF(html_string, response)
return response
```

### 3. Template HTML

**Fichier** : `backend/certificats/templates/certificats/certificate.html`

Le template contient :
- **CSS** pour le style (taille A4, marges, polices)
- **Structure HTML** avec les informations du certificat
- **Variables Django** (`{{ user_nom }}`, `{{ user_cin }}`, etc.)

### 4. Endpoints API

#### A. Rechercher des certificats
```
POST /api/certificats/recherche/
Body: { "cni": "AB123456" }
```

Retourne la liste des certificats disponibles pour un CIN.

#### B. Télécharger un certificat PDF
```
GET /api/certificats/cert::{cin}::test::{attempt_id}/pdf
```

Génère et télécharge le PDF à la volée.

**Format de l'ID** :
- `cert::{cin}::test::{attempt_id}` - Certificat basé sur un test
- `cert::{cin}::sensibilisation` - Certificat de sensibilisation

## 📋 Données incluses dans le certificat

Le certificat contient :
- **Nom et Prénom** de l'utilisateur
- **CIN** (Carte d'Identité Nationale)
- **Entité** (département/service)
- **Chef de projet**
- **Date de passage du test**
- **Logo OCP** (si disponible)

## 🎨 Personnalisation

### Modifier le design

Éditez le fichier `backend/certificats/templates/certificats/certificate.html` :

1. **Modifier les styles CSS** dans la balise `<style>`
2. **Ajouter/supprimer des champs** dans la section `<div class="content">`
3. **Changer les couleurs, polices, tailles**, etc.

### Ajouter des images

Le logo est chargé depuis :
```
backend/public/logo_ocp.webp
backend/public/ocp-logo.png
backend/public/placeholder-logo.png
```

Placez vos images dans `backend/public/` et modifiez le code dans `views_public.py` ligne 239.

## ⚠️ Limitations de xhtml2pdf

`xhtml2pdf` a quelques limitations :

1. **CSS limité** : Tous les styles CSS ne sont pas supportés
   - ✅ Supporté : `color`, `font-size`, `margin`, `padding`, `border`
   - ❌ Non supporté : `flexbox` avancé, `grid`, certaines propriétés modernes

2. **Images** : 
   - Utilisez des chemins absolus pour les images
   - Formats supportés : PNG, JPG, GIF

3. **Polices** :
   - Utilisez des polices système (Arial, Times, etc.)
   - Les polices personnalisées nécessitent une configuration supplémentaire

## 🔍 Exemple d'utilisation complète

```python
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa

def generate_certificate(request):
    # Données du certificat
    context = {
        'user_nom': 'Dupont',
        'user_prenom': 'Jean',
        'user_cin': 'AB123456',
        'user_entite': 'Production',
        'user_chef_projet': 'M. Martin',
        'test_date': '15/12/2025',
        'logo_path': '/path/to/logo.png'
    }
    
    # Générer le HTML
    html_string = render_to_string('certificats/certificate.html', context)
    
    # Créer la réponse PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="certificat.pdf"'
    
    # Convertir en PDF
    pisa.CreatePDF(html_string, response)
    
    return response
```

## 📝 Notes importantes

1. **Génération à la volée** : Les certificats sont générés à la demande, pas stockés en base
2. **Tests finaux uniquement** : Seuls les tests avec `etat='test_final'` génèrent des certificats
3. **Validation** : Le système vérifie que l'utilisateur a réussi le test avant de générer le certificat
4. **Expiration** : Les certificats ont une date d'expiration (1 an par défaut)

## 🐛 Dépannage

### Erreur "xhtml2pdf not found"
```bash
pip install xhtml2pdf==0.2.15
```

### Erreur "Image not found"
- Vérifiez que le logo existe dans `backend/public/`
- Utilisez des chemins absolus dans le template

### PDF mal formaté
- Vérifiez que le CSS est compatible avec xhtml2pdf
- Évitez les propriétés CSS modernes non supportées

## 📚 Documentation xhtml2pdf

- Documentation officielle : https://xhtml2pdf.readthedocs.io/
- GitHub : https://github.com/xhtml2pdf/xhtml2pdf

