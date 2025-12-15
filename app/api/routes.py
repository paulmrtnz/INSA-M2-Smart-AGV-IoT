from app.api import router
import platform
import sys


@router.get('/health')
def health_check():
    """
    Endpoint de santé de l'API.
    
    Vérifie que l'application fonctionne correctement.
    
    Returns:
        JSON: Status de l'application
    """
    return {
        'status': 'healthy',
        'message': 'API IoT Robot opérationnelle',
        'version': '1.0.0'
    }


@router.get('/info')
def get_info():
    """
    Informations système.
    
    Returns:
        JSON: Informations sur le serveur et l'environnement
    """
    return {
        'platform': platform.system(),
        'python_version': sys.version,
        'architecture': platform.machine(),
        'node': platform.node()
    }


@router.get('/images/list')
def list_images():
    """
    Liste toutes les images prédéfinies disponibles.
    
    Returns:
        JSON: Liste des noms d'images
    """
    from app.services.ble_manager import IMAGES
    
    return {
        'images': list(IMAGES.keys()),
        'count': len(IMAGES)
    }
