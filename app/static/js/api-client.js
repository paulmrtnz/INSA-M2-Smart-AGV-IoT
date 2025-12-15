/**
 * Client JavaScript pour l'API FastAPI Bluetooth IoT Robot
 */

// Configuration de base
const API_BASE_URL = '/api';
let ws = null; // WebSocket pour les notifications BLE

// Helper pour afficher les logs
function log(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);
    const consoleEl = document.getElementById('console');
    if (consoleEl) {
        const timestamp = new Date().toLocaleTimeString();
        const color = type === 'error' ? 'text-red-400' : 
                      type === 'success' ? 'text-green-400' : 
                      type === 'notification' ? 'text-yellow-400' :
                      'text-blue-400';
        consoleEl.innerHTML += `<div class="${color}">[${timestamp}] ${message}</div>`;
        consoleEl.scrollTop = consoleEl.scrollHeight;
    }
}

/**
 * Met à jour les indicateurs en fonction des événements Bluetooth reçus
 */
function updateIndicatorsFromEvent(notification) {
    const text = notification.text ? notification.text.toLowerCase() : '';
    
    // Mode Auto
    if (text.includes('event:auto_mode')) {
        const autoIndi = document.getElementById('indi-auto');
        const manuIndi = document.getElementById('indi-manu');
        if (autoIndi && manuIndi) {
            autoIndi.classList.add('active');
            manuIndi.classList.remove('active');
            log('Mode AUTO activé', 'success');
        }
    }
    
    // Mode Manuel
    if (text.includes('event:manual_mode')) {
        const autoIndi = document.getElementById('indi-auto');
        const manuIndi = document.getElementById('indi-manu');
        if (autoIndi && manuIndi) {
            autoIndi.classList.remove('active');
            manuIndi.classList.add('active');
            log('Mode MANUEL activé', 'success');
        }
    }
    
    // Phares activés
    if (text.includes('event:headlights_on')) {
        const lightsIndi = document.getElementById('indi-lights');
        if (lightsIndi) {
            lightsIndi.classList.add('active');
            log('Phares ACTIVÉS', 'success');
        }
    }
    
    // Phares désactivés
    if (text.includes('event:headlights_off')) {
        const lightsIndi = document.getElementById('indi-lights');
        if (lightsIndi) {
            lightsIndi.classList.remove('active');
            log('Phares DÉSACTIVÉS', 'info');
        }
    }
    
    // Obstacle détecté
    if (text.includes('event:obstacle_detected')) {
        const obstacleIndi = document.getElementById('indi-obstacle');
        if (obstacleIndi) {
            obstacleIndi.classList.add('critical');
            log('⚠️ OBSTACLE DÉTECTÉ!', 'error');
            
            // Retirer la classe critical après 3 secondes (si pas d'autre obstacle)
            setTimeout(() => {
                if (obstacleIndi) {
                    obstacleIndi.classList.remove('critical');
                }
            }, 3000);
        }
    }
}

/**
 * Fonction de test pour simuler les événements Bluetooth
 * À utiliser dans la console pour tester: testBLEEvent('event:auto_mode')
 */
function testBLEEvent(eventType) {
    const mockNotification = {
        type: 'ble_notification',
        text: eventType
    };
    updateIndicatorsFromEvent(mockNotification);
}

// Initialiser WebSocket pour les notifications BLE
function initWebSocket() {
    if (ws) {
        return; // Déjà connecté
    }
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/ble-notifications`;
    
    try {
        ws = new WebSocket(wsUrl);
        
        ws.onopen = () => {
            log("Écoute des notifications BLE lancée...", 'success');
        };
        
        ws.onmessage = (event) => {
            try {
                const notification = JSON.parse(event.data);
                
                if (notification.type === 'ble_notification') {
                    // Formater le message
                    let message = `BLE NOTI: `;                    
                    if (notification.text) {
                        message += `${notification.text}`;
                    }
                    log(message, 'notification');
                    
                    // Traiter les événements pour mettre à jour les indicateurs
                    updateIndicatorsFromEvent(notification);
                } else {
                    log(`Données reçues: ${JSON.stringify(notification)}`, 'info');
                }
            } catch (e) {
                log(`Erreur parsing WebSocket: ${e.message}`, 'error');
            }
        };
        
        ws.onerror = (error) => {
            log(`## Erreur WebSocket: ${error}`, 'error');
        };
        
        ws.onclose = () => {
            log('## WebSocket déconnecté', 'error');
            ws = null;
            // Reconnecter après 3 secondes
            setTimeout(() => initWebSocket(), 3000);
        };
    } catch (e) {
        log(`Erreur création WebSocket: ${e.message}`, 'error');
    }
}

