# 📊 Diagrammes UML - Résumé des Livrables

## ✅ Mission Accomplie

Tous les diagrammes demandés ont été générés avec succès pour documenter l'architecture complète du projet IoT AGV, en reliant les deux blocs principaux : **l'application web** et **le robot Arduino**.

---

## 📦 Fichiers Créés

### Dossier : `docs/diagrams/`

#### Fichiers Sources PlantUML (.puml)
1. ✅ `01-architecture-globale.puml` (3.3 KB)
2. ✅ `02-vue-ensemble-systeme.puml` (3.5 KB)
3. ✅ `03-machine-etats-robot.puml` (5.0 KB)
4. ✅ `04-machine-etats-application.puml` (5.6 KB)
5. ✅ `05-sequence-fonctionnement-global.puml` (7.1 KB)
6. ✅ `06-diagramme-deploiement.puml` (5.9 KB)

#### Images Générées (.png)
1. ✅ `Architecture_Globale.png` (165 KB)
2. ✅ `Vue_Ensemble_Systeme.png` (195 KB)
3. ✅ `Machine_Etats_Robot.png` (250 KB)
4. ✅ `Machine_Etats_Application.png` (239 KB)
5. ✅ `Fonctionnement_Global.png` (316 KB)
6. ✅ `Diagramme_Deploiement.png` (318 KB)

#### Documentation
7. ✅ `README.md` (10.1 KB) - Guide complet d'utilisation

#### Mises à Jour
8. ✅ `README.md` principal mis à jour avec références aux diagrammes

---

## 📋 Détails des Diagrammes

### 1️⃣ Architecture Globale
**Type** : Diagramme de composants  
**Objectif** : Vue d'ensemble en couches du système complet

**Contenu** :
- ✅ Couche Utilisateur (Navigateur Web)
- ✅ Couche Application Backend (API Layer, Services, Data)
- ✅ Couche Communication (Bluetooth Low Energy)
- ✅ Couche Robot (Capteurs, Actionneurs, Communication)
- ✅ Relations et flux de données entre tous les composants
- ✅ Légende avec stack technologique

**Technologies représentées** :
- Backend : Python 3.8+, FastAPI, Uvicorn
- Frontend : HTML5, JavaScript ES6+, CSS3
- BLE : Bleak 0.21+
- Database : SQLite, SQLAlchemy 2.0+
- Robot : Arduino UNO, C++

---

### 2️⃣ Vue d'Ensemble du Système
**Type** : Diagramme de composants détaillé  
**Objectif** : Interactions entre tous les éléments du système

**Contenu** :
- ✅ Interface Web (Dashboard, Historique, Diagnostic)
- ✅ API REST (25+ endpoints organisés)
- ✅ Services (BLE Manager, WebSocket Manager)
- ✅ Base de données (4 tables : télémétrie, événements, statistiques, logs)
- ✅ Robot AGV (Machine à états, capteurs, actionneurs)
- ✅ Flux de données complets

**Points clés** :
- UUID BLE : 0xFFE1 (Notify), 0xFFE2 (Write)
- Portée Bluetooth : ~10m
- Format données : JSON avec checksum SHA256

---

### 3️⃣ Machine à États du Robot
**Type** : Diagramme d'états UML  
**Objectif** : Comportement détaillé du firmware Arduino

**États principaux** :
1. ✅ **STARTING** : Initialisation matérielle
   - Configuration pins
   - Setup capteurs/actionneurs
   - Affichage logo PGP
   - Démarrage Bluetooth (9600 baud)

2. ✅ **WAITING_BT** : Attente connexion Bluetooth
   - Affichage "Waiting BT..."
   - LED Matrix clignote
   - Moteurs désactivés
   - Écoute messages BT

3. ✅ **MANUAL** : Mode manuel
   - Traitement commandes IR
   - Traitement commandes BLE
   - Contrôle manuel moteurs
   - Gestion phares

4. ✅ **AUTO** : Mode automatique
   - Navigation autonome
   - Suivi de ligne (3 IR)
   - Détection obstacle continue
   - Ajustement vitesse

5. ✅ **OBSTACLE_DETECTED** : Sécurité anti-collision
   - Arrêt immédiat moteurs
   - Affichage LED "!!!"
   - Attente dégagement (distance > 25cm)

