"""
Gestionnaire WebSocket pour les notifications BLE
Gère la diffusion des notifications à tous les clients connectés
"""
from typing import List, Set
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    Gestionnaire de connexions WebSocket
    Permet la diffusion de messages à tous les clients connectés
    """
    
    def __init__(self):
        """Initialise le gestionnaire avec une liste vide de connexions"""
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """
        Ajoute une nouvelle connexion WebSocket
        
        Args:
            websocket: La connexion WebSocket à ajouter
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"✓ Client WebSocket connecté. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """
        Supprime une connexion WebSocket
        
        Args:
            websocket: La connexion WebSocket à supprimer
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"✓ Client WebSocket déconnecté. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: str):
        """
        Diffuse un message à tous les clients connectés
        
        Args:
            message: Le message à diffuser (JSON)
        """
        if not self.active_connections:
            logger.debug("Aucun client WebSocket connecté pour la diffusion")
            return
        
        # Copier la liste pour éviter les modifications pendant l'itération
        connections_copy = self.active_connections.copy()
        
        for connection in connections_copy:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi WebSocket: {str(e)}")
                # Supprimer la connexion défectueuse
                self.disconnect(connection)
    
    async def broadcast_json(self, data: dict):
        """
        Diffuse un message JSON à tous les clients connectés
        
        Args:
            data: Le dictionnaire à envoyer (sera sérialisé en JSON)
        """
        import json
        await self.broadcast(json.dumps(data))
    
    def get_connection_count(self) -> int:
        """
        Retourne le nombre de connexions actives
        
        Returns:
            Nombre de clients WebSocket connectés
        """
        return len(self.active_connections)


# Instance globale du gestionnaire
manager = WebSocketManager()