// Fermer WebSocket
function closeWebSocket() {
    if (ws) {
        ws.close();
        ws = null;
    }
}

// Gestion de la connexion
async function connectRobot() {
    try {
        log('Connexion en cours...', 'info');
        const response = await fetch(`${API_BASE_URL}/ble/connect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        
        if (response.ok && data.success) {
            log('Connecte au robot!', 'success');
            initWebSocket(); // Initialiser WebSocket pour les notifications
            updateUIConnected(true);
            return true;
        } else {
            log(`Erreur: ${data.message || 'Connexion echouee'}`, 'error');
            return false;
        }
    } catch (error) {
        log(`Erreur: ${error.message}`, 'error');
        return false;
    }
}

async function disconnectRobot() {
    try {
        log('Deconnexion en cours...', 'info');
        const response = await fetch(`${API_BASE_URL}/ble/disconnect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        
        if (response.ok && data.success) {
            log('Deconnecte du robot!', 'success');
            closeWebSocket(); // Fermer WebSocket
            updateUIConnected(false);
            return true;
        } else {
            log(`Erreur: ${data.message || 'Deconnexion echouee'}`, 'error');
            return false;
        }
    } catch (error) {
        log(`Erreur: ${error.message}`, 'error');
        return false;
    }
}

async function getStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/ble/status`);
        const data = await response.json();
        
        if (response.ok) {
            log(`Statut: ${data.connected ? 'Connecte' : 'Deconnecte'} - Device: ${data.device}`, 'info');
            updateUIConnected(data.connected);
            return data;
        } else {
            log('Impossible de recuperer le statut', 'error');
            return null;
        }
    } catch (error) {
        log(`Erreur: ${error.message}`, 'error');
        return null;
    }
}

async function scanDevices() {
    try {
        log('Scan en cours...', 'info');
        const response = await fetch(`${API_BASE_URL}/ble/scan?timeout=5`);
        const data = await response.json();
        
        if (response.ok) {
            log(`${data.count} appareils trouves`, 'success');
            if (data.devices && data.devices.length > 0) {
                data.devices.forEach((device, i) => {
                    log(`  ${i+1}. ${device.name || 'Unknown'} (${device.address})`, 'info');
                });
            }
            return data.devices || [];
        } else {
            log('Erreur lors du scan', 'error');
            return [];
        }
    } catch (error) {
        log(`Erreur: ${error.message}`, 'error');
        return [];
    }
}

// Envoyer un message
async function sendMessage(message) {
    try {
        if (!message || message.length === 0) {
            log('Message vide', 'error');
            return false;
        }
        
        if (message.length > 15) {
            log('Message trop long (max 15 caracteres)', 'error');
            return false;
        }
        
        log(`Envoi message: "${message}"`, 'info');
        const response = await fetch(`${API_BASE_URL}/ble/message`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            log(data.message || 'Message envoye', 'success');
            return true;
        } else {
            log(`Erreur: ${data.message || 'Envoi echoue'}`, 'error');
            return false;
        }
    } catch (error) {
        log(`Erreur: ${error.message}`, 'error');
        return false;
    }
}

// Envoyer une image LED
async function sendImage(imageName) {
    try {
        if (!imageName || imageName.length === 0) {
            log('Nom image vide', 'error');
            return false;
        }
        
        log(`Envoi image: "${imageName}"`, 'info');
        const response = await fetch(`${API_BASE_URL}/ble/image`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: imageName })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            log(data.message || 'Image envoyee', 'success');
            return true;
        } else {
            log(`Erreur: ${data.message || 'Envoi echoue'}`, 'error');
            return false;
        }
    } catch (error) {
        log(`Erreur: ${error.message}`, 'error');
        return false;
    }
}

// Update UI based on connection status
function updateUIConnected(connected) {
    const connectBtn = document.getElementById('connectBtn');
    const disconnectBtn = document.getElementById('disconnectBtn');
    const statusIndicator = document.getElementById('statusIndicator');
    const overlay = document.getElementById('overlay-disconnected');
    
    if (connectBtn) {
        connectBtn.disabled = connected;
        connectBtn.style.opacity = connected ? '0.5' : '1';
    }
    
    if (disconnectBtn) {
        disconnectBtn.disabled = !connected;
        disconnectBtn.style.opacity = !connected ? '0.5' : '1';
    }
    
    if (statusIndicator) {
        const dot = statusIndicator.querySelector('.status-dot');
        const text = statusIndicator.querySelector('span:last-child');
        
        if (dot) {
            dot.classList.remove('connected', 'disconnected');
            dot.classList.add(connected ? 'connected' : 'disconnected');
        }
        
        if (text) {
            text.textContent = connected ? 'Connecté' : 'Déconnecté';
        }
    }

    if (overlay) {
        if (connected) {
            overlay.classList.add('hidden');
        } else {
            overlay.classList.remove('hidden');
        }
    }
}

// Mettre à jour les métriques du dashboard
function updateDashboardMetrics(telemetry) {
    // Vitesse (PWM)
    if (telemetry.speed_pwm !== undefined) {
        const speedEl = document.getElementById('metrique-speed');
        if (speedEl) {
            // Convertir PWM (0-255) en pourcentage
            const speedPercent = Math.round((telemetry.speed_pwm / 255) * 100);
            speedEl.textContent = `${speedPercent}%`;
        }
    }
    
    // Temps de fonctionnement (session)
    if (telemetry.uptime_s !== undefined) {
        const timeEl = document.getElementById('metrique-time-session');
        if (timeEl) {
            timeEl.textContent = `${telemetry.uptime_s}s`;
        }
    }
    
    // Distance parcourue (session)
    if (telemetry.dist_traveled_cm !== undefined) {
        const distSessionEl = document.getElementById('metrique-distance-session');
        if (distSessionEl) {
            const distMeters = (telemetry.dist_traveled_cm / 100).toFixed(2);
            distSessionEl.textContent = `${distMeters} m`;
        }
    }
    
    // Distance totale
    if (telemetry.distance_cm !== undefined) {
        const distEl = document.getElementById('metrique-distance');
        if (distEl) {
            const distMeters = (telemetry.distance_cm / 100).toFixed(2);
            distEl.textContent = `${distMeters} m`;
        }
    }
    
    // Intensité lumineuse
    if (telemetry.light_level !== undefined) {
        const lightEl = document.getElementById('metrique-light-intensity');
        if (lightEl) {
            lightEl.textContent = `${telemetry.light_level} lux`;
        }
    }
    
    // Batterie
    if (telemetry.battery_level !== undefined) {
        const batteryNum = document.getElementById('battery-num');
        if (batteryNum) {
            batteryNum.textContent = `${telemetry.battery_level}%`;
        }
        fetchBattery(telemetry.battery_level);
    }
    
    // Mode
    if (telemetry.mode) {
        const autoIndi = document.getElementById('indi-auto');
        const manuIndi = document.getElementById('indi-manu');
        
        if (telemetry.mode.toLowerCase().includes('auto') || telemetry.mode.toUpperCase() === 'AUTO') {
            autoIndi?.classList.add('active');
            manuIndi?.classList.remove('active');
        } else if (telemetry.mode.toLowerCase().includes('manual') || telemetry.mode.toLowerCase().includes('manu')) {
            autoIndi?.classList.remove('active');
            manuIndi?.classList.add('active');
        }
    }
    
    // Détection d'obstacle
    if (telemetry.distance_cm !== undefined) {
        const obstacleIndi = document.getElementById('indi-obstacle');
        if (obstacleIndi) {
            if (telemetry.distance_cm < 20) {
                obstacleIndi.classList.add('critical');
            } else {
                obstacleIndi.classList.remove('critical');
            }
        }
    }
}

// Gérer les événements spéciaux
function handleEvent(eventText) {
    const text = eventText.toLowerCase();
    
    if (text.includes('obstacle')) {
        log('⚠️ OBSTACLE DÉTECTÉ!', 'error');
    } else if (text.includes('emergency') || text.includes('stop')) {
        log('🚨 ARRÊT D\'URGENCE!', 'error');
    } else if (text.includes('auto')) {
        log('🤖 Mode automatique activé', 'success');
    } else if (text.includes('manual') || text.includes('manuel')) {
        log('🎮 Mode manuel activé', 'success');
    } else if (text.includes('lights')) {
        log('💡 Lumières modifiées', 'info');
    }
}

// Récupérer la dernière télémétrie au chargement
async function fetchLatestTelemetry() {
    try {
        const response = await fetch(`${API_BASE_URL}/telemetry/latest`);
        const data = await response.json();
        
        if (data.success && data.data) {
            updateDashboardMetrics(data.data);
            // log('Télémétrie chargée', 'info');
        }
    } catch (error) {
        console.error('Erreur chargement télémétrie:', error);
    }
}

/**
 * Charge et affiche les statistiques TOTALES depuis la base de données
 */
async function fetchTotalMetrics() {
    try {
        const response = await fetch(`${API_BASE_URL}/telemetry/total-stats`);
        if (!response.ok) {
            console.error('Erreur lors du chargement des stats totales');
            return;
        }
        
        const data = await response.json();
        
        if (data.success) {
            // Distance totale
            const distEl = document.getElementById('metrique-distance');
            if (distEl) {
                distEl.textContent = `${data.total_distance_m} m`;
            }
            
            // Temps total
            const timeEl = document.getElementById('metrique-time');
            if (timeEl) {
                timeEl.textContent = `${data.total_uptime_hours} h`;
            }
            
            // Obstacles totaux
            const obstaclesEl = document.getElementById('metrique-obstacles');
            if (obstaclesEl) {
                obstaclesEl.textContent = `${data.total_obstacles}`;
            }
            
            log(`Métriques totales mises à jour: ${data.total_distance_m}m, ${data.total_uptime_hours}h, ${data.total_obstacles} obstacles`, 'success');
        }
    } catch (error) {
        console.error('Erreur lors de la récupération des métriques totales:', error);
    }
}

// Export des fonctions globalement
window.connectRobot = connectRobot;
window.disconnectRobot = disconnectRobot;
window.getStatus = getStatus;
window.scanDevices = scanDevices;
window.sendMessage = sendMessage;
window.sendImage = sendImage;
window.updateUIConnected = updateUIConnected;
window.log = log;
window.initWebSocket = initWebSocket;
window.closeWebSocket = closeWebSocket;
window.updateDashboardMetrics = updateDashboardMetrics;
window.fetchLatestTelemetry = fetchLatestTelemetry;
window.fetchTotalMetrics = fetchTotalMetrics;
window.updateIndicatorsFromEvent = updateIndicatorsFromEvent;
window.testBLEEvent = testBLEEvent;

/**
 * Fonction d'initialisation globale du dashboard
 * À appeler après que tous les scripts soient chargés
 */
window.initDashboard = function() {
    console.log("=== INITIALISATION DASHBOARD ===");
    log("Dashboard initialise", "info");

    // Verifier le statut initial
    setTimeout(() => {
        getStatus();
        fetchLatestTelemetry();
        fetchTotalMetrics(); // Charger les métriques totales
    }, 500);

    // Rafraîchir la télémétrie toutes les 5 secondes
    setInterval(() => {
        fetchLatestTelemetry();
    }, 5000);
    
    // Rafraîchir les métriques totales toutes les 30 secondes
    setInterval(() => {
        fetchTotalMetrics();
    }, 30000);
    
    // Attacher les écouteurs d'événements boutons
    console.log("=== ATTACHEMENT DES ÉCOUTEURS ===");
    const connectBtnEl = document.getElementById("connectBtn");
    console.log("connectBtn trouvé:", connectBtnEl);
    
    if (connectBtnEl) {
        connectBtnEl.addEventListener("click", async () => {
            console.log("=== CLIC SUR CONNECTER ===");
            await connectRobot();
        });
    } else {
        console.error("❌ connectBtn introuvable!");
    }

    const disconnectBtnEl = document.getElementById("disconnectBtn");
    console.log("disconnectBtn trouvé:", disconnectBtnEl);
    
    if (disconnectBtnEl) {
        disconnectBtnEl.addEventListener("click", async () => {
            console.log("=== CLIC SUR DÉCONNECTER ===");
            await disconnectRobot();
        });
    }

    const connectBtnOverlay = document.getElementById("connectBtnOverlay");
    if (connectBtnOverlay) {
        connectBtnOverlay.addEventListener("click", async () => {
            console.log("=== CLIC SUR CONNECTER (OVERLAY) ===");
            await connectRobot();
        });
    }
    
    console.log("=== INITIALISATION COMPLÈTE ===");
    log("Dashboard IoT - Pret", "info");
};

