"""
Gestionnaire de connexion Bluetooth Low Energy (BLE)
Gère la communication avec le robot Arduino via BLE
"""
import asyncio
from bleak import BleakClient, BleakScanner
from typing import Optional, Dict
import logging
import json
import re

from app.api.websocket_manager import manager as connection_manager

# Configuration du logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration BLE
ADDRESS = "48:87:2d:76:b3:1d"
# UUID_WRITE en format standard Bluetooth (16-bit 0xFFE2 -> UUID 128-bit)
UUID_WRITE = "0000ffe2-0000-1000-8000-00805f9b34fb"
# UUID_NOTIFY en format standard Bluetooth (16-bit 0xFFE1 -> UUID 128-bit)
UUID_WRITENOTIFY = "0000ffe1-0000-1000-8000-00805f9b34fb"

# Images prédéfinies pour la matrice LED (16 bytes chacune)
# IMAGES = {
#     'heart': bytes([0x00, 0x00, 0x00, 0x0c, 0x1e, 0x3f, 0x7f, 0xfe, 0xfe, 0x7f, 0x3f, 0x1e, 0x0c, 0x00, 0x00, 0x00]),
#     'cross': bytes([0x81, 0x42, 0x24, 0x18, 0x18, 0x24, 0x42, 0x81, 0x81, 0x42, 0x24, 0x18, 0x18, 0x24, 0x42, 0x81]),
#     'ok': bytes([0x0, 0x0, 0x0, 0x38, 0x44, 0x44, 0x38, 0x0, 0x0, 0x7c, 0x10, 0x28, 0x44, 0x0, 0x0, 0x0]),
#     'warning': bytes([0x0, 0x0, 0x5e, 0x5e, 0x0, 0x0, 0x0, 0x5e, 0x5e, 0x0, 0x0, 0x0, 0x5e, 0x5e, 0x0, 0x0]),
#     'smile': bytes([0x00, 0x00, 0x00, 0x10, 0x20, 0x40, 0x46, 0x40, 0x40, 0x46, 0x40, 0x20, 0x10, 0x00, 0x00, 0x00]),
#     'sad': bytes([0x00, 0x00, 0x00, 0x00, 0x40, 0x24, 0x20, 0x20, 0x20, 0x20, 0x24, 0x40, 0x00, 0x00, 0x00, 0x00]),
#     'neutral': bytes([0x0, 0x0, 0x0, 0x3c, 0x42, 0x95, 0x81, 0x42, 0x42, 0x81, 0x91, 0x42, 0x3c, 0x0, 0x0, 0x0]),
#     'arrow_up': bytes([0x0, 0x10, 0x38, 0x7c, 0xfe, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x0, 0x0, 0x0]),
#     'arrow_down': bytes([0x0, 0x0, 0x0, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0xfe, 0x7c, 0x38, 0x10, 0x0, 0x0]),
#     'arrow_left': bytes([0x0, 0x0, 0x10, 0x30, 0x78, 0xfe, 0x78, 0x30, 0x10, 0x10, 0x10, 0x10, 0x10, 0x0, 0x0, 0x0]),
#     'arrow_right': bytes([0x0, 0x0, 0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x78, 0xfe, 0x78, 0x30, 0x10, 0x0, 0x0, 0x0]),
#     'stop': bytes([0x0, 0x0, 0x0, 0x7e, 0x7e, 0x7e, 0x7e, 0x7e, 0x7e, 0x7e, 0x7e, 0x7e, 0x0, 0x0, 0x0, 0x0]),
#     'off': bytes([0x0, 0x3c, 0x42, 0x42, 0x3c, 0x0, 0x7e, 0xa, 0xa, 0x2, 0x0, 0x7e, 0xa, 0xa, 0x2, 0x0])
# }


