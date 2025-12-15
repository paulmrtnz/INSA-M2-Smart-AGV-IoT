/**
 * Client JavaScript pour l'API Bluetooth IoT Robot
 * Utilisez ces fonctions dans votre dashboard.html
 */

// ============================================================
// Configuration
// ============================================================

const API_BASE_URL = 'http://localhost:5000/api';

// ============================================================
// Helpers HTTP
// ============================================================

/**
 * Helper pour faire des requêtes GET
 */
async function apiGet(endpoint) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`);
        const data = await response.json();
        return { success: response.ok, data, status: response.status };
    } catch (error) {
        console.error('API GET Error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Helper pour faire des requêtes POST
 */
async function apiPost(endpoint, body = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body)
        });
        const data = await response.json();
        return { success: response.ok, data, status: response.status };
    } catch (error) {
        console.error('API POST Error:', error);
        return { success: false, error: error.message };
    }
}

// ============================================================
// API Bluetooth - Connexion
// ============================================================

/**
 * Se connecter au robot via Bluetooth
 */
async function connectBluetooth() {
    console.log('🔌 Connexion au robot...');
    const result = await apiPost('/ble/connect');
    
    if (result.success) {
        console.log('✅ Connecté:', result.data);
        return result.data;
    } else {
        console.error('❌ Erreur de connexion:', result.data);
        return null;
    }
}

/**
 * Se déconnecter du robot
 */
async function disconnectBluetooth() {
    console.log('🔌 Déconnexion...');
    const result = await apiPost('/ble/disconnect');
    
    if (result.success) {
        console.log('✅ Déconnecté');
        return true;
    } else {
        console.error('❌ Erreur de déconnexion');
        return false;
    }
}

/**
 * Obtenir le statut de la connexion
 */
async function getBluetoothStatus() {
    const result = await apiGet('/ble/status');
    return result.success ? result.data : null;
}

/**
 * Scanner les appareils Bluetooth à proximité
 */
async function scanDevices(timeout = 5) {
    console.log(`🔍 Scan des appareils (${timeout}s)...`);
    const result = await apiGet(`/ble/scan?timeout=${timeout}`);
    
    if (result.success) {
        console.log(`✅ ${result.data.count} appareil(s) trouvé(s):`, result.data.devices);
        return result.data.devices;
    } else {
        console.error('❌ Erreur de scan');
        return [];
    }
}

// ============================================================
// API Bluetooth - Messages
// ============================================================

/**
 * Envoyer un message texte au robot
 */
async function sendMessage(message) {
    if (message.length > 15) {
        console.warn('⚠️ Message tronqué à 15 caractères');
        message = message.substring(0, 15);
    }
    
    console.log(`📤 Envoi du message: "${message}"`);
    const result = await apiPost('/ble/message', { message });
    
    if (result.success) {
        console.log('✅ Message envoyé');
        return true;
    } else {
        console.error('❌ Échec de l\'envoi:', result.data);
        return false;
    }
}

// ============================================================
// API Bluetooth - Images LED
// ============================================================

/**
 * Envoyer une image prédéfinie à la matrice LED
 */
async function sendImage(imageName) {
    console.log(`🖼️ Envoi de l'image: ${imageName}`);
    const result = await apiPost('/ble/image', { name: imageName });
    
    if (result.success) {
        console.log('✅ Image envoyée');
        return true;
    } else {
        console.error('❌ Échec de l\'envoi:', result.data);
        return false;
    }
}

/**
 * Envoyer une image personnalisée (16 bytes)
 */
async function sendCustomImage(imageData) {
    if (!Array.isArray(imageData) || imageData.length !== 16) {
        console.error('❌ L\'image doit être un array de 16 bytes');
        return false;
    }
    
    console.log('🖼️ Envoi image personnalisée');
    const result = await apiPost('/ble/image', { data: imageData });
    
    if (result.success) {
        console.log('✅ Image personnalisée envoyée');
        return true;
    } else {
        console.error('❌ Échec de l\'envoi:', result.data);
        return false;
    }
}

