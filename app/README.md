# Application Web IoT Robot AGV - PGP Solutions
# Documentation

> **Application FastAPI pour le contrôle d'un robot Arduino via Bluetooth Low Energy**  
> Version 2.0.0 | Architecture moderne avec async/await natif

---

## Table des Matières

1. [Stack Technologique](#-stack-technologique)
2. [Architecture de l'Application](#-architecture-de-lapplication)
3. [Architecture de la Base de Données](#-architecture-de-la-base-de-données)
4. [Prise en Main Rapide](#-prise-en-main-rapide)
5. [Structure des Fichiers](#-structure-des-fichiers)
6. [API Endpoints](#-api-endpoints)
7. [Interface Web](#-interface-web)
8. [Maintenance et Monitoring](#-maintenance-et-monitoring)

---

## Stack Technologique

### Backend
- **FastAPI 0.104+** - Framework web moderne avec support async natif
- **Uvicorn** - Serveur ASGI haute performance
- **SQLAlchemy 2.0+** - ORM pour la gestion de la base de données
- **Bleak 0.21+** - Bibliothèque Bluetooth Low Energy multi-plateforme

### Frontend
- **Jinja2** - Moteur de templates HTML
- **Vanilla JavaScript** - Pas de framework lourd, API native moderne
- **CSS3** - Styles personnalisés modulaires
- **WebSocket** - Communication temps réel pour les notifications BLE

### Base de Données
- **SQLite** - Base de données embarquée, légère et performante
- **4 Tables relationnelles** avec index optimisés
- **Stockage complet** des paquets de télémétrie et événements

### Utilitaires
- **python-dotenv** - Gestion des variables d'environnement
- **pytest** - Tests unitaires et d'intégration

---

## Architecture de l'Application

### Vue d'Ensemble

L'application suit une **architecture modulaire en couches** avec séparation des responsabilités :

```
┌────────────────────────────────────────────────────┐
│                  Client (Navigateur)               │
│              HTML + JS + CSS + WebSocket           │
└────────────────────┬───────────────────────────────┘
                     │ HTTP/WebSocket
┌────────────────────▼───────────────────────────────┐
│              FastAPI Application                   │
│  ┌──────────────────────────────────────────────┐  │
│  │  Routes HTML (Dashboard, Debug, History...)  │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │  API REST (Bluetooth, Telemetry, Diagnostic) │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │  WebSocket Manager (Notifications temps réel)│  │
│  └──────────────────────────────────────────────┘  │
└────────────────────┬───────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────┐
│                  Services Layer                    │
│  ┌──────────────────────────────────────────────┐  │
│  │  BLE Manager (Connexion, Envoi, Réception)   │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────┬───────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────┐
│                 Data Layer (SQLAlchemy)            │
│  ┌──────────────────────────────────────────────┐  │
│  │  Models: Telemetry, Event, Stats, Logs       │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────┬───────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────┐
│              SQLite Database (robot_data.db)       │
└────────────────────────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────┐
│              Robot Arduino (Bluetooth)             │
└────────────────────────────────────────────────────┘
```

### Modules Principaux

#### 1. **Point d'Entrée** (`main.py`)
```python
# Initialise l'application FastAPI
app = create_app()

# Lance le serveur Uvicorn
uvicorn.run(app, host="0.0.0.0", port=8000)
```

**Fonctionnalités :**
- Configuration du serveur ASGI
- Hot reload en développement
- Affichage des URLs d'accès (Swagger, ReDoc)

#### 2. **Factory** (`__init__.py`)
```python
def create_app() -> FastAPI:
    # Création de l'instance FastAPI
    # Configuration CORS
    # Montage des fichiers statiques
    # Initialisation de la BDD
    # Enregistrement des routers
    # Configuration WebSocket
```

#### 3. **API Layer** (`app/api/`)

##### Structure des Routers
```
api/
├── __init__.py           # Router principal
├── routes.py             # Endpoints génériques (health, info)
├── bluetooth.py          # Contrôle BLE (connect, message, motor)
├── telemetry.py          # Historique et statistiques
├── maintenance.py        # Nettoyage et optimisation BDD
├── diagnostic.py         # Tests et diagnostics système
└── websocket_manager.py  # Gestion des connexions WebSocket
```

#### 4. **Services Layer** (`app/services/`)

##### BLE Manager (`ble_manager.py`)
**Responsabilité unique :** Gestion de la connexion Bluetooth

**Caractéristiques :**
- Thread-safe avec `asyncio.Lock`
- Gestion d'erreurs complète
- Reconnexion automatique
- Notification callback pour WebSocket
- Parsing automatique des paquets BLE
- Stockage automatique en BDD

#### 5. **Data Layer** (`app/models/`)

##### Models (`database.py`, `telemetry.py`, `maintenance.py`)
```python
# Configuration SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Modèles ORM
class Telemetry(Base):
    __tablename__ = "telemetry"
    # ... colonnes et relations

class Event(Base):
    __tablename__ = "events"
    # ... colonnes et relations
```

#### 6. **Frontend Layer** (`app/static/`, `app/templates/`)

##### Templates HTML
- `index.html` - Page d'accueil
- `dashboard.html` - Tableau de bord principal
- `diagnostic.html` - Page de diagnostic
- `history.html` - Historique des données
- `debug.html` - Console de débogage
- `test.html` - Page de test des fonctionnalités

##### JavaScript Modulaire
- `api-client.js` - Client HTTP pour l'API REST
- `robot-api.js` - Interface de contrôle du robot
- `charts.js` - Graphiques et visualisations

##### CSS Modulaire
- `constants.css` - Variables globales
- `components.css` - Composants réutilisables
- `modules.css` - Modules métier
- `animations.css` - Animations et transitions

---

## Architecture de la Base de Données

### Schéma Complet

```sql
┌──────────────────────────────────────────────────────┐
│               Table: telemetry                       │
├──────────────────────────────────────────────────────┤
│ id (PK)              INTEGER AUTO_INCREMENT          │
│ packet_id            VARCHAR(36) UNIQUE (UUID)       │
│ timestamp            DATETIME (indexed)              │
│ received_at          DATETIME                        │
│ uptime_s             INTEGER                         │
│ mode                 VARCHAR(20) (indexed)           │
│ distance_cm          FLOAT                           │
│ obstacle_events      INTEGER                         │
│ last_ir_cmd          VARCHAR(20)                     │
│ speed_pwm            INTEGER (0-255)                 │
│ dist_traveled_cm     FLOAT                           │
│ battery_level        INTEGER (0-100)                 │
│ signal_strength      INTEGER (RSSI)                  │
│ packet_raw           TEXT (JSON brut)                │
│ checksum             VARCHAR(64) (SHA256)            │
│ processed            BOOLEAN                         │
│ archived             BOOLEAN                         │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│                 Table: events                        │
├──────────────────────────────────────────────────────┤
│ id (PK)              INTEGER AUTO_INCREMENT          │
│ event_id             VARCHAR(36) UNIQUE (UUID)       │
│ timestamp            DATETIME (indexed)              │
│ received_at          DATETIME                        │
│ event_type           VARCHAR(50) (indexed)           │
│ category             VARCHAR(20) (indexed)           │
│ description          VARCHAR(255)                    │
│ value                VARCHAR(100)                    │
│ new_value            VARCHAR(100)                    │
│ severity_level       INTEGER (1-5)                   │
│ acknowledged         BOOLEAN                         │
│ source               VARCHAR(50)                     │
│ metadata             TEXT (JSON)                     │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│          Table: telemetry_statistics                 │
├──────────────────────────────────────────────────────┤
│ id (PK)              INTEGER AUTO_INCREMENT          │
│ period_start         DATETIME (indexed)              │
│ period_end           DATETIME                        │
│ total_packets        INTEGER                         │
│ avg_distance_cm      FLOAT                           │
│ max_distance_cm      FLOAT                           │
│ min_distance_cm      FLOAT                           │
│ avg_speed_pwm        FLOAT                           │
│ total_obstacles      INTEGER                         │
│ total_distance_cm    FLOAT                           │
│ mode_auto_count      INTEGER                         │
│ mode_manual_count    INTEGER                         │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│            Table: connection_log                     │
├──────────────────────────────────────────────────────┤
│ id (PK)              INTEGER AUTO_INCREMENT          │
│ timestamp            DATETIME (indexed)              │
│ event_type           VARCHAR(20) (indexed)           │
│ device_address       VARCHAR(17)                     │
│ device_name          VARCHAR(100)                    │
│ success              BOOLEAN                         │
│ error_message        TEXT                            │
│ duration_ms          INTEGER                         │
└──────────────────────────────────────────────────────┘
```

### Types d'Événements

| Type | Catégorie | Description |
|------|-----------|-------------|
| `mode_change` | info | Changement de mode (auto ↔ manual) |
| `lights_toggle` | info | Activation/désactivation des lumières |
| `obstacle_detected` | warning | Obstacle détecté par ultrason |
| `emergency_stop` | critical | Arrêt d'urgence activé |
| `battery_low` | warning | Batterie faible (< 20%) |
| `connection_established` | info | Connexion BLE établie |
| `connection_lost` | error | Perte de connexion BLE |

### Stratégie de Stockage

#### Historisation Complète
- **UUID unique** par paquet (pas de doublons)
- **Checksum SHA256** pour validation d'intégrité
- **Timestamps séparés** (timestamp du paquet vs received_at)
- **Flags archived** pour archivage sans suppression
- **Métadonnées brutes** (packet_raw) pour audit complet

#### Maintenance Automatique
- **Nettoyage périodique** : Suppression des données > X jours
- **Archivage** : Marquage `archived=True` sans suppression
- **Optimisation** : VACUUM et réindexation automatique
- **Statistiques agrégées** : Pré-calcul pour graphiques rapides


## Prise en Main Rapide

### Prérequis

- **Python 3.8+** installé
- **Robot Arduino** avec Bluetooth activé
- **Windows/Linux/macOS** (compatible multi-plateforme)

### Installation en 5 Étapes

#### 1. Cloner le Repository

#### 2. Créer l'Environnement Virtuel

```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

#### 3. Installer les Dépendances

```powershell
pip install -r requirements.txt
```

**Dépendances principales :**
- `fastapi==0.104.1` - Framework web
- `uvicorn[standard]==0.24.0` - Serveur ASGI
- `bleak==0.21.1` - Bluetooth Low Energy
- `sqlalchemy==2.0.23` - ORM base de données
- `jinja2==3.1.2` - Templates HTML
- `python-dotenv==1.0.0` - Variables d'environnement

#### 4. Configurer l'Environnement

Créer un fichier `.env` à la racine :

```env
# Configuration Bluetooth (obligatoire)
BLE_DEVICE_ADDRESS=48:87:2d:76:b3:1d
BLE_UUID_WRITE=FFE2
```

> **Note :** Pour trouver l'adresse MAC de votre robot, utilisez l'endpoint `/api/ble/scan`

#### 5. Lancer l'Application

```powershell
# Méthode 1 : Via run.py (recommandé)
python run.py

# Méthode 2 : Via main.py
python app/main.py

# Méthode 3 : Via uvicorn directement
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Accès à l'Application

Une fois lancé, l'application est accessible sur :

| Service | URL | Description |
|---------|-----|-------------|
| **Dashboard** | http://localhost:8000 | Interface principale |
| **Swagger UI** | http://localhost:8000/docs | Documentation API interactive |
| **ReDoc** | http://localhost:8000/redoc | Documentation API alternative |
| **API REST** | http://localhost:8000/api | Endpoints API |

### Première Connexion au Robot

1. Ouvrir http://localhost:8000
2. Cliquer sur **"Connecter Bluetooth"**
3. Attendre le voyant vert ✅
4. Tester l'envoi d'un message ou une commande moteur


## Structure des Fichiers

### Vue d'Ensemble

```
/
│
├── config.py                 # Configuration (dev, prod, test)
├── requirements.txt          # Dépendances Python
├── run.py                    # Script de lancement principal
├── .env                      # Variables d'environnement (à créer)
├── .gitignore                # Fichiers à ignorer
├── robot_data.db             # Base de données SQLite (auto-créée)
│
├── app/                      # ← Dossier de l'application web
│   │
│   ├── __init__.py           # Factory FastAPI
│   ├── main.py               # Point d'entrée principal
│   ├── routes.py             # Routes HTML (dashboard, debug...)
│   ├── README.md             # ← Ce fichier
│   │
│   ├── api/                  # API REST
│   │   ├── __init__.py       # Router principal
│   │   ├── routes.py         # Endpoints génériques (health, info)
│   │   ├── bluetooth.py      # Contrôle BLE (connect, message, motor)
│   │   ├── telemetry.py      # Historique et statistiques
│   │   ├── maintenance.py    # Nettoyage et optimisation BDD
│   │   ├── diagnostic.py     # Tests et diagnostics système
│   │   └── websocket_manager.py  # Gestion WebSocket temps réel
│   │
│   ├── models/               # Modèles de données (ORM)
│   │   ├── __init__.py       # Exports des modèles
│   │   ├── database.py       # Configuration SQLAlchemy
│   │   ├── telemetry.py      # Tables: Telemetry, Event, Stats, Logs
│   │   └── maintenance.py    # Utilitaires maintenance BDD
│   │
│   ├── services/             # Services métier
│   │   ├── __init__.py       # Exports des services
│   │   └── ble_manager.py    # Gestionnaire Bluetooth
│   │
│   ├── static/               # Fichiers statiques
│   │   ├── css/
│   │   │   ├── constants.css      # Variables globales
│   │   │   ├── components.css    # Composants UI
│   │   │   ├── modules.css       # Modules métier
│   │   │   ├── animations.css    # Animations
│   │   │   ├── fonts.css         # Polices
│   │   │   ├── index.css         # Page d'accueil
│   │   │   ├── style.css         # Styles généraux
│   │   │   └── custom.css        # Personnalisations
│   │   │
│   │   ├── js/
│   │   │   ├── api-client.js     # Client HTTP pour API
│   │   │   ├── robot-api.js      # Interface robot
│   │   │   └── charts.js         # Graphiques
│   │   │
│   │   ├── img/              # Images et icônes
│   │   └── fonts/            # Polices personnalisées
│   │       └── LemonMilk/
│   │
│   └── templates/            # Templates HTML (Jinja2)
│       ├── index.html        # Page d'accueil
│       ├── dashboard.html    # Tableau de bord principal
│
└── robot/                    # Code Arduino (référence)
    └── arduino_sketch/
        ├── arduino_sketch.ino
        ├── BluetoothManager.cpp/.h
        ├── Robot.cpp/.h
        └── ...
```

## Interface Web

### Pages Disponibles

#### 1. Page d'Accueil (`/`)
- Présentation du projet
- Lien vers dashboard

#### 2. Dashboard (`/dashboard`)
**Sections principales :**
- **Connexion Bluetooth** : Connecter/déconnecter le robot
- **Statut en Temps Réel** : Distance, mode, batterie, vitesse
- **Graphiques** : Historique distance, batterie, vitesse

---

**Développé avec ❤️ par Paul MARTINEZ, Guilherme DE CONTE MAZUR, Phu KHONG** | Documentation: 15/12/2025
