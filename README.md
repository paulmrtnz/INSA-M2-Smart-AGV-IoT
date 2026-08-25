<div align="center">

# Plateforme IoT - Véhicule Guidé Automatique (AGV)

### Projet Académique INSA Centre Val de Loire - 5ème année

**Conception et développement d'une plateforme IoT complète pour la gestion intelligente d'un robot AGV**

<img src="https://www.insa-centrevaldeloire.fr/themes/custom/efil/logo.svg" height="64">

---

**Auteurs** : [Paul MARTINEZ](https://www.linkedin.com/in/paul-martinez-paul/) • [Guilherme De Conte Mazur](https://www.linkedin.com/in/guilherme-de-conte-mazur/) • [Phu Khong](https://www.linkedin.com/in/phu-khong-7b484721b/)

**Date** : Décembre 2025

<img src="https://skills.syvixor.com/api/icons?i=python,arduino,fastapi,sql,cpp&perline=12&radius=40" alt="Skill Icons" />

</div>

---

## Table des matières

- [Vue d'ensemble](#vue-densemble)
- [Contexte et objectifs](#contexte-et-objectifs)
- [Architecture système](#architecture-système)
- [Fonctionnalités](#fonctionnalités)
- [Technologies utilisées](#technologies-utilisées)
- [Structure du projet](#structure-du-projet)
- [Installation et démarrage](#installation-et-démarrage)
- [Documentation détaillée](#documentation-détaillée)
- [Résultats et performances](#résultats-et-performances)
- [Auteurs et contributions](#auteurs-et-contributions)

---

## Vue d'ensemble

Ce projet implémente une **plateforme IoT moderne et complète** pour la gestion d'un **Véhicule à Guidage Automatique (AGV)** éducatif basé sur le **Keyestudio Mini Tank Robot V3 (KS0555)**. 

Le système intègre trois composants principaux :

1. **Robot embarqué** : Arduino avec navigation autonome multi-mode
2. **Application web** : Interface de contrôle et supervision temps réel
3. **Système de télémétrie** : Collecte, stockage et analyse des données

### Caractéristiques clés

- ✅ **Navigation autonome** avec suivi de ligne et évitement d'obstacles
- ✅ **Contrôle à distance** via application web ou télécommande infrarouge
- ✅ **Télémétrie temps réel** avec historisation complète
- ✅ **Communication Bluetooth Low Energy (BLE)** bidirectionnelle
- ✅ **Interface web moderne** avec graphiques interactifs
- ✅ **Base de données SQLite** pour l'analyse des performances

---

## Contexte et objectifs

### Contexte pédagogique

Ce projet s'inscrit dans le cadre du module **Systèmes Industriels IoT** de la 5ème année du cycle ingénieur INSA Centre Val de Loire, Génie des Systèmes Industriels, option ACAD.

### Objectifs du projet

#### Objectifs techniques

1. **Concevoir une architecture IoT complète** intégrant capteurs, actionneurs et communication sans fil
2. **Développer un système de navigation autonome** avec évitement d'obstacles et suivi de ligne
3. **Implémenter une communication Bluetooth Low Energy** robuste et efficace
4. **Créer une interface de supervision** web moderne et réactive
5. **Mettre en place un système de télémétrie** avec historisation et analyse

#### Objectifs pédagogiques

- Maîtriser les **technologies IoT** (capteurs, communication sans fil, cloud)
- Appliquer les principes de **l'embarqué temps réel** (Arduino, interruptions, PWM)
- Développer des compétences en **développement web** (FastAPI, JavaScript)
- Comprendre les enjeux de la **cybersécurité** et de la **fiabilité** des systèmes autonomes

### Cas d'usage ciblé

Le système développé simule un **AGV industriel** utilisé dans les entrepôts ou usines pour :
- Transporter des marchandises de manière autonome
- Suivre des parcours prédéfinis (lignes au sol)
- Éviter les obstacles dynamiques (personnes, objets)
- Remonter des données de fonctionnement pour la maintenance prédictive

---

## Architecture système

### Architecture globale

Le système suit une architecture **3-tiers** avec séparation claire des responsabilités :

```
┌─────────────────────────────────────────────────────────────┐
│                    NIVEAU PRÉSENTATION                      │
│          Interface web (Navigateur - Port 8000)             │
│        • Dashboard HTML/CSS/JS                              │
│        • Graphiques temps réel (WebSocket)                  │
│        • Contrôle du robot (boutons, commandes)             │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST + WebSocket
┌──────────────────────▼──────────────────────────────────────┐
│                    NIVEAU APPLICATION                       │
│          Serveur FastAPI (Python - Backend)                 │
│        • API REST (25+ endpoints)                           │
│        • WebSocket Manager (notifications)                  │
│        • BLE Manager (Bleak)                                │
│        • ORM SQLAlchemy                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ Bluetooth Low Energy
┌──────────────────────▼──────────────────────────────────────┐
│                    NIVEAU EMBARQUÉ                          │
│          Robot Arduino AGV (Microcontrôleur)                │
│        • Programme C++ (arduino_sketch.ino)                 │
│        • Capteurs (ultrason, IR, photorésistance)           │
│        • Actionneurs (moteurs DC, LED matrix)               │
│        • Module Bluetooth HC-05                             │
└─────────────────────────────────────────────────────────────┘
```

### Communication BLE

Le protocole de communication utilise **Bluetooth Low Energy (BLE)** pour échanger des données entre le robot et l'application web :

**Format des paquets de télémétrie (Robot → Serveur)** :
```json
{
  "packet_id": "uuid-unique",
  "timestamp": "2025-01-04T10:30:00",
  "uptime_s": 3600,
  "mode": "AUTO",
  "distance_cm": 45.2,
  "obstacle_events": 3,
  "speed_pwm": 180,
  "battery_level": 85,
  "dist_traveled_cm": 12450.5
}
```

---

## Fonctionnalités

### Robot embarqué (Arduino)

#### Modes de fonctionnement

1. **Mode Automatique** (`MODE_AUTO`)
   - Suivi de ligne noir automatique (3 capteurs IR)
   - Évitement d'obstacles par ultrason (HC-SR04)
   - Distance de sécurité : 25 cm
   - Arrêt d'urgence automatique si obstacle < seuil

2. **Mode Manuel** (`MODE_MANUAL`)
   - Contrôle par télécommande infrarouge
   - Contrôle depuis l'application web (via BLE)
   - Commandes directionnelles (avant, arrière, gauche, droite)
   - Contrôle de vitesse variable (PWM 0-255)

#### Capteurs intégrés

| Capteur | Modèle | Fonction | Plage |
|---------|--------|----------|-------|
| Ultrason | HC-SR04 | Mesure distance obstacles | 2-400 cm |
| Ligne IR | 3× capteurs IR | Détection ligne noire | Binaire (0/1) |
| Photorésistance | Analogique | Mesure luminosité ambiante | 0-1023 |
| Récepteur IR | VS1838B | Réception commandes télécommande | 38 kHz |

#### Actionneurs

- **Moteurs DC** : 2× moteurs avec driver L298N (contrôle PWM)
- **Matrice LED 8×16** : Affichage d'expressions et messages
- **Servo-moteur** : Rotation capteur ultrason (scan 180°)
- **Module Bluetooth** : HC-05/06 pour communication BLE

#### Télémétrie embarquée

Le robot collecte et envoie toutes les **5 secondes** :
- Distance parcourue (cumulative)
- Vitesse moteurs (PWM actuel)
- Distance obstacle (ultrason)
- Mode de fonctionnement
- Niveau de batterie (estimé)
- Événements (obstacles, changements de mode)

### Application web (FastAPI)

#### Dashboard interactif

- **Statut temps réel** :
  - Connexion Bluetooth (connecté/déconnecté)
  - Mode actif (AUTO/MANUAL)
  - Distance obstacle actuelle
  - Vitesse et batterie

- **Contrôles** :
  - Boutons de connexion/déconnexion BLE
  - Changement de mode (AUTO ↔ MANUAL)
  - Commandes directionnelles (↑ ↓ ← →)
  - Réglage vitesse (curseur 0-255)

- **Graphiques dynamiques** (mise à jour automatique) :
  - Évolution distance obstacle
  - Historique batterie
  - Vitesse moyenne
  - Distance parcourue cumulée

#### API REST

**25+ endpoints disponibles** répartis en 5 catégories :

| Catégorie | Exemples d'Endpoints | Description |
|-----------|----------------------|-------------|
| **Bluetooth** | `POST /api/ble/connect`<br>`POST /api/ble/disconnect`<br>`POST /api/ble/send` | Gestion connexion BLE |
| **Télémétrie** | `GET /api/telemetry/latest`<br>`GET /api/telemetry/history`<br>`GET /api/telemetry/stats` | Récupération données |
| **Commandes** | `POST /api/robot/motor`<br>`POST /api/robot/mode`<br>`POST /api/robot/speed` | Contrôle robot |
| **Diagnostic** | `GET /api/diagnostic/status`<br>`GET /api/diagnostic/errors` | Tests et diagnostics |
| **Maintenance** | `POST /api/maintenance/cleanup`<br>`POST /api/maintenance/archive` | Gestion BDD |

**Documentation interactive** : http://localhost:8000/docs (Swagger UI)

#### WebSocket temps réel

- **Notifications push** depuis le serveur vers le navigateur
- **Événements** : connexion BLE, réception télémétrie, erreurs
- **Fréquence** : temps réel (dès réception d'un paquet BLE)

### Système de télémétrie

#### Base de données SQLite

**4 tables relationnelles** optimisées avec index :

1. **`telemetry`** : Paquets de télémétrie bruts (tous les champs du robot)
2. **`events`** : Événements système (obstacles, changements mode, erreurs)
3. **`telemetry_statistics`** : Statistiques agrégées par période
4. **`connection_log`** : Historique des connexions BLE

#### Fonctionnalités avancées

- **UUID unique** par paquet (prévention doublons)
- **Checksum SHA256** pour validation d'intégrité
- **Timestamps précis** (timestamp paquet + received_at serveur)
- **Archivage** sans suppression (flag `archived`)
- **Export données** : JSON, CSV, Excel
- **Statistiques pré-calculées** pour graphiques rapides

---

## Technologies utilisées

### Stack technologique complète

| Couche | Technologies | Version | Rôle |
|--------|--------------|---------|------|
| **Robot** | Arduino IDE | 1.8+ | Développement embarqué |
| | C++ | C++11 | Langage programmation |
| | HC-SR04 | - | Capteur ultrason |
| | Capteurs IR | - | Détection ligne |
| | Bluetooth HC-05 | - | Communication sans fil |
| **Backend** | Python | 3.8+ | Langage serveur |
| | FastAPI | 0.104+ | Framework web async |
| | Uvicorn | 0.24+ | Serveur ASGI |
| | SQLAlchemy | 2.0+ | ORM base de données |
| | Bleak | 0.21+ | Bibliothèque BLE |
| **Frontend** | HTML5 | - | Structure pages |
| | CSS3 | - | Styles modulaires |
| | JavaScript | ES6+ | Logique client |
| | WebSocket API | - | Communication temps réel |
| **Base de Données** | SQLite | 3.x | Stockage local |

### Bibliothèques Arduino

- `IRremote.h` : Réception infrarouge

---

---

## Structure du projet

```
5A_ACAD_IoT/
│
├── 📄 README.md                    # ← Ce fichier (documentation principale)
├── 📄 ARCHITECTURE_BLE.md          # Documentation détaillée architecture BLE
├── 📄 config.py                    # Configuration (dev, prod, test)
├── 📄 requirements.txt             # Dépendances Python
├── 📄 run.py                       # Script de lancement simplifié
├── 📄 .env.example                 # Modèle variables d'environnement
├── 📄 .gitignore                   # Fichiers à ignorer par Git
├── 📊 robot_data.db                # Base SQLite (auto-créée au 1er lancement)
│
├── 📂 app/                         # APPLICATION WEB FASTAPI
│   ├── 📄 README.md                # Documentation complète application web
│   ├── 📄 __init__.py              # Factory FastAPI
│   ├── 📄 main.py                  # Point d'entrée (lance le serveur)
│   ├── 📄 routes.py                # Routes HTML (dashboard, historique...)
│   │
│   ├── 📂 api/                     # ENDPOINTS REST
│   │   ├── 📄 __init__.py          # Router principal
│   │   ├── 📄 routes.py            # Endpoints génériques (health, info)
│   │   ├── 📄 bluetooth.py         # Contrôle BLE (connect, send, receive)
│   │   ├── 📄 telemetry.py         # Récupération télémétrie (latest, history, stats)
│   │   ├── 📄 diagnostic.py        # Tests et diagnostics système
│   │   ├── 📄 maintenance.py       # Maintenance BDD (cleanup, archive, vacuum)
│   │   └── 📄 websocket_manager.py # Gestion WebSocket temps réel
│   │
│   ├── 📂 models/                  # MODÈLES DE DONNÉES (ORM)
│   │   ├── 📄 __init__.py          # Exports des modèles
│   │   ├── 📄 database.py          # Configuration SQLAlchemy (engine, session)
│   │   ├── 📄 telemetry.py         # Tables : Telemetry, Event, Stats, Logs
│   │   └── 📄 maintenance.py       # Utilitaires maintenance BDD
│   │
│   ├── 📂 services/                # SERVICES MÉTIER
│   │   ├── 📄 __init__.py          # Exports des services
│   │   └── 📄 ble_manager.py       # Gestionnaire Bluetooth (singleton thread-safe)
│   │
│   ├── 📂 static/                  # FICHIERS STATIQUES
│   │   ├── 📂 css/
│   │   │   ├── 📄 constants.css    # Variables globales (couleurs, espacements)
│   │   │   ├── 📄 components.css   # Composants UI réutilisables
│   │   │   ├── 📄 modules.css      # Modules métier (graphiques, dashboard)
│   │   │   ├── 📄 animations.css   # Animations et transitions
│   │   │   ├── 📄 fonts.css        # Polices personnalisées
│   │   │   ├── 📄 index.css        # Styles page d'accueil
│   │   │   ├── 📄 style.css        # Styles généraux
│   │   │   └── 📄 custom.css       # Personnalisations
│   │   │
│   │   ├── 📂 js/
│   │   │   ├── 📄 api-client.js    # Client HTTP pour appeler l'API REST
│   │   │   ├── 📄 robot-api.js     # Interface de contrôle robot
│   │   │   └── 📄 charts.js        # Graphiques (Chart.js, D3.js...)
│   │   │
│   │   ├── 📂 img/                 # Images, icônes, logos
│   │   └── 📂 fonts/               # Polices personnalisées (LemonMilk, etc.)
│   │       └── 📂 LemonMilk/
│   │
│   └── 📂 templates/               # TEMPLATES HTML (Jinja2)
│       ├── 📄 index.html           # Page d'accueil
│       ├── 📄 dashboard.html       # Tableau de bord principal
│       ├── 📄 diagnostic.html      # Page de diagnostic
│       ├── 📄 history.html         # Historique des données
│       ├── 📄 debug.html           # Console de débogage
│       └── 📄 test.html            # Tests fonctionnels
│
└── 📂 robot/                       # CODE ARDUINO EMBARQUÉ
    ├── 📄 README.md                # Documentation complète robot
    └── 📂 arduino_sketch/          # Sketch Arduino + bibliothèques
        ├── 📄 arduino_sketch.ino   # Programme principal (setup, loop)
        ├── 📄 Robot.cpp/.h         # Orchestration haut niveau
        ├── 📄 MotorController.cpp/.h # Contrôle moteurs DC (PWM, direction)
        ├── 📄 UltrasonicSensor.cpp/.h # Capteur ultrason HC-SR04
        ├── 📄 LineTracker.cpp/.h   # Suivi de ligne (3 capteurs IR)
        ├── 📄 Photoresistor.cpp/.h # Capteur de luminosité
        ├── 📄 IRRemote.cpp/.h      # Récepteur infrarouge (télécommande)
        ├── 📄 BluetoothManager.cpp/.h # Communication Bluetooth
        ├── 📄 LEDMatrix.cpp/.h     # Affichage matrice LED 8×16
        └── 📄 MetricsManager.cpp/.h # Collecte et envoi télémétrie
```
---

## Installation et démarrage

### Prérequis système

**Logiciels requis** :
- ✅ **Python 3.8+** (télécharger sur [python.org](https://www.python.org/downloads/))
- ✅ **Arduino IDE 1.8+** (télécharger sur [arduino.cc](https://www.arduino.cc/en/software))

**Matériel requis** :
- ✅ **Robot Keyestudio KS0555** assemblé et fonctionnel
- ✅ **Module Bluetooth** HC-05 ou HC-06 configuré
- ✅ **Câble USB** pour connexion Arduino
- ✅ **Alimentation** 6× piles AA

---

### Installation complète (étape par étape)

#### **Étape 1 : Cloner le repository (ou Télécharger le ZIP)**

```bash
# Option A : Via Git
git clone https://github.com/paulmrtnz/INSA-M2-Smart-AGV-IoT
cd INSA-M2-Smart-AGV-IoT

# Option B : Télécharger le ZIP et extraire
```

#### **Étape 2 : Configuration de l'environnement Python**

##### Windows (PowerShell)
```powershell
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
.\venv\Scripts\Activate.ps1

# Si erreur de politique d'exécution :
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Installer les dépendances
pip install -r requirements.txt
```

##### Linux / macOS (Bash)
```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

#### **Étape 3 : Configuration des variables d'environnement**

Créer un fichier `.env` à la racine du projet :

```bash
# Copier le modèle
cp .env.example .env

# Éditer le fichier .env (notepad, nano, vim...)
```

**Contenu du fichier `.env`** :
```env
# ==========================================
# CONFIGURATION BLUETOOTH (OBLIGATOIRE)
# ==========================================
BLE_DEVICE_ADDRESS=48:87:2d:76:b3:1d  # ← Remplacer par l'adresse MAC de votre robot
BLE_UUID_WRITE=FFE2                    # UUID caractéristique écriture BLE

# ==========================================
# CONFIGURATION SERVEUR (OPTIONNEL)
# ==========================================
HOST=0.0.0.0                           # Écoute sur toutes les interfaces
PORT=8000                              # Port du serveur web
DEBUG=True                             # Mode debug (développement)

# ==========================================
# CONFIGURATION BASE DE DONNÉES (OPTIONNEL)
# ==========================================
DATABASE_URL=sqlite:///./robot_data.db # Chemin de la base SQLite
```

> **💡 Comment trouver l'adresse MAC Bluetooth ?**
> 
> - **Windows** : Paramètres → Bluetooth → Rechercher "HC-05" → Propriétés
> - **Linux** : `bluetoothctl` → `scan on` → noter l'adresse MAC
> - **Application web** : Utiliser l'endpoint `/api/ble/scan` après démarrage

#### **Étape 4 : Flasher le robot Arduino**

1. **Ouvrir Arduino IDE**
2. **Ouvrir le fichier** : `robot/arduino_sketch/arduino_sketch.ino`
3. **Configurer la carte** :
   - Outils → Type de carte → Arduino UNO
   - Outils → Port → Sélectionner le port COM (ex: COM3)
4. **Compiler et téléverser** : Cliquer sur "Téléverser" (→)
5. **Vérifier** : Ouvrir le moniteur série (9600 bauds) → messages de démarrage

#### **Étape 5 : Lancer l'Application Web**

```bash
# Méthode 1 : Via le script run.py (recommandé)
python run.py

# Méthode 2 : Via main.py directement
python app/main.py

# Méthode 3 : Via uvicorn en ligne de commande
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Sortie attendue** :
```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)

╔═══════════════════════════════════════════════════════╗
║         APPLICATION WEB AGV DÉMARRÉE                  ║
╠═══════════════════════════════════════════════════════╣
║  Dashboard   : http://localhost:8000/dashboard        ║
╚═══════════════════════════════════════════════════════╝
```

#### **Étape 6 : Utiliser l'Application**

1. **Ouvrir le navigateur** : http://localhost:8000
2. **Connecter le robot** :
   - Cliquer sur le bouton **"Connecter Bluetooth"**
   - Attendre le voyant vert ✅
3. **Visualiser les données** :
   - Graphiques temps réel
   - Historique télémétrie
   - Statistiques

---

## Documentation détaillée

### Documentation par composant

| Document | Contenu | Lien |
|----------|---------|------|
| **README Application Web** | Installation, API, architecture backend | [app/README.md](app/README.md) |
| **README Robot Arduino** | Composants, capteurs, code embarqué | [robot/README.md](robot/README.md) |
| **Architecture BLE** | Protocole, paquets, communication | [ARCHITECTURE_BLE.md](ARCHITECTURE_BLE.md) |

### Ressources externes

- **Documentation Keyestudio KS0555** : https://docs.keyestudio.com/projects/KS0555/en/latest
- **FastAPI Documentation** : https://fastapi.tiangolo.com/
- **Bleak (BLE Python)** : https://bleak.readthedocs.io/
- **Arduino Reference** : https://www.arduino.cc/reference/

---

## Auteurs

### Équipe PGP Solutions

- **Paul MARTINEZ** 
- **Guilherme De Conte Mazur**
- **Phu Khong**

---

### Citation recommandée

```
MARTINEZ Paul, DE CONTE MAZUR Guilherme, KHONG Phu (2025).
"Plateforme IoT pour Véhicule Guidé Automatique (AGV)".
Projet académique INSA Centre Val de Loire, 5A ACAD.
https://github.com/paulmrtnz/INSA-M2-Smart-AGV-IoT
```

---

<div align="center">

**Développé avec ❤️ par Paul MARTINEZ, Guilherme DE CONTE MAZUR, Phu KHONG**

**INSA Centre Val de Loire** | Décembre 2025

</div>