/**
 * Obtenir la liste des images disponibles
 */
async function getAvailableImages() {
    const result = await apiGet('/images/list');
    return result.success ? result.data.images : [];
}

// ============================================================
// API Bluetooth - Moteurs
// ============================================================

/**
 * Contrôler les moteurs du robot
 */
async function controlMotor(command, speed = 255) {
    const validCommands = ['forward', 'backward', 'left', 'right', 'stop'];
    
    if (!validCommands.includes(command)) {
        console.error(`❌ Commande invalide. Utilisez: ${validCommands.join(', ')}`);
        return false;
    }
    
    console.log(`🚗 Commande moteur: ${command} (vitesse: ${speed})`);
    const result = await apiPost('/ble/motor', { command, speed });
    
    if (result.success) {
        console.log('✅ Commande exécutée');
        return true;
    } else {
        console.error('❌ Échec de la commande:', result.data);
        return false;
    }
}

// ============================================================
// Helpers moteurs (raccourcis)
// ============================================================

async function moveForward(speed = 255) {
    return await controlMotor('forward', speed);
}

async function moveBackward(speed = 255) {
    return await controlMotor('backward', speed);
}

async function turnLeft(speed = 200) {
    return await controlMotor('left', speed);
}

async function turnRight(speed = 200) {
    return await controlMotor('right', speed);
}

async function stopMotors() {
    return await controlMotor('stop', 0);
}

// ============================================================
// API - Informations système
// ============================================================

/**
 * Vérifier la santé de l'API
 */
async function checkHealth() {
    const result = await apiGet('/health');
    return result.success ? result.data : null;
}

/**
 * Obtenir les informations système
 */
async function getSystemInfo() {
    const result = await apiGet('/info');
    return result.success ? result.data : null;
}

// ============================================================
// Classe principale Robot Controller
// ============================================================

class RobotController {
    constructor() {
        this.isConnected = false;
    }
    
    async connect() {
        const result = await connectBluetooth();
        this.isConnected = result !== null;
        return this.isConnected;
    }
    
    async disconnect() {
        const result = await disconnectBluetooth();
        this.isConnected = !result;
        return result;
    }
    
    async status() {
        return await getBluetoothStatus();
    }
    
    // Messages
    async sendText(message) {
        return await sendMessage(message);
    }
    
    // Images
    async displayImage(imageName) {
        return await sendImage(imageName);
    }
    
    async displayCustomImage(imageData) {
        return await sendCustomImage(imageData);
    }
    
    // Moteurs
    async forward(speed) {
        return await moveForward(speed);
    }
    
    async backward(speed) {
        return await moveBackward(speed);
    }
    
    async left(speed) {
        return await turnLeft(speed);
    }
    
    async right(speed) {
        return await turnRight(speed);
    }
    
    async stop() {
        return await stopMotors();
    }
}

// ============================================================
// Exemples d'utilisation
// ============================================================

/*

// Utilisation simple avec fonctions
async function demo() {
    // Se connecter
    await connectBluetooth();
    
    // Envoyer un message
    await sendMessage('Hello!');
    
    // Afficher un coeur
    await sendImage('heart');
    
    // Avancer
    await moveForward(200);
    
    // Attendre 2 secondes
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Arrêter
    await stopMotors();
    
    // Se déconnecter
    await disconnectBluetooth();
}

// Utilisation avec la classe RobotController
async function demoClass() {
    const robot = new RobotController();
    
    await robot.connect();
    await robot.sendText('Bonjour');
    await robot.displayImage('smile');
    await robot.forward(200);
    
    setTimeout(async () => {
        await robot.stop();
        await robot.disconnect();
    }, 2000);
}

// Exemple avec contrôle clavier
document.addEventListener('keydown', async (event) => {
    switch(event.key) {
        case 'ArrowUp':
            await moveForward();
            break;
        case 'ArrowDown':
            await moveBackward();
            break;
        case 'ArrowLeft':
            await turnLeft();
            break;
        case 'ArrowRight':
            await turnRight();
            break;
        case ' ':
            await stopMotors();
            break;
    }
});

*/
