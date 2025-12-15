# Robot Autonome AGV - PGP Solutions
# Documentation

## Table des matières
- [Robot Autonome AGV - Mini Tank Robot V3 (KS0555)](#robot-autonome-agv---mini-tank-robot-v3-ks0555)
  - [Table des matières](#table-des-matières)
  - [Vue d'ensemble](#vue-densemble)
  - [Caractéristiques principales](#caractéristiques-principales)
  - [Architecture du système](#architecture-du-système)
  - [Composants matériels](#composants-matériels)
    - [Contrôleur](#contrôleur)
    - [Capteurs](#capteurs)
    - [Actionneurs](#actionneurs)
  - [Scénarios de fonctionnement](#scénarios-de-fonctionnement)
    - [1 Suivi de ligne avec évitement d'obstacles (Mode Automatique)](#1-suivi-de-ligne-avec-évitement-dobstacles-mode-automatique)
    - [2 Gestion de la lumière ambiante](#2-gestion-de-la-lumière-ambiante)
    - [3 Télémétrie Bluetooth (Communication hôte)](#3-télémétrie-bluetooth-communication-hôte)
    - [4 Mode Contrôle infrarouge (Mode Manuel)](#4-mode-contrôle-infrarouge-mode-manuel)
  - [Structure du code](#structure-du-code)
    - [Flux d'exécution](#flux-dexécution)
  - [Documentation complète](#documentation-complète)
  - [Dépannage](#dépannage)

## Vue d'ensemble

Ce projet est une implémentation du **Keyestudio Mini Tank Robot V3 (KS0555)**, un véhicule à guidage automatique (AGV) éducatif basé sur Arduino. Le robot est conçu pour démontrer plusieurs concepts de robotique autonome incluant l'évitement d'obstacles, le suivi de ligne, et le contrôle à distance.

**Référence produit**: KS0555 Mini Tank Robot V3  
**Plateforme**: Arduino (Keyestudio V4.0 Development Board)  
**Documentation officielle**: [docs.keyestudio.com/projects/KS0555](https://docs.keyestudio.com/projects/KS0555/en/latest)

## Caractéristiques principales

- **Modes de navigation autonome**:
  - Suivi de ligne automatique
  - Évitement d'obstacles par ultrasons
  - Suivi d'objets (ultrasonic following)

- **Modes de contrôle manuel**:
  - Contrôle par télécommande infrarouge
  - Contrôle de la vitesse variable

- **Modes de communication**:
  - Matrice LED 8×16 pour texte
  - Module Bluetooth Low Energy
  - Système de mesure et télémétrie

## Architecture du système

```
+-----------------------------+
|    arduino_sketch.ino       |  ← Contrôleur principal
| (setup(), loop(), états)    |
+-----------------------------+
      |
      |--> Gère 2 modes de fonctionnement :
      |    1. MODE_MANUAL : Contrôle à distance
      |    2. MODE_AUTO : Navigation autonome
      |
      |--> Priorité sécurité : Détection d'obstacles prioritaire
      |
+------------------------------------------------------------------------------------------------+
|                                    MODULES (Capteurs & Actionneurs)                            |
+------------------------------------+------------------------------------+------------------------------------+
|        Capteurs (Entrées)          |      Actionneurs (Sorties)         |         Communication              |
+------------------------------------+------------------------------------+------------------------------------+
|                                    |                                    |                                    |
|  UltrasonicSensor.cpp/.h           |   MotorController.cpp/.h           |    IRRemote.cpp/.h                 |
|    - Mesure de distance            |     - Mouvement avant/arrière      |     - Réception commandes IR       |
|    - Détection d'obstacles         |     - Rotations gauche/droite      |     - Décodage télécommande        |
|    - Portée: 2cm - 400cm           |     - Contrôle de vitesse PWM      |                                    |
|                                    |     - Arrêt d'urgence              |                                    |
|  LineTracker.cpp/.h                |                                    |   BluetoothManager.cpp/.h          |
|    - 3 capteurs IR ligne           |   LEDMatrix.cpp/.h                 |     - Communication série BT       |
|    - Détection ligne noire         |     - Affichage 8×16 pixels        |     - Contrôle depuis smartphone   |
|    - Logique de suivi              |     - Expressions faciales         |     - Commandes à distance         |
|                                    |     - Indicateurs d'état           |                                    |
|  Photoresistor.cpp/.h              |                                    |   MetricsManager.cpp/.h            |
|    - Mesure de luminosité          |   Robot.cpp/.h                     |     - Collecte de données          |
|    - Détection source lumineuse    |     - Orchestration haut niveau    |     - Télémétrie (prévu)           |
|    - Suivi de lumière              |     - Gestion des modes            |                                    |
|                                    |                                    |                                    |
+------------------------------------+------------------------------------+------------------------------------+
```

## Composants matériels

### Contrôleur
- **Keyestudio V4.0 Development Board** (Arduino UNO)
- Microcontrôleur ATmega328P
- Tensions d'opération: 5V (logique) / 7-12V (alimentation moteurs)

### Capteurs
- **Capteur ultrasonique HC-SR04**: Mesure de distance (2-400cm)
- **3× Capteurs de ligne infrarouge**: Détection de lignes
- **Photorésistance**: Mesure de luminosité ambiante
- **Récepteur infrarouge**: Réception commandes télécommande
- **Module Bluetooth**: Communication sans fil

### Actionneurs
- **2× Moteurs DC avec réducteur**: Propulsion chenilles
- **Driver moteur L298N**: Contrôle bidirectionnel + PWM
- **Matrice LED 8×16**: Affichage expressions/états
- **Servo moteur**: Rotation du capteur ultrasonique (scanning)

## Scénarios de fonctionnement

### 1 Suivi de ligne avec évitement d'obstacles (Mode Automatique)
**Objectif**: Suivre automatiquement une ligne sur le sol pour gérer le déplacement dans des espaces partagés.

**Fonctionnement**:
1. Les 3 capteurs IR de ligne détectent la présence/absence de la ligne
2. La direction est déduite des valeurs des 3 capteurs
3. **Si obstacle < seuil (25 cm)**:
   - Arrêt immédiat
   - Affichage d'un message d'avertissement ("!!!")
   - Attente du dégagement de l'obstacle
4. **Si pas d'obstacle** → Continuer

### 2 Gestion de la lumière ambiante
**Objectif**: Adapter l'utilisation de phares ou non en fonction de l'environnement.

**Fonctionnement**:
- 1 photorésisteurs placés à l'avant.
- Comparaison des valeurs de luminosité:
  - **Si luminosité < seuil**: → Allumer les phares
  - **Si luminosité > seuil**: → Eteindre les phares

### 3 Télémétrie Bluetooth (Communication hôte)
**Objectif**: Envoyer des données de fonctionnement à un ordinateur distant pour le contrôle du fonctionnement

**Fonctionnement**:
- Communication série via module Bluetooth HC-05/06
- Envoi de paquets de données mesurées sur l'appareil

### 4 Mode Contrôle infrarouge (Mode Manuel)
**Objectif**: Pilotage manuel via la télécommande (pour maintenance ou prise en main d'urgence)

**Fonctionnement**:
- Réception et décodage des signaux IR
- Mapping des boutons:
  - **Flèches directionnelles**: → Déplacements
  - **\***: → Passage en mode automatique

## Structure du code

```
arduino_sketch/
├── arduino_sketch.ino       # Programme principal
├── Robot.cpp/.h             # Classe orchestratrice
├── MotorController.cpp/.h   # Contrôle des moteurs
├── UltrasonicSensor.cpp/.h  # Gestion capteur ultrason
├── LineTracker.cpp/.h       # Logique suivi de ligne
├── Photoresistor.cpp/.h     # Capteurs de luminosité
├── IRRemote.cpp/.h          # Réception infrarouge
├── BluetoothManager.cpp/.h  # Communication Bluetooth
├── LEDMatrix.cpp/.h         # Affichage matrice LED
└── MetricsManager.cpp/.h    # Télémétrie et métriques
```

### Flux d'exécution

```
setup()
  ├── Initialisation des pins
  ├── Configuration des modules
  └── État initial: MODE_MANUAL

loop()
  ├── Lecture des capteurs
  ├── Traitement commandes (IR/BT)
  ├── Exécution logique du mode actif
  │   ├── MODE_AUTO → Suivi ligne autonome
  │   └── MODE_MANUAL → Attente commandes
  ├── Sécurité: Vérification obstacles
  └── Mise à jour affichages (LED Matrix)
```

## Documentation complète

Pour des informations détaillées sur:
- **Assemblage du robot**: [Product Setup](https://docs.keyestudio.com/projects/KS0555/en/latest/docs/Product%20setup/Product%20setup.html)
- **Schémas de câblage**: [Product Introduction](https://docs.keyestudio.com/projects/KS0555/en/latest/docs/Product%20introduction.html)

**Lien documentation officielle**: https://docs.keyestudio.com/projects/KS0555/en/latest

## Dépannage

| Problème | Solution |
|----------|----------|
| Robot ne répond pas | Vérifier alimentation + connexion USB |
| Moteurs ne tournent pas | Vérifier driver L298N + tensions |
| Capteur US incohérent | Vérifier câblage TRIG/ECHO + alimentation 5V |
| Bluetooth non détecté | Vérifier baud rate (9600) + LED module BT |
| Suivi ligne imprécis | Calibrer seuils + contraste piste |

---

**Développé avec ❤️ par Paul MARTINEZ, Guilherme DE CONTE MAZUR, Phu KHONG** | Documentation: 15/12/2025