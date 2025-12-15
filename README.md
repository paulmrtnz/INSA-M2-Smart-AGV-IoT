<header align="center">
<h1 align="center">Projet Plateforme IoT - AGV Industriel</h1>
<p align="center">
 <b><a href="https://www.linkedin.com/in/paul-martinez-paul/" target="_blank">Paul MARTINEZ</a></b> • 
  <b><a href="https://www.linkedin.com/in/guilherme-de-conte-mazur/" target="_blank">Guilherme De Conte Mazur</a></b> • 
  <b><a href="https://www.linkedin.com/in/phu-khong-7b484721b/" target="_blank">Phu Khong</a></b>
<p>
<div align="center" style="display: flex; place-content: center; gap: 1.5em;">
<img src="https://www.insa-centrevaldeloire.fr/themes/custom/efil/logo.svg" height="64">
</div>
</header>
<br/>

> Plateforme IoT complète pour le contrôle et la supervision d'un robot AGV autonome via Bluetooth Low Energy  
> **Projet académique INSA CVL - 5ème année ACAD | Décembre 2025**

## Vue d'Ensemble

Ce projet implémente une **plateforme IoT moderne** pour la gestion d'un véhicule à guidage automatique (AGV) éducatif basé sur le **Keyestudio Mini Tank Robot V3 (KS0555)**. La solution complète comprend :

- **Robot embarqué** : Arduino avec navigation autonome, évitement d'obstacles, suivi de ligne
- **Application web** : Interface de contrôle temps réel avec FastAPI et WebSocket
- **Télémétrie** : Collecte et historisation des données dans une base SQLite
- **Communication** : Protocole Bluetooth Low Energy bidirectionnel

## Fonctionnalités Principales

### Robot Embarqué
- **Navigation autonome** avec suivi de ligne et évitement d'obstacles (ultrason)
- **Contrôle manuel** via télécommande infrarouge ou application web
- **Télémétrie temps réel** : distance, vitesse, mode, batterie, obstacles
- **Affichage LED 8×16** pour messages et icônes
- **Communication BLE** avec parsing automatique des paquets

### Application Web
- **Dashboard interactif** avec statut temps réel et graphiques
- **Historique complet** des données avec export JSON/CSV
- **API REST** documentée

## Stack Technologique

| Composant | Technologies |
|-----------|-------------|
| **Robot** | Arduino UNO, C++, HC-SR04 (ultrason), capteurs IR, Bluetooth |
| **Backend** | Python 3.8+, FastAPI, SQLAlchemy, Bleak (BLE), Uvicorn |
| **Frontend** | Jinja2, JavaScript ES6+, CSS3, WebSocket |
| **Base de données** | SQLite avec 4 tables (télémétrie, événements, stats, logs) |
| **Communication** | Bluetooth Low Energy (BLE) bidirectionnel |

## Structure du Projet

```
5A_ACAD_IoT/
│
├── app/                    # Application web FastAPI
│   ├── README.md           # Documentation complète application web
│   ├── api/                   # Endpoints REST (Bluetooth, Telemetry, Maintenance)
│   ├── models/                # Modèles SQLAlchemy (BDD)
│   ├── services/              # Services métier (BLE Manager)
│   ├── static/                # CSS, JavaScript, images
│   └── templates/             # Pages HTML (dashboard, diagnostic, history)
│
├── robot/                  # Code Arduino embarqué
│   ├── README.md           # Documentation complète robot
│   └── arduino_sketch/        # Sketch Arduino + bibliothèques
│       ├── arduino_sketch.ino # Programme principal
│       ├── Robot.cpp/.h       # Orchestration haut niveau
│       ├── MotorController.*  # Contrôle moteurs
│       ├── UltrasonicSensor.* # Capteur de distance
│       ├── LineTracker.*      # Suivi de ligne
│       ├── BluetoothManager.* # Communication BLE
│       ├── LEDMatrix.*        # Affichage LED 8×16
│       └── MetricsManager.*   # Collecte télémétrie
│
├── config.py               # Configuration (dev, prod, test)
├── run.py                  # Script de lancement
├── requirements.txt        # Dépendances Python
└── robot_data.db           # Base SQLite (auto-créée)
```

## Démarrage Rapide

### Prérequis
- **Python 3.8+** pour l'application web
- **Arduino IDE** pour flasher le robot
- **Robot Keyestudio KS0555** assemblé et opérationnel

### Installation

```powershell
# 1. Cloner le repository

# 2. Créer l'environnement virtuel Python
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# source venv/bin/activate    # Linux/macOS

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer l'environnement
copy .env.example .env
# Éditer .env avec l'adresse MAC de votre robot

# 5. Flasher le robot Arduino
# Ouvrir robot/arduino_sketch/arduino_sketch.ino dans Arduino IDE
# Compiler et téléverser sur la carte

# 6. Lancer l'application web
python run.py
```

### Accès
- **Dashboard** : http://localhost:8000
- **API Documentation** : http://localhost:8000/docs

## Documentation Détaillée

### Pour l'Application Web
➡️ **[Consultez le README complet de l'application](app/README.md)**

### Pour le Robot Arduino
➡️ **[Consultez le README complet du robot](robot/README.md)**

## Architecture Globale

```
┌───────────────────────────────────────────────────┐
│         Utilisateur (Navigateur Web)              │
│         http://localhost:8000                     │
└────────────────────┬──────────────────────────────┘
                     │ HTTP / WebSocket
┌────────────────────▼──────────────────────────────┐
│         Application Web FastAPI                   │
│  • Dashboard interactif                           │
│  • API REST (25+ endpoints)                       │
│  • WebSocket temps réel                           │
│  • Base de données SQLite                         │
└────────────────────┬──────────────────────────────┘
                     │ Bluetooth Low Energy
┌────────────────────▼──────────────────────────────┐
│         Robot Arduino AGV (KS0555)                │
│  • Navigation autonome                            │
│  • Capteurs (ultrason, IR, photorésistance)       │
│  • Actionneurs (moteurs, LED matrix)              │
│  • Télémétrie temps réel                          │
└───────────────────────────────────────────────────┘
```

## Données Collectées

Le système collecte et stocke automatiquement :
- **Télémétrie** : Distance parcourue, vitesse PWM, distance obstacles, mode (auto/manuel)
- **Événements** : Changements de mode, obstacles détectés, batterie faible, connexion/déconnexion
- **Statistiques** : Agrégats pour graphiques (moyennes, max, min, tendances)
- **Logs** : Historique des connexions BLE avec durées et erreurs

Format de stockage : **SQLite** avec UUID unique, checksums SHA256, et timestamps précis.


## Auteurs

- **Paul MARTINEZ**
- **Guilherme De Conte Mazur**
- **Phu Khong**

---

**Développé avec ❤️ par Paul MARTINEZ, Guilherme DE CONTE MAZUR, Phu KHONG** | Documentation: 15/12/2025
