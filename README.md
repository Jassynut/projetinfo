# 🏭 Plateforme HSE - Induction HSE Jorf Lasfar

Plateforme web complète pour la gestion des formations HSE (Health, Safety, Environment), des tests et des certificats pour les collaborateurs OCP.

## 📋 Table des matières

- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Prérequis](#-prérequis)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Utilisation](#-utilisation)
- [Structure du projet](#-structure-du-projet)
- [API Documentation](#-api-documentation)
- [Déploiement](#-déploiement)
- [Contribution](#-contribution)

## ✨ Fonctionnalités

### 🔐 Authentification multi-niveaux

- **Apprenants (HSE Users)** : Authentification par CIN uniquement via QR code
- **Managers HSE** : Authentification par Nom complet + CIN
- **Administrateurs** : Authentification Django standard

### 📊 Gestion des données

- **Base de données des apprenants** : CRUD complet avec import/export Excel
- **Filtrage et recherche** : Par date, CIN, nom, prénom, entité, entreprise
- **Gestion de la présence** : Suivi de la présence des apprenants
- **Statistiques détaillées** : Tableaux de bord avec graphiques de progression

### 📝 Gestion des tests

- **Versions de tests** : Création et gestion de multiples versions
- **Questions** : Gestion des questions avec options multiples
- **QR Codes** : Génération de QR codes pour accès mobile aux tests
- **Tests multilingues** : Support français, arabe, anglais

### 📜 Certificats

- **Génération automatique** : Création de certificats PDF après réussite du test
- **Consultation** : Recherche et téléchargement de certificats par CIN
- **Personnalisation** : Certificats avec logo OCP et informations détaillées

### 📈 Statistiques

- **Tableau de bord HSE** : Statistiques en temps réel
- **Progression mensuelle** : Graphiques de progression des moyennes
- **Indicateurs clés** : Présence, test initial, test final, amélioration

## 🏗️ Architecture

### Stack technique

- **Backend** : Django 4.x + Django REST Framework
- **Frontend** : React 19 + Vite + Tailwind CSS
- **Base de données** : MySQL 8.0
- **Conteneurisation** : Docker & Docker Compose
- **Serveur web** : Nginx (production)

### Structure

```
projetinfo/
├── backend/              # Application Django
│   ├── authentication/  # Module d'authentification
│   ├── hse_app/         # Module HSE (utilisateurs, managers)
│   ├── tests/           # Module tests et questionnaires
│   ├── certificats/      # Module certificats
│   └── stats/           # Module statistiques
├── frontend/            # Application React
│   ├── src/
│   │   ├── pages/      # Pages de l'application
│   │   ├── components/ # Composants réutilisables
│   │   └── utils/      # Utilitaires (CSRF, axios)
│   └── public/         # Assets statiques
└── docker-compose.yml  # Configuration Docker
```

## 📦 Prérequis

- **Docker** & **Docker Compose** (recommandé)
- Ou :
  - **Python 3.11+**
  - **Node.js 18+** et **npm/yarn**
  - **MySQL 8.0+**

## 🚀 Installation

### Option 1 : Docker (Recommandé)

1. **Cloner le repository**
   ```bash
   git clone <repository-url>
   cd projetinfo
   ```

2. **Lancer les services**
   ```bash
   docker-compose up -d
   ```

3. **Créer les migrations et superutilisateur** (première fois)
   ```bash
   docker-compose exec backend python manage.py migrate
   docker-compose exec backend python manage.py createsuperuser
   ```

4. **Accéder à l'application**
   - Frontend : http://localhost:3000
   - Backend API : http://localhost:8000
   - Admin Django : http://localhost:8000/admin

### Option 2 : Installation manuelle

#### Backend

1. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows
   ```

2. **Installer les dépendances**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configurer la base de données**
   - Créer une base de données MySQL : `hse_database`
   - Configurer les variables d'environnement (voir [Configuration](#-configuration))

4. **Appliquer les migrations**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

5. **Lancer le serveur**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

#### Frontend

1. **Installer les dépendances**
   ```bash
   cd frontend
   npm install
   # ou
   yarn install
   ```

2. **Lancer le serveur de développement**
   ```bash
   npm run dev
   # ou
   yarn dev
   ```

3. **Accéder à l'application**
   - http://localhost:3000

## ⚙️ Configuration

### Variables d'environnement

#### Backend (`backend/settings.py` ou variables Docker)

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_NAME=hse_database
DATABASE_USER=root
DATABASE_PASSWORD=root
DATABASE_HOST=db  # ou localhost si installation manuelle
DATABASE_PORT=3306
ALLOWED_HOSTS=localhost,127.0.0.1,10.24.159.13,*
FRONTEND_URL=http://10.24.159.13:3000
```

#### Frontend (`frontend/src/config.js`)

La configuration de l'API est automatique et détecte l'URL du serveur.

### Configuration CORS

Les origines autorisées sont configurées dans `backend/settings.py` :
- `CORS_ALLOWED_ORIGINS` : Liste des origines autorisées
- `CSRF_TRUSTED_ORIGINS` : Origines de confiance pour CSRF

## 📖 Utilisation

### Pour les Managers

1. **Connexion**
   - Accéder à http://localhost:3000
   - Saisir le nom complet et le CIN
   - Cliquer sur "Se connecter"

2. **Gestion des apprenants**
   - Accéder à "Base de données"
   - Ajouter/modifier/supprimer des apprenants
   - Importer depuis Excel
   - Exporter en Excel

3. **Gestion des tests**
   - Accéder à "Gestion des questionnaires"
   - Créer des versions de tests
   - Ajouter/modifier des questions
   - Générer des QR codes

4. **Statistiques**
   - Accéder à "Tableau de bord"
   - Sélectionner une date
   - Consulter les statistiques et graphiques

### Pour les Apprenants

1. **Accès au test**
   - Scanner le QR code fourni par le manager
   - Ou accéder directement via l'URL du test

2. **Authentification**
   - Saisir le CIN
   - Sélectionner la langue (FR/AR/EN)

3. **Passer le test**
   - Répondre aux questions
   - Soumettre le test
   - Consulter les résultats

4. **Télécharger le certificat**
   - Si le test est réussi, le certificat est généré automatiquement
   - Rechercher le certificat par CIN dans "Rechercher un certificat"

## 📁 Structure du projet

### Backend

- `authentication/` : Authentification multi-niveaux
- `hse_app/` : Modèles HSE (utilisateurs, managers)
- `tests/` : Gestion des tests et questionnaires
- `certificats/` : Génération de certificats PDF
- `stats/` : Calcul et API des statistiques

### Frontend

- `src/pages/` : Pages principales
  - `Login.jsx` : Page de connexion
  - `Dashboard.jsx` : Tableau de bord principal
  - `Database.jsx` : Gestion des apprenants
  - `DashboardHSE.jsx` : Statistiques HSE
  - `GestionQuestionnaires.jsx` : Gestion des tests
  - `PasserTest.jsx` : Interface apprenant
  - `ConsultationCertificats.jsx` : Consultation certificats

- `src/components/` : Composants réutilisables
  - `TopNav.jsx` : Navigation principale
  - `ManualAddStudent.jsx` : Formulaire ajout apprenant
  - `ManualEditStudent.jsx` : Formulaire modification apprenant

## 📚 API Documentation

La documentation complète de l'API est disponible dans :
- `backend/BACKEND_API_DOCUMENTATION.md`

### Endpoints principaux

#### Authentification
- `POST /api/manager/login/` : Connexion manager
- `POST /api/auth/test/{test_id}/auth/` : Authentification apprenant

#### Utilisateurs HSE
- `GET /api/hse/users/` : Liste des utilisateurs
- `POST /api/hse/users/create/` : Créer un utilisateur
- `GET /api/hse/users/{id}/` : Détails d'un utilisateur
- `PUT /api/hse/users/{id}/update/` : Modifier un utilisateur

#### Tests
- `GET /api/tests/` : Liste des tests
- `POST /api/tests/` : Créer un test
- `GET /api/test/{id}/questions/` : Questions d'un test

#### Certificats
- `GET /api/certificates/` : Liste des certificats
- `GET /api/certificates/{id}/download/` : Télécharger un certificat
- `POST /api/certificates/search/` : Rechercher un certificat

#### Statistiques
- `GET /api/stats/hse/stats/` : Statistiques par date
- `GET /api/stats/hse/stats/monthly/` : Statistiques mensuelles

## 🐳 Déploiement

### Docker Compose

Le projet est configuré pour être déployé avec Docker Compose :

```bash
# Démarrer tous les services
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter les services
docker-compose down

# Reconstruire les images
docker-compose build --no-cache
```

### Production

Pour la production, modifier :
- `DEBUG=False` dans `settings.py`
- `SECRET_KEY` sécurisé
- `ALLOWED_HOSTS` avec les domaines réels
- Configuration HTTPS
- Variables d'environnement sécurisées

## 🔧 Commandes utiles

### Backend

```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic

# Shell Django
python manage.py shell
```

### Frontend

```bash
# Développement
npm run dev

# Build production
npm run build

# Preview build
npm run preview

# Linter
npm run lint
```

## 🧪 Tests

```bash
# Backend
python manage.py test

# Frontend
npm test
```

**Version** : 1.0.0  
**Dernière mise à jour** : 2025-12-18

