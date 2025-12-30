# Diagrammes d'Architecture - Plateforme IoT AGV

> Documentation visuelle complète du projet Smart AGV IoT  
> **Projet INSA CVL - 5ème année ACAD | Décembre 2025**

## 📋 Table des Matières

1. [Vue d'Ensemble](#vue-densemble)
2. [Liste des Diagrammes](#liste-des-diagrammes)
3. [Comment Utiliser les Diagrammes](#comment-utiliser-les-diagrammes)
4. [Génération des Images](#génération-des-images)
5. [Légende et Conventions](#légende-et-conventions)

---

## Vue d'Ensemble

Ce dossier contient l'ensemble des diagrammes UML décrivant l'architecture complète du système IoT AGV. Les diagrammes couvrent tous les aspects du projet, de l'architecture globale aux machines à états détaillées, en passant par les séquences d'opération et le déploiement.

Le projet est composé de **deux blocs principaux** :
- **Application Web** : Backend FastAPI + Frontend HTML/CSS/JS
- **Robot Arduino** : Firmware embarqué avec capteurs et actionneurs

Ces deux blocs communiquent via **Bluetooth Low Energy (BLE)** pour assurer le contrôle temps réel et la télémétrie.

---

## Liste des Diagrammes

### 1. Architecture Globale
**Fichier** : [`01-architecture-globale.puml`](01-architecture-globale.puml)

**Description** : Vue d'ensemble de l'architecture en couches du système complet.

**Contenu** :
- Couche Utilisateur (Navigateur Web)
- Couche Application (API Layer, Services Layer, Data Layer)
- Couche Communication (Bluetooth Low Energy)
- Couche Robot (Capteurs, Actionneurs, Communication)

**À consulter pour** :
- Comprendre l'organisation globale du système
- Identifier les dépendances entre composants
- Visualiser les flux de données

---

### 2. Vue d'Ensemble du Système
**Fichier** : [`02-vue-ensemble-systeme.puml`](02-vue-ensemble-systeme.puml)

**Description** : Diagramme de composants montrant les interactions entre tous les éléments du système.

**Contenu** :
- Interface Web (Dashboard, Historique, Diagnostic)
- API REST (25+ endpoints)
- Services (BLE Manager, WebSocket Manager)
- Base de données SQLite (4 tables)
- Robot AGV (FSM, Capteurs, Actionneurs)

**À consulter pour** :
- Comprendre le rôle de chaque composant
- Visualiser les flux de communication
- Identifier les points d'intégration

---

### 3. Machine à États du Robot
**Fichier** : [`03-machine-etats-robot.puml`](03-machine-etats-robot.puml)

**Description** : Diagramme d'états UML détaillant le comportement du firmware Arduino.

**États principaux** :
- **STARTING** : Initialisation matérielle
- **WAITING_BT** : Attente connexion Bluetooth
- **MANUAL** : Contrôle manuel (IR ou BLE)
- **AUTO** : Navigation autonome (suivi ligne)
- **OBSTACLE_DETECTED** : Sécurité anti-collision

**Transitions** :
- Connexion/Déconnexion BLE
- Commandes IR/BLE (mode auto/manuel)
- Détection obstacle (distance < 25cm)
- Dégagement obstacle (distance > 25cm)

**À consulter pour** :
- Comprendre le comportement du robot
- Déboguer les transitions d'état
- Implémenter de nouveaux modes

---

### 4. Machine à États de l'Application
**Fichier** : [`04-machine-etats-application.puml`](04-machine-etats-application.puml)

**Description** : Diagramme d'états de l'application web FastAPI et du gestionnaire BLE.

**États principaux** :
- **INIT** : Initialisation serveur Uvicorn
- **READY** : Serveur prêt, BLE non connecté
- **CONNECTING_BLE** : Tentative connexion Bluetooth
- **CONNECTED** : BLE actif et opérationnel
- **DISCONNECTING** : Fermeture propre connexion

**Tâches parallèles** :
- HTTP Request Handling (API REST)
- WebSocket Connections (notifications temps réel)
- Database Operations (stockage télémétrie)

**À consulter pour** :
- Comprendre le cycle de vie de la connexion BLE
- Gérer les erreurs de connexion
- Optimiser les tâches asynchrones

---

### 5. Séquence de Fonctionnement Global
**Fichier** : [`05-sequence-fonctionnement-global.puml`](05-sequence-fonctionnement-global.puml)

**Description** : Diagramme de séquence détaillant un scénario complet d'utilisation.

**Phases couvertes** :
1. **Démarrage et Initialisation** : Lancement serveur + robot
2. **Connexion Bluetooth** : Établissement lien BLE
3. **Envoi Commande** : Contrôle manuel (exemple: "forward")
4. **Réception Télémétrie** : Collecte automatique toutes les 30s
5. **Mode Automatique** : Navigation autonome avec suivi ligne
6. **Consultation Historique** : Requêtes API pour données passées
7. **Déconnexion** : Fermeture propre connexion BLE

**À consulter pour** :
- Comprendre le flux complet d'utilisation
- Identifier les points de synchronisation
- Déboguer les problèmes de communication

---

### 6. Diagramme de Déploiement
**Fichier** : [`06-diagramme-deploiement.puml`](06-diagramme-deploiement.puml)

**Description** : Architecture physique et logique du déploiement.

**Nœuds représentés** :
- **Poste Développeur/Serveur** :
  - Environnement Python (venv)
  - Application FastAPI
  - Base de données SQLite
  - Serveur Uvicorn (port 8000)
  
- **Poste Client** :
  - Navigateur Web
  - Interface HTML/CSS/JS
  - Client WebSocket
  
- **Robot AGV** :
  - Arduino UNO (ATmega328P)
  - Module Bluetooth HC-05/06
  - Capteurs (Ultrason, IR, Photorésistance)
  - Actionneurs (Moteurs, LED Matrix)
  - Alimentation batteries

**Communication** :
- HTTP/WebSocket (Client ↔ Serveur)
- Bluetooth Low Energy (Serveur ↔ Robot)

**À consulter pour** :
- Comprendre l'infrastructure technique
- Planifier le déploiement
- Configurer l'environnement de développement

---

## Comment Utiliser les Diagrammes

### Format PlantUML

Tous les diagrammes sont au format **PlantUML** (`.puml`), un langage de description de diagrammes UML textuel.

**Avantages** :
- ✅ Versionnable avec Git
- ✅ Modifiable facilement (simple texte)
- ✅ Génération automatique d'images
- ✅ Compatible avec de nombreux outils

### Visualisation en Ligne

**Option 1 : PlantUML Online Server**
1. Aller sur https://www.plantuml.com/plantuml/uml/
2. Copier-coller le contenu d'un fichier `.puml`
3. Cliquer sur "Submit"
4. Télécharger l'image générée (PNG/SVG)

**Option 2 : Visual Studio Code**
1. Installer l'extension "PlantUML" (jebbs.plantuml)
2. Ouvrir un fichier `.puml`
3. Appuyer sur `Alt+D` pour prévisualiser
4. Clic droit → "Export Current Diagram" pour exporter

**Option 3 : GitHub (rendu natif)**
- GitHub rend automatiquement certains formats UML
- Voir le fichier directement dans l'interface web

---

## Génération des Images

### Installation PlantUML Local

#### Prérequis
- **Java Runtime Environment (JRE)** : version 8 ou supérieure
- **Graphviz** : pour le rendu (optionnel mais recommandé)

#### Installation

**Windows** :
```powershell
# Chocolatey
choco install plantuml graphviz

# Ou téléchargement manuel
# https://plantuml.com/download
```

**Linux (Ubuntu/Debian)** :
```bash
sudo apt update
sudo apt install plantuml graphviz
```

**macOS** :
```bash
# Homebrew
brew install plantuml graphviz
```

#### Génération des PNG

```bash
# Générer un diagramme unique
plantuml 01-architecture-globale.puml

# Générer tous les diagrammes du dossier
plantuml *.puml

# Générer en SVG (vectoriel)
plantuml -tsvg *.puml

# Générer en PDF
plantuml -tpdf *.puml
```

Les images sont générées dans le même dossier avec les extensions `.png`, `.svg` ou `.pdf`.

---

## Légende et Conventions

### Symboles UML Utilisés

| Symbole | Signification | Utilisation |
|---------|---------------|-------------|
| Rectangle | Composant / Nœud | Modules logiciels, matériel |
| Cylindre | Base de données | SQLite, tables |
| Nuage | Réseau / Protocole | BLE, HTTP, WebSocket |
| Bonhomme | Acteur | Utilisateur |
| Flèche pleine | Relation forte | Dépendance directe |
| Flèche pointillée | Relation faible | Communication réseau |
| État arrondi | État FSM | États machine à états |
| Note jaune | Annotation | Informations complémentaires |

### Code Couleur (selon le thème)

- **Blanc/Gris clair** : Composants applicatifs
- **Jaune** : Notes et annotations
- **Bleu** : Communication / Protocoles
- **Vert** : États actifs / OK
- **Rouge** : États d'erreur / Alerte

### Nomenclature

- **UPPERCASE** : États, constantes
- **camelCase** : Variables, méthodes
- **PascalCase** : Classes, composants
- **kebab-case** : Noms de fichiers

---

## Maintenance des Diagrammes

### Bonnes Pratiques

1. **Modifier le source `.puml`** : Ne jamais éditer directement les images PNG/SVG
2. **Regénérer après modification** : Toujours regénérer les images après changement
3. **Versionner les sources** : Commit des `.puml`, pas forcément des images
4. **Documenter les changements** : Ajouter une note de version si modification importante
5. **Valider la cohérence** : Vérifier que les diagrammes restent cohérents entre eux

### Mises à Jour

Lorsque le code évolue, mettre à jour les diagrammes concernés :

| Changement Code | Diagrammes à Mettre à Jour |
|-----------------|---------------------------|
| Nouvel état robot | 03-machine-etats-robot.puml |
| Nouvelle API endpoint | 02-vue-ensemble-systeme.puml |
| Changement BLE | 01-architecture-globale.puml, 05-sequence-fonctionnement-global.puml |
| Nouveau composant | 01-architecture-globale.puml, 02-vue-ensemble-systeme.puml |
| Changement déploiement | 06-diagramme-deploiement.puml |

---

## Ressources Complémentaires

### Documentation PlantUML
- **Site officiel** : https://plantuml.com/
- **Guide de syntaxe** : https://plantuml.com/guide
- **Exemples** : https://real-world-plantuml.com/

### Documentation Projet
- **README Principal** : [`../../README.md`](../../README.md)
- **README Application** : [`../../app/README.md`](../../app/README.md)
- **README Robot** : [`../../robot/README.md`](../../robot/README.md)

### Support
Pour toute question sur les diagrammes, contacter l'équipe projet :
- **Paul MARTINEZ** - [LinkedIn](https://www.linkedin.com/in/paul-martinez-paul/)
- **Guilherme De Conte Mazur** - [LinkedIn](https://www.linkedin.com/in/guilherme-de-conte-mazur/)
- **Phu Khong** - [LinkedIn](https://www.linkedin.com/in/phu-khong-7b484721b/)

---

**Développé avec ❤️ par Paul MARTINEZ, Guilherme DE CONTE MAZUR, Phu KHONG**  
**Documentation : Décembre 2025**