**Transitions** :
- ✅ Connexion/Déconnexion BLE
- ✅ Commandes IR (# = auto, * = manual)
- ✅ Commandes BLE ("auto", "manual", "forward", etc.)
- ✅ Détection obstacle (< 25cm)

**Commandes IR documentées** :
- ↑ (0xFF629D) = Avancer
- ↓ (0xFFA857) = Reculer
- ← (0xFF22DD) = Tourner gauche
- → (0xFFC23D) = Tourner droite
- OK (0xFF02FD) = Stop
- # (0xFF52AD) = Mode auto
- * (0xFF42BD) = Mode manuel

---

### 4️⃣ Machine à États de l'Application
**Type** : Diagramme d'états UML  
**Objectif** : Cycle de vie de l'application FastAPI et connexion BLE

**États principaux** :
1. ✅ **INIT** : Initialisation serveur
   - Création instance FastAPI
   - Configuration CORS
   - Montage fichiers statiques
   - Initialisation BDD
   - Enregistrement routers

2. ✅ **READY** : Serveur prêt
   - HTTP actif sur port 8000
   - API REST disponible
   - BLE Manager initialisé (non connecté)
   - WebSocket en écoute

3. ✅ **CONNECTING_BLE** : Tentative connexion
   - Création BleakClient
   - Connexion adresse MAC
   - Timeout 10 secondes
   - Lock asyncio actif

4. ✅ **CONNECTED** : BLE opérationnel
   - Client BLE actif
   - Notifications actives (UUID 0xFFE1)
   - Canal écriture prêt (UUID 0xFFE2)
   - WebSocket diffuse statut

5. ✅ **DISCONNECTING** : Fermeture propre
   - Arrêt notifications
   - Fermeture BleakClient
   - Nettoyage ressources

**Tâches parallèles** :
- ✅ HTTP Request Handling (API REST)
- ✅ WebSocket Connections (notifications temps réel)
- ✅ Database Operations (stockage télémétrie)

---

### 5️⃣ Séquence de Fonctionnement Global
**Type** : Diagramme de séquence UML  
**Objectif** : Scénario complet d'utilisation du système

**Phases détaillées** :

**Phase 1 : Démarrage et Initialisation**
- ✅ Utilisateur accède au dashboard
- ✅ Robot initialise hardware
- ✅ Application prête à recevoir connexions

**Phase 2 : Connexion Bluetooth**
- ✅ Utilisateur clique "Connecter"
- ✅ BLE Manager établit connexion
- ✅ Robot passe en mode MANUAL
- ✅ WebSocket notifie connexion réussie

**Phase 3 : Envoi Commande (Mode Manuel)**
- ✅ Utilisateur clique "Avancer"
- ✅ API envoie commande via BLE
- ✅ Robot exécute mouvement
- ✅ Événement enregistré en BDD

**Phase 4 : Réception Télémétrie**
- ✅ Robot collecte métriques (toutes les 30s)
- ✅ Envoi paquet JSON via BLE
- ✅ Application parse et stocke en BDD
- ✅ WebSocket diffuse aux clients
- ✅ Dashboard mis à jour

**Phase 5 : Passage en Mode Automatique**
- ✅ Utilisateur active mode auto
- ✅ Robot navigue autonomement
- ✅ Suivi de ligne actif
- ✅ Détection obstacles continue
- ✅ Événements envoyés en temps réel

**Phase 6 : Consultation Historique**
- ✅ Utilisateur consulte page historique
- ✅ API requête BDD
- ✅ Affichage graphiques et tableaux

**Phase 7 : Déconnexion**
- ✅ Utilisateur déconnecte
- ✅ Robot retourne en WAITING_BT
- ✅ Moteurs arrêtés
- ✅ Log de connexion enregistré

**Acteurs représentés** :
- Utilisateur
- Navigateur Web
- FastAPI Application
- BLE Manager
- SQLite Database
- WebSocket Manager
- Bluetooth Low Energy (protocole)
- Robot Arduino (BT Manager)
- Robot Controller
- Capteurs/Actionneurs

---

### 6️⃣ Diagramme de Déploiement
**Type** : Diagramme de déploiement UML  
**Objectif** : Architecture physique et logique du système

**Nœuds représentés** :

**1. Poste Développeur/Serveur**
- ✅ Environnement Python 3.8+ (venv)
- ✅ Application FastAPI complète
- ✅ Base de données SQLite
- ✅ Serveur Uvicorn ASGI (port 8000)
- ✅ Tous les modules (API, Services, Models, Static, Templates)

**2. Poste Client (Utilisateur)**
- ✅ Navigateur Web
- ✅ Interface HTML/CSS/JS
- ✅ Client WebSocket
- ✅ Support Chrome/Edge/Firefox/Safari

**3. Robot AGV - Keyestudio KS0555**
- ✅ Arduino UNO (ATmega328P)
- ✅ Module Bluetooth HC-05/06 (9600 baud)
- ✅ Capteurs :
  - HC-SR04 Ultrason
  - 3x IR Ligne
  - Photorésistance
  - Récepteur IR
- ✅ Actionneurs :
  - 2x Moteurs DC + Driver L298N
  - LED Matrix 8x16
- ✅ Alimentation batteries (7-12V)

**Communication** :
- ✅ HTTP/WebSocket (Client ↔ Serveur)
- ✅ Bluetooth Low Energy (Serveur ↔ Robot)
- ✅ Portée BLE : ~10 mètres

---

## 🎯 Utilisation des Diagrammes

### Visualisation en Ligne
1. **PlantUML Online** : https://www.plantuml.com/plantuml/uml/
   - Copier-coller le contenu d'un fichier `.puml`
   - Générer l'image en temps réel

2. **Visual Studio Code**
   - Installer extension "PlantUML" (jebbs.plantuml)
   - Ouvrir fichier `.puml`
   - `Alt+D` pour prévisualiser
   - Clic droit → "Export Current Diagram"

3. **GitHub**
   - Voir directement les images PNG dans le repository
   - Ou consulter le README dans `docs/diagrams/`

### Régénération des Images
```bash
cd docs/diagrams
plantuml -tpng *.puml
```

### Modification des Diagrammes
1. Éditer le fichier `.puml` source
2. Regénérer l'image PNG
3. Commit les deux fichiers (source + image)

---

## 📚 Documentation Complète

### Structure de Documentation
```
docs/diagrams/
├── README.md                              # Guide complet (10 KB)
├── 01-architecture-globale.puml           # Source PlantUML
├── Architecture_Globale.png               # Image générée
├── 02-vue-ensemble-systeme.puml
├── Vue_Ensemble_Systeme.png
├── 03-machine-etats-robot.puml
├── Machine_Etats_Robot.png
├── 04-machine-etats-application.puml
├── Machine_Etats_Application.png
├── 05-sequence-fonctionnement-global.puml
├── Fonctionnement_Global.png
├── 06-diagramme-deploiement.puml
└── Diagramme_Deploiement.png
```

### README des Diagrammes Contient
- ✅ Vue d'ensemble complète
- ✅ Description détaillée de chaque diagramme
- ✅ Instructions d'utilisation
- ✅ Guide d'installation PlantUML
- ✅ Bonnes pratiques de maintenance
- ✅ Légende et conventions
- ✅ Liens vers documentation projet

---

## 🔗 Intégration dans le Projet

### README Principal Mis à Jour
Le fichier `README.md` principal a été enrichi avec :
- ✅ Section "Diagrammes d'Architecture"
- ✅ Lien direct vers `docs/diagrams/README.md`
- ✅ Liste des 6 diagrammes disponibles

### Cohérence
- ✅ Tous les diagrammes sont cohérents entre eux
- ✅ Nomenclature uniforme
- ✅ Technologies alignées avec le code
- ✅ États synchronisés avec le firmware

---

## 🎨 Qualité des Diagrammes

### Format PlantUML
- ✅ **Versionnable** : Format texte compatible Git
- ✅ **Modifiable** : Facile à éditer et maintenir
- ✅ **Générable** : Automatisation possible
- ✅ **Standard** : UML conforme

### Contenu
- ✅ **Complet** : Tous les aspects du système
- ✅ **Détaillé** : Informations techniques précises
- ✅ **Annoté** : Notes explicatives
- ✅ **Légendes** : Technologies et conventions

### Images
- ✅ **Haute résolution** : 165-318 KB par image
- ✅ **Lisible** : Texte clair et organisé
- ✅ **Professionnel** : Style cohérent

---

## ✨ Points Forts

1. **Documentation Complète** : Tous les aspects du système sont couverts
2. **Deux Blocs Reliés** : Application ↔ Robot parfaitement documenté
3. **Multi-Niveaux** : Du global au détail
4. **Maintenable** : Format texte facile à mettre à jour
5. **Professionnel** : Qualité académique/industrielle
6. **Pratique** : README avec guide d'utilisation

---

## 🚀 Pour Aller Plus Loin

### Utilisations Possibles
1. **Présentation projet** : Slides avec images PNG
2. **Documentation technique** : Rapport avec diagrammes
3. **Formation équipe** : Support pédagogique
4. **Maintenance** : Référence pour évolution code
5. **Audit** : Compréhension rapide architecture

### Évolutions Futures
Si le code évolue, mettre à jour :
- Le fichier `.puml` correspondant
- Regénérer l'image PNG
- Vérifier cohérence avec autres diagrammes

---

## 📞 Support

Pour toute question sur les diagrammes :
- **Paul MARTINEZ**
- **Guilherme De Conte Mazur**
- **Phu Khong**

---

**🎉 Mission accomplie avec succès !**

**Développé avec ❤️ par l'équipe projet INSA CVL**  
**Décembre 2025**
