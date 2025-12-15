"""
Routes API pour le diagnostic et le debogage Bluetooth
Permet de tester la communication avec le robot et afficher les logs
"""
from fastapi import HTTPException
from pydantic import BaseModel, Field
from app.api import router
from app.services.ble_manager import ble_manager
from typing import List, Dict


class TestDataRequest(BaseModel):
    """Modèle pour envoyer des données de test"""
    data_type: str = Field(..., description="Type: 'hex', 'text', 'image'")
    content: str = Field(..., description="Contenu à envoyer (hex string, texte, ou nom d'image)")


class DiagnosticResponse(BaseModel):
    """Réponse de diagnostic"""
    success: bool
    message: str
    data_sent: str = None
    data_hex: str = None


@router.get('/diagnostic/info')
async def get_diagnostic_info():
    """Récupère les informations de diagnostic"""
    return {
        'device_address': ble_manager.address,
        'uuid_write': ble_manager.uuid_write,
        'is_connected': ble_manager.is_connected,
        'available_images': list(IMAGES.keys()),
        'images_count': len(IMAGES)
    }


@router.post('/diagnostic/send-raw')
async def send_raw_data(request: TestDataRequest):
    """
    Envoie des données brutes au robot pour diagnostic
    Utile pour tester la communication via le moniteur série Arduino
    """
    if not ble_manager.is_connected:
        raise HTTPException(status_code=503, detail={
            'success': False,
            'message': 'Non connecté au robot'
        })
    
    try:
        if request.data_type == 'hex':
            # Format: "01 48 65 6C 6C 6F 00 00 00 00 00 00 00 00 00 00"
            hex_string = request.content.replace(' ', '').replace('\n', '')
            
            # Vérifier que ce sont des caractères hexadécimaux valides
            if not all(c in '0123456789ABCDEFabcdef' for c in hex_string):
                raise ValueError("Contenu hex invalide")
            
            if len(hex_string) % 2 != 0:
                raise ValueError("Nombre de caractères hex impair")
            
            # Convertir en bytes
            data = bytes.fromhex(hex_string)
            data_hex = ' '.join(f'{b:02X}' for b in data)
            
            success = await ble_manager.send_data(data)
            
            return {
                'success': success,
                'message': f'Données brutes envoyées: {len(data)} bytes',
                'data_sent': data_hex,
                'data_hex': data_hex
            }
        
        elif request.data_type == 'text':
            # Envoyer comme message texte (protocole 0x01)
            success = await ble_manager.send_message(request.content)
            
            # Reconstruire les données qui ont été envoyées
            msg_bytes = request.content.encode('utf-8')[:15]
            data_sent = bytes([0x01]) + msg_bytes.ljust(15, b'\x00')
            data_hex = ' '.join(f'{b:02X}' for b in data_sent)
            
            return {
                'success': success,
                'message': f'Message texte envoyé: "{request.content}"',
                'data_sent': repr(data_sent),
                'data_hex': data_hex
            }
        
        elif request.data_type == 'image':
            # Envoyer une image (protocole 0x02)
            if request.content not in IMAGES:
                raise HTTPException(status_code=400, detail={
                    'success': False,
                    'message': f'Image inconnue: {request.content}',
                    'available_images': list(IMAGES.keys())
                })
            
            success = await ble_manager.send_image(request.content)
            
            # Reconstruire les données
            image = IMAGES[request.content]
            data_sent = bytes([0x02]) + image
            data_hex = ' '.join(f'{b:02X}' for b in data_sent)
            
            return {
                'success': success,
                'message': f'Image envoyée: "{request.content}"',
                'data_sent': repr(data_sent),
                'data_hex': data_hex
            }
        
        else:
            raise ValueError(f"Type de données invalide: {request.data_type}")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail={
            'success': False,
            'message': f'Erreur: {str(e)}'
        })


@router.get('/diagnostic/images')
async def get_images_hex():
    """
    Récupère toutes les images prédéfinies en format hexadécimal
    Utile pour copier-coller dans le moniteur série
    """
    result = {}
    for name, image_data in IMAGES.items():
        # Format: protocole (0x02) + image data
        full_data = bytes([0x02]) + image_data
        hex_str = ' '.join(f'{b:02X}' for b in full_data)
        result[name] = {
            'hex': hex_str,
            'byte_count': len(full_data)
        }
    
    return result


@router.get('/diagnostic/test-message')
async def get_test_message_hex(message: str = "Hello"):
    """
    Génère le format hexadécimal pour un message texte
    Utile pour copier-coller dans le moniteur série
    """
    if not ble_manager.is_connected:
        raise HTTPException(status_code=503, detail={
            'success': False,
            'message': 'Non connecté au robot'
        })
    
    try:
        # Limiter à 15 caractères
        msg_bytes = message.encode('utf-8')[:15]
        data = bytes([0x01]) + msg_bytes.ljust(15, b'\x00')
        hex_str = ' '.join(f'{b:02X}' for b in data)
        
        return {
            'message': message,
            'byte_count': len(data),
            'hex_format': hex_str,
            'ascii_representation': repr(data)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail={
            'success': False,
            'error': str(e)
        })


@router.get('/diagnostic/test-values')
async def get_test_values():
    """
    Fournit des valeurs de test pour chaque type de donnée
    """
    return {
        'sample_text_hex': {
            'description': 'Message "TEST" en format BLE',
            'hex': '01 54 45 53 54 00 00 00 00 00 00 00 00 00 00 00',
            'explanation': '01 = header texte, puis "TEST" en ASCII suivi de 0x00 padding'
        },
        'sample_image_hex': {
            'description': 'Image "heart" en format BLE',
            'hex': '02 00 00 00 0C 1E 3F 7F FE FE 7F 3F 1E 0C 00 00 00',
            'explanation': '02 = header image, puis 16 bytes de pattern LED'
        },
        'all_images': {name: 'Disponible' for name in IMAGES.keys()}
    }