class BLEConnectionManager:
    """
    Gestionnaire de connexion Bluetooth Low Energy persistante
    Gère la connexion, déconnexion et envoi de données au robot
    """
    
    def __init__(self, address: str = ADDRESS, uuid_write: str = UUID_WRITENOTIFY, uuid_notify: str = UUID_WRITENOTIFY):
        """
        Initialise le gestionnaire BLE
        
        Args:
            address: Adresse MAC du device Bluetooth
            uuid_write: UUID de la caractéristique GATT pour écriture
        """
        self.address = address
        self.uuid_write = uuid_write
        self.uuid_notify = uuid_notify
        self.client: Optional[BleakClient] = None
        self.is_connected = False
        self._connecting = False  # Flag simple pour éviter les connexions multiples
    
    async def connect(self) -> Dict[str, any]:
        """
        Établit la connexion avec le device BLE
        
        Returns:
            Dict avec status et message
        """
        if self._connecting or self.is_connected:
            if self.is_connected:
                logger.info("Déjà connecté au device")
                return {"success": True, "message": "Déjà connecté", "address": self.address}
            else:
                return {"success": False, "message": "Connexion en cours..."}
        
        self._connecting = True
        
        try:
            self.client = BleakClient(self.address)
            await self.client.connect()
            self.is_connected = True
            self._connecting = False
            logger.info(f"✓ Connecté au device {self.address}")
            await self.start_notifications()
            return {"success": True, "message": "Connexion réussie", "address": self.address}
        
        except Exception as e:
            error_msg = f"Erreur de connexion : {str(e)}"
            logger.error(f"✗ {error_msg}")
            self.is_connected = False
            self._connecting = False
            return {"success": False, "message": error_msg}
    
    async def disconnect(self) -> Dict[str, any]:
        """
        Ferme la connexion BLE
        
        Returns:
            Dict avec status et message
        """
        if not self.client or not self.is_connected:
            return {"success": True, "message": "Déjà déconnecté"}
        
        try:
            await self.stop_notifications()
            await self.client.disconnect()
            self.is_connected = False
            self._connecting = False
            logger.info("✓ Déconnecté")
            return {"success": True, "message": "Déconnexion réussie"}
        
        except Exception as e:
            error_msg = f"Erreur lors de la déconnexion : {str(e)}"
            logger.error(f"✗ {error_msg}")
            self.is_connected = False
            return {"success": False, "message": error_msg}
    
    async def send_data(self, data: bytes) -> bool:
        """
        Envoie des données via BLE
        
        Args:
            data: Données à envoyer (bytes)
        
        Returns:
            True si envoi réussi, False sinon
        """
        if not self.is_connected:
            logger.error("✗ Non connecté. Connexion requise.")
            return False
        
        try:
            # Logs détaillés pour diagnostic
            hex_str = ' '.join(f'{b:02X}' for b in data)
            logger.info(f"📤 Envoi de {len(data)} bytes via BLE ({self.uuid_write})")
            logger.info(f"   Données (hex): {hex_str}")
            logger.info(f"   Données (ascii): {repr(data)}")
            
            await self.client.write_gatt_char(self.uuid_write, data)
            logger.info(f"✓ Données envoyées avec succès")
            return True
        
        except Exception as e:
            logger.error(f"✗ Erreur lors de l'envoi : {str(e)}")
            self.is_connected = False
            return False
    
    # async def send_message(self, message: str) -> bool:
    #     """
    #     Envoie un message texte à la matrice LED
        
    #     Args:
    #         message: Texte à afficher (max 15 caractères)
        
    #     Returns:
    #         True si envoi réussi
    #     """
    #     message_bytes = message.encode('utf-8')[:15]
    #     message_buffer = bytes([0x01]) + message_bytes.ljust(15, b'\x00')
        
    #     logger.info(f"💬 Envoi message: '{message}' (longueur: {len(message_bytes)} chars)")
    #     logger.info(f"   Header: 0x01 (type=texte)")
    #     logger.info(f"   Buffer complet: {' '.join(f'{b:02X}' for b in message_buffer)}")
        
    #     result = await self.send_data(message_buffer)
        
    #     if result:
    #         logger.info(f"✓ Message envoye avec succès")
    #     return result
    
    # async def send_image(self, image_name: str) -> bool:
    #     """
    #     Envoie une image predefinie a la matrice LED
        
    #     Args:
    #         image_name: Nom de l'image (heart, smile, sad, etc.)
        
    #     Returns:
    #         True si envoi reussi
    #     """
    #     if image_name not in IMAGES:
    #         logger.error(f"✗ Image inconnue : {image_name}")
    #         logger.error(f"   Images disponibles: {list(IMAGES.keys())}")
    #         return False
        
    #     image = IMAGES[image_name]
    #     image_data = bytes([0x02]) + image
        
    #     logger.info(f"🖼️  Envoi image: '{image_name}' (16 bytes)")
    #     logger.info(f"   Header: 0x02 (type=image)")
    #     logger.info(f"   Data (hex): {' '.join(f'{b:02X}' for b in image)}")
    #     logger.info(f"   Buffer complet: {' '.join(f'{b:02X}' for b in image_data)}")
        
    #     result = await self.send_data(image_data)
        
    #     if result:
    #         logger.info(f"✓ Image envoyee avec succès")
    #     return result
    
    # async def control_motor(self, command: str, speed: int = 255) -> bool:
    #     """
    #     Envoie une commande aux moteurs
        
    #     Args:
    #         command: 'forward', 'backward', 'left', 'right', 'stop'
    #         speed: Vitesse (0-255)
        
    #     Returns:
    #         True si envoi reussi
    #     """
    #     valid_commands = ['forward', 'backward', 'left', 'right', 'stop']
    #     if command not in valid_commands:
    #         logger.error(f"✗ Commande invalide : {command}")
    #         return False
        
    #     # Protocole moteur: 0x03 + command_byte + speed
    #     command_map = {'forward': 0x01, 'backward': 0x02, 'left': 0x03, 'right': 0x04, 'stop': 0x00}
    #     motor_data = bytes([0x03, command_map[command], speed])
        
    #     result = await self.send_data(motor_data)
        
    #     if result:
    #         logger.info(f"✓ Moteur : {command} (speed={speed})")
    #     return result
    
    async def get_status(self) -> Dict[str, any]:
        """
        Récupère le statut de la connexion
        
        Returns:
            Dict avec informations de connexion
        """
        return {
            "connected": self.is_connected,
            "address": self.address,
            "uuid_write": self.uuid_write
        }
    
    async def scan_devices(self, timeout: float = 5.0) -> list:
        """
        Scanne les devices BLE à proximité
        
        Args:
            timeout: Durée du scan en secondes
        
        Returns:
            Liste des devices trouvés
        """
        try:
            logger.info(f"Scan BLE en cours ({timeout}s)...")
            devices = await BleakScanner.discover(timeout=timeout)
            
            device_list = []
            for device in devices:
                device_list.append({
                    "address": device.address,
                    "name": device.name or "Unknown",
                    "rssi": device.rssi
                })
            
            logger.info(f"✓ {len(device_list)} device(s) trouvé(s)")
            return device_list
        
        except Exception as e:
            logger.error(f"✗ Erreur lors du scan : {str(e)}")
            return []
        
    async def _notification_handler(self, sender, data):
        """
        Gère les notifications BLE entrantes et les diffuse via WebSocket.
        Parse les paquets de télémétrie et événements pour stockage en BDD.
        """
        hex_str = ' '.join(f'{b:02X}' for b in data)
        logger.info(f"🔔 Notification BLE reçue (sender {sender}): {hex_str}")
        
        # Décoder le texte
        text = None
        try:
            text = data.decode('utf-8', errors='ignore').strip()
            if text:
                logger.info(f"   ASCII: {text}")
        except:
            pass
        
        # Préparer les données de notification
        notification_data = {
            "type": "ble_notification",
            "sender": str(sender),
            "hex": hex_str,
            "bytes": [int(b) for b in data],
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        if text:
            notification_data["text"] = text
            
            # Parser les paquets de télémétrie (JSON)
            if text.startswith('{') and text.endswith('}'):
                try:
                    telemetry = json.loads(text)
                    if 'uptime_s' in telemetry or 'mode' in telemetry:
                        # C'est un paquet de télémétrie
                        await self._store_telemetry(telemetry)
                        notification_data["telemetry"] = telemetry
                        logger.info(f"📊 Télémétrie stockée: {telemetry}")
                except json.JSONDecodeError:
                    pass
            
            # Parser les événements spéciaux
            elif any(keyword in text.lower() for keyword in ['auto', 'manual', 'lights', 'obstacle', 'emergency', 'stop']):
                await self._store_event(text)
                notification_data["event"] = text
                logger.info(f"⚡ Événement détecté: {text}")
        
        # Diffuser via WebSocket
        await connection_manager.broadcast(json.dumps(notification_data))

    async def start_notifications(self):
        """
        Active les notifications pour la caractéristique spécifiée.
        """
        if not self.client or not self.is_connected:
            logger.warning("Non connecté, impossible d'activer les notifications.")
            return {"success": False, "message": "Non connecté."}

        try:
            logger.info(f"💡 Activation des notifications pour {self.uuid_notify}")
            
            # Vérifier que la caractéristique existe
            char = None
            try:
                for service in self.client.services:
                    for characteristic in service.characteristics:
                        if characteristic.uuid.lower() == self.uuid_notify.lower():
                            char = characteristic
                            logger.info(f"✓ Caractéristique trouvée: {characteristic.uuid}")
                            break
                    if char:
                        break
                
                if not char:
                    logger.warning(f"⚠️ Caractéristique {self.uuid_notify} non trouvée. Services disponibles:")
                    for service in self.client.services:
                        logger.warning(f"  Service: {service.uuid}")
                        for char in service.characteristics:
                            logger.warning(f"    - {char.uuid}")
            except Exception as e:
                logger.warning(f"⚠️ Erreur lors de l'énumération des caractéristiques: {str(e)}")
            
            await self.client.start_notify(self.uuid_notify, self._notification_handler)
            logger.info("✓ Notifications activées.")
            return {"success": True, "message": "Notifications activées."}
        except Exception as e:
            logger.error(f"✗ Erreur lors de l'activation des notifications : {str(e)}")
            return {"success": False, "message": f"Erreur: {str(e)}"}

    async def stop_notifications(self):
        """
        Désactive les notifications pour la caractéristique spécifiée.
        """
        if not self.client or not self.is_connected:
            return {"success": True, "message": "Déjà déconnecté ou notifications non actives."}
        try:
            logger.info(f"🔕 Désactivation des notifications pour {self.uuid_notify}")
            await self.client.stop_notify(self.uuid_notify)
            logger.info("✓ Notifications désactivées.")
            return {"success": True, "message": "Notifications désactivées."}
        except Exception as e:
            logger.error(f"✗ Erreur lors de la désactivation des notifications : {str(e)}")
            return {"success": False, "message": f"Erreur: {str(e)}"}
        

    async def _store_telemetry(self, telemetry: dict):
        """Stocke un paquet de télémétrie en base de données"""
        try:
            from app.models.database import SessionLocal
            from app.models.telemetry import Telemetry
            import hashlib
            import uuid
            from datetime import datetime
            
            db = SessionLocal()
            try:
                # Générer un ID unique et checksum
                packet_str = json.dumps(telemetry, sort_keys=True)
                packet_id = str(uuid.uuid4())
                checksum = hashlib.sha256(packet_str.encode()).hexdigest()
                
                telem = Telemetry(
                    packet_id=packet_id,
                    timestamp=datetime.utcnow(),
                    uptime_s=telemetry.get('uptime_s'),
                    mode=telemetry.get('mode'),
                    distance_cm=telemetry.get('distance_cm'),
                    obstacle_events=telemetry.get('obstacle_events'),
                    last_ir_cmd=telemetry.get('last_ir_cmd'),
                    speed_pwm=telemetry.get('speed_pwm'),
                    dist_traveled_cm=telemetry.get('dist_traveled_cm'),
                    battery_level=telemetry.get('battery_level'),
                    signal_strength=telemetry.get('signal_strength'),
                    packet_raw=packet_str,
                    checksum=checksum,
                    processed=True
                )
                db.add(telem)
                db.commit()
                logger.info(f"✓ Télémétrie enregistrée (ID: {telem.id}, Checksum: {checksum[:8]}...)")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"✗ Erreur stockage télémétrie: {e}")
    
    async def _store_event(self, event_text: str):
        """Stocke un événement en base de données"""
        try:
            from app.models.database import SessionLocal
            from app.models.telemetry import Event
            from datetime import datetime
            import uuid
            
            # Déterminer le type d'événement et sa sévérité
            event_type = "unknown"
            description = event_text
            value = None
            new_value = None
            category = "info"
            severity = 1
            
            text_lower = event_text.lower()
            
            if 'auto' in text_lower:
                event_type = "mode_change"
                value = "manual"
                new_value = "auto"
                description = "Passage en mode automatique"
                category = "info"
                severity = 1
            elif 'manual' in text_lower or 'manuel' in text_lower:
                event_type = "mode_change"
                value = "auto"
                new_value = "manual"
                description = "Passage en mode manuel"
                category = "info"
                severity = 1
            elif 'lights' in text_lower or 'lumière' in text_lower:
                event_type = "lights_toggle"
                value = "off" if 'on' in text_lower else "on"
                new_value = "on" if 'on' in text_lower else "off"
                description = f"Lumières {new_value}"
                category = "info"
                severity = 1
            elif 'obstacle' in text_lower:
                event_type = "obstacle_detected"
                description = "Obstacle détecté"
                category = "warning"
                severity = 2
            elif 'emergency' in text_lower or 'urgence' in text_lower:
                event_type = "emergency_stop"
                description = "Arrêt d'urgence"
                category = "critical"
                severity = 4
            elif 'battery' in text_lower or 'batterie' in text_lower:
                event_type = "battery_low"
                description = "Batterie faible"
                category = "warning"
                severity = 2
            elif 'disconnect' in text_lower or 'connection' in text_lower:
                event_type = "connection"
                description = event_text
                category = "warning"
                severity = 2
            
            db = SessionLocal()
            try:
                event = Event(
                    event_id=str(uuid.uuid4()),
                    timestamp=datetime.utcnow(),
                    event_type=event_type,
                    category=category,
                    description=description,
                    value=value,
                    new_value=new_value,
                    source="bluetooth",
                    raw_data=event_text,
                    severity_level=severity,
                    processed=True
                )
                db.add(event)
                db.commit()
                logger.info(f"✓ Événement enregistré: {event_type} [{category}] - {description}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"✗ Erreur stockage événement: {e}")


# Instance globale du gestionnaire
ble_manager = BLEConnectionManager()


async def send_image(image) -> bool:
    """ Envoie une image à la matrice LED """
    image_data = bytes([0x02]) + image
    if await ble_manager.send_data(image_data):
        print("✓ Image envoyée !")
    return True


async def send_message(message: str) -> bool:
    """
    Envoie un message texte au device
    
    Args:
        message: Texte à afficher (max 15 caractères)
    
    Returns:
        True si envoi réussi
    """
    # Tronquer à 15 caractères et encoder en UTF-8
    message_bytes = message.encode('utf-8')[:15]
    
    # Protocole : 0x01 + message (padded à 15 bytes)
    message_buffer = bytes([0x01]) + message_bytes.ljust(15, b'\x00')
    
    result = await ble_manager.send_data(message_buffer)
    
    if result:
        logger.info(f"✓ Message envoyé : '{message}'")
    return result

async def read_notif(sender: int, data: bytearray):
    """ Callback pour les notifications reçues """
    hex_str = ' '.join(f'{b:02X}' for b in data)
    try:
        ascii_str = data.decode('utf-8', errors='ignore').strip()
        logger.info(f"📥 Notification reçue: {ascii_str}")
    except Exception as e:
        logger.info(f"📥 Notification reçue: Erreur décodage: {str(e)}")