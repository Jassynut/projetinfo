# 📚 Documentation API - Plateforme HSE

## 🔐 Vue d'ensemble de l'authentification

### 3 Niveaux d'Authentification:

1. **HSE Users** (Passent le test)
   - Authentification: CIN uniquement (1 seul champ)
   - Backend: `HSEUserBackend`
   - URL: `POST /api/auth/test/{test_id}/auth/`

2. **Managers HSE** (Gèrent les tests)
   - Authentification: Full Name + CIN
   - Backend: `HSEManagerBackend`
   - URL: `POST /api/manager/login/`

3. **Admins** (Accès complet)
   - Authentification: Username + Password
   - Backend: `AdminBackend`
   - URL: `/admin/`

---

## 📊 API Endpoints Complets

### AUTHENTIFICATION

#### 1. Manager Login (PC)
\`\`\`
POST /api/manager/login/
Content-Type: application/json

{
    "full_name": "Fatima Zohra",
    "cin": "AB123456"
}

Response:
{
    "success": true,
    "user": {
        "id": 1,
        "full_name": "Fatima Zohra",
        "username": "fatima_zohra",
        "user_type": "manager",
        "is_staff": true
    }
}
\`\`\`

#### 2. HSE User Auth (Mobile - CIN seul)
\`\`\`
POST /api/auth/test/{test_id}/auth/
Content-Type: application/json

{
    "cin": "AB123456"
}

Response:
{
    "success": true,
    "test_session": {
        "id": 5,
        "test_id": 1,
        "test_title": "Test HSE Version 1",
        "started_at": "2025-01-15T10:30:00Z",
        "duration_minutes": 10,
        "questions_count": 21
    },
    "user": {
        "id": 1,
        "cin": "AB123456",
        "full_name": "Ahmed Mustafa",
        "user_type": "user",
        "employee_data": {
            "id": 1,
            "full_name": "Ahmed Mustafa",
            "department": "Production",
            "position": "Ouvrier",
            "site": "Phosboucraa"
        }
    },
    "questions": [...]
}
\`\`\`

---

### UTILISATEURS HSE

#### 1. Lister tous les utilisateurs
\`\`\`
GET /api/hse/users/?search=&page=1&page_size=20&entreprise=&entite=&reussite=
Authorization: Token <token>

Response:
{
    "success": true,
    "users": [
        {
            "id": 1,
            "cin": "AB123456",
            "nom": "Mustafa",
            "prenom": "Ahmed",
            "full_name": "Ahmed Mustafa",
            "email": "ahmed@example.com",
            "entreprise": "OCP",
            "entite": "Phosboucraa",
            "presence": true,
            "reussite": true,
            "score": 19,
            "taux_reussite": 85.5,
            "test_attempts": 2
        }
    ],
    "pagination": {
        "page": 1,
        "page_size": 20,
        "total_count": 150,
        "total_pages": 8
    }
}
\`\`\`

#### 2. Chercher un utilisateur par CIN
\`\`\`
GET /api/hse/users/search/?cin=AB123456
Authorization: Token <token>

Response:
{
    "success": true,
    "user": {
        "id": 1,
        "cin": "AB123456",
        "full_name": "Ahmed Mustafa",
        "email": "ahmed@example.com",
        "presence": true,
        "score": 19,
        "recent_attempts": [
            {
                "test_version": 1,
                "started_at": "2025-01-15T10:30:00Z",
                "status": "completed",
                "passed": true,
                "total_score": 90.5,
                "mandatory_score": 100.0
            }
        ]
    }
}
\`\`\`

#### 3. Créer un utilisateur HSE
\`\`\`
POST /api/hse/users/create/
Authorization: Token <token>
Content-Type: application/json

{
    "nom": "Mustafa",
    "prenom": "Ahmed",
    "cin": "AB123456",
    "email": "ahmed@example.com",
    "entite": "Phosboucraa",
    "entreprise": "OCP",
    "presence": true,
    "reussite": false,
    "score": 0
}

Response:
{
    "success": true,
    "user": {
        "id": 1,
        "full_name": "Ahmed Mustafa",
        "cin": "AB123456",
        "entreprise": "OCP"
    }
}
\`\`\`

#### 4. Modifier la présence d'un utilisateur
\`\`\`
PATCH /api/hse/users/{user_id}/presence/
Authorization: Token <token>
Content-Type: application/json

{
    "presence": true
}

Response:
{
    "success": true,
    "user": {
        "id": 1,
        "full_name": "Ahmed Mustafa",
        "presence": true,
        "updated_at": "2025-01-15T10:30:00Z"
    }
}
\`\`\`

---

### TESTS HSE

#### 1. Lister les versions de tests
\`\`\`
GET /api/hse/tests/
Response:
{
    "success": true,
    "tests": [
        {
            "id": 1,
            "version": 1,
            "description": "Test HSE Version 1",
            "duration_minutes": 10,
            "total_questions": 21,
            "mandatory_questions_count": 9,
            "optional_questions_count": 12,
            "is_active": true,
            "questions_in_order": [1, 5, 3, 7, ...],
            "mandatory_questions": [1, 5, 3, 7, 9, 11, 13, 15, 17]
        }
    ]
}
\`\`\`

#### 2. Démarrer une tentative de test
\`\`\`
POST /api/hse/test-attempts/start/
Authorization: Token <token>
Content-Type: application/json

{
    "test_version": 1,
    "langue": "ar"
}

Response:
{
    "success": true,
    "attempt": {
        "id": 5,
        "test_version": 1,
        "langue": "Arabe",
        "started_at": "2025-01-15T10:30:00Z",
        "duration_minutes": 10,
        "total_questions": 21,
        "mandatory_count": 9
    },
    "questions": [
        {
            "id": 1,
            "question_code": "Q1",
            "enonce": "L'équipement de protection individuelle est obligatoire...",
            "is_mandatory": true,
            "points": 1,
            "has_image": false,
            "image_url": null
        }
    ]
}
\`\`\`

#### 3. Soumettre les réponses du test
\`\`\`
POST /api/hse/test-attempts/{attempt_id}/submit/
Authorization: Token <token>
Content-Type: application/json

{
    "answers": {
        "1": {"answer": true, "is_mandatory": true},
        "2": {"answer": false, "is_mandatory": false},
        "3": {"answer": true, "is_mandatory": true}
    }
}

Response:
{
    "success": true,
    "results": {
        "passed": true,
        "mandatory": {
            "correct": 9,
            "total": 9,
            "percentage": 100.0,
            "passed": true
        },
        "optional": {
            "correct": 10,
            "total": 12,
            "percentage": 83.33
        },
        "overall": {
            "correct": 19,
            "total": 21,
            "percentage": 90.48
        },
        "time_taken_seconds": 480
    }
}
\`\`\`

#### 4. Historique des tests
\`\`\`
GET /api/hse/test-attempts/history/
Authorization: Token <token>

Response:
{
    "success": true,
    "history": [
        {
            "id": 5,
            "test_version": 1,
            "test_description": "Test HSE Version 1",
            "started_at": "2025-01-15T10:30:00Z",
            "completed_at": "2025-01-15T10:38:00Z",
            "langue": "Arabe",
            "status": "passed",
            "passed": true,
            "scores": {
                "mandatory": "9/9",
                "optional": "10/12",
                "overall": "90%"
            },
            "time_taken": "8:00"
        }
    ]
}
\`\`\`

---

### CERTIFICATS

#### 1. Générer un certificat
\`\`\`
GET /api/certificates/generate/{attempt_id}/
Authorization: Token <token>

Response:
{
    "success": true,
    "certificate": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "certificate_number": "HSE-20250115-A1B2C3",
        "user_full_name": "Ahmed Mustafa",
        "user_cin": "AB123456",
        "test_version": 1,
        "score": 90,
        "issued_date": "2025-01-15T10:38:00Z",
        "expiry_date": "2026-01-15",
        "download_url": "/api/certificates/550e8400-e29b-41d4-a716-446655440000/download/"
    }
}
\`\`\`

#### 2. Télécharger un certificat PDF
\`\`\`
GET /api/certificates/{certificate_id}/download/
Response: PDF File (application/pdf)
\`\`\`

#### 3. Rechercher un certificat par nom
\`\`\`
POST /api/certificates/search/
Content-Type: application/json

{
    "user_name": "Ahmed Mustafa",
    "user_cin": "AB123456"
}

Response:
{
    "success": true,
    "certificates": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "certificate_number": "HSE-20250115-A1B2C3",
            "user_full_name": "Ahmed Mustafa",
            "user_cin": "AB123456",
            "test_version": 1,
            "score": 90,
            "issued_date": "2025-01-15T10:38:00Z",
            "expiry_date": "2026-01-15",
            "is_expired": false,
            "days_until_expiry": 365,
            "download_url": "/api/certificates/550e8400-e29b-41d4-a716-446655440000/download/"
        }
    ]
}
\`\`\`

---

### STATISTIQUES (Admin)

#### 1. Statistiques globales
\`\`\`
GET /api/hse/statistics/
Authorization: Token <token> (Admin only)

Response:
{
    "success": true,
    "statistics": {
        "users": {
            "total": 150,
            "present": 140,
            "successful": 120,
            "presence_rate": 93.33,
            "success_rate": 80.0
        },
        "attempts": {
            "total": 180,
            "completed": 150,
            "passed": 120,
            "completion_rate": 83.33,
            "success_rate": 80.0
        },
        "by_version": [
            {
                "version": 1,
                "attempts": 50,
                "avg_score": 85.5,
                "passed": 42,
                "pass_rate": 84.0
            }
        ],
        "by_langue": [
            {
                "langue": "Arabe",
                "attempts": 100,
                "avg_score": 85.2
            }
        ]
    }
}
\`\`\`

---

## 🔗 Architecture Frontend-Backend

### Flux de Communication:

\`\`\`
┌─────────────────────────────────────────────────────────────────────┐
│                         PLATEFORME HSE                              │
├──────────────────────────────┬──────────────────────────────────────┤
│    FRONTEND (React/Next.js)  │        BACKEND (Django REST)        │
├──────────────────────────────┼──────────────────────────────────────┤
│ INTERFACE MANAGER (PC)       │ Port: 8000                           │
│ - Dashboard users            │ → /api/hse/users/                    │
│ - Modifier présence          │ → PATCH /api/hse/users/{id}/presence/│
│ - Générer QR codes           │ → POST /api/manager/generate-qr/     │
│ - Voir statistiques          │ → GET /api/hse/statistics/           │
│ - Gérer tests & versions     │ → GET /api/hse/tests/               │
├──────────────────────────────┼──────────────────────────────────────┤
│ INTERFACE MOBILE (Tablet)    │ Port: 8000                           │
│ - Scanner QR code            │ → POST /api/auth/decode-qr/         │
│ - Entrer CIN                 │ → POST /api/auth/test/{id}/auth/     │
│ - Passer le test             │ → GET /api/hse/test-attempts/start/  │
│ - Soumettre réponses         │ → POST /api/hse/test-attempts/{}/sub│
│ - Télécharger certificat     │ → GET /api/certificates/download/   │
├──────────────────────────────┼──────────────────────────────────────┤
│ SECTION RECHERCHE CERTIFICAT │ Port: 8000                           │
│ - Entrer nom utilisateur     │ → POST /api/certificates/search/     │
│ - Voir score & certificat    │ → GET /api/certificates/{id}/        │
│ - Télécharger PDF            │ → GET /api/certificates/{}/download/ │
└──────────────────────────────┴──────────────────────────────────────┘
\`\`\`

### Sécurité & CORS:

\`\`\`python
# settings.py
CORS_ALLOW_ALL_ORIGINS = True  # À remplacer en production

# Meilleure pratique:
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",      # Frontend dev
    "http://10.26.31.10:5173",    # Tablet (local network)
    "https://yourdomain.com",     # Production
]
\`\`\`

---

## 📱 Flux Utilisateur Complet

### 1. Manager - Configuration du Test
\`\`\`
1. Manager accède à l'interface PC
2. Se connecte: full_name + CIN
3. Sélectionne un test (version 1-6)
4. Clique "Générer QR Code"
5. Backend génère QR avec URL et test_id
6. Affiche QR à l'écran
\`\`\`

### 2. HSE User - Passage du Test
\`\`\`
1. Employé scanne QR code depuis tablet
2. Frontend envoie QR data au backend
3. Backend retourne infos du test
4. Employé entre son CIN
5. Backend authentifie et crée une tentative
6. Employé répond aux 21 questions (9 obligatoires + 12 optionnelles)
7. Soumet ses réponses
8. Backend calcule:
   - Score obligatoires (doit être 9/9)
   - Score optionnels
   - Score total (/21)
   - Réussi ou échoué
9. Si réussi → Génère certificat
10. Employé télécharge PDF du certificat
\`\`\`

### 3. Recherche Certificat - Section Spéciale
\`\`\`
1. Utilisateur entre le nom ou CIN
2. Frontend envoie au backend
3. Backend recherche tous les certificats
4. Affiche les certificats avec scores
5. Utilisateur clique "Télécharger"
6. Backend envoie PDF
\`\`\`

---

## 🔧 Intégration Frontend-Backend

### Schéma d'URL Recommandé:

\`\`\`javascript
// .env.local
REACT_APP_API_URL=http://localhost:8000/api

// Appels API depuis React:
const API = process.env.REACT_APP_API_URL

// Authentification Manager
const loginManager = async (fullName, cin) => {
  const response = await fetch(`${API}/manager/login/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ full_name: fullName, cin })
  })
  return response.json()
}

// Lister utilisateurs
const listUsers = async () => {
  const response = await fetch(`${API}/hse/users/`, {
    method: 'GET',
    headers: { 'Authorization': `Token ${token}` }
  })
  return response.json()
}
\`\`\`

---

## 🚀 Déploiement & Production

### Variables d'Environnement Requises:

\`\`\`bash
# Django
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,10.26.31.10

# Database
DATABASE_URL=mysql://user:password@localhost/hse_database

# CORS
CORS_ALLOWED_ORIGINS=https://yourdomain.com

# PDF Generation
WEASYPRINT_URL=http://localhost:6000  # Optional
\`\`\`

### Docker Compose (Recommandé):

\`\`\`yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    environment:
      MYSQL_DATABASE: hse_database
      MYSQL_ROOT_PASSWORD: root

  backend:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    ports:
      - "8000:8000"
    depends_on:
      - mysql
    environment:
      DATABASE_URL: mysql://root:root@mysql/hse_database
\`\`\`

---

## 📝 Notes pour l'Équipe Frontend

1. **Utiliser Token Authentication** pour les requêtes sécurisées
2. **Gérer les Erreurs 401/403** → Rediriger vers login
3. **Valider les réponses** avant soumission
4. **Implémenter un timeout** de session (10-15 minutes)
5. **Sauvegarder les réponses localement** (cache) pour éviter les pertes
6. **Afficher barre de progression** pendant le test
7. **Confirmer avant soumission** du test
