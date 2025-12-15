"""
Configuration de l'application FastAPI
Différentes configurations pour développement, production et tests
"""
import os


class Config:
    """Configuration de base commune à tous les environnements"""
    
    # Configuration Bluetooth
    BLE_DEVICE_ADDRESS = os.environ.get('BLE_DEVICE_ADDRESS') or '48:87:2d:76:b3:1d'
    BLE_UUID_WRITE = os.environ.get('BLE_UUID_WRITE') or 'FFE2'
    
    # Configuration CORS
    CORS_ORIGINS = ["*"]  # En production, spécifier les domaines autorisés
    
    # Limite de taille des requêtes (16 MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024