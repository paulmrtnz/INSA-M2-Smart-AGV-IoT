"""
Routes API pour la gestion Bluetooth
Gere la connexion et envoi de messages/images au robot
Utilise FastAPI avec support async natif
"""
from fastapi import HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from app.api import router
from app.api.websocket_manager import manager
from app.services.ble_manager import ble_manager


class MessageRequest(BaseModel):
    message: str = Field(..., max_length=15)


class ImageRequest(BaseModel):
    name: str = Field(...)


@router.get('/ble/status')
async def get_ble_status():
    """Recupere le statut de la connexion Bluetooth"""
    return {
        'connected': ble_manager.is_connected,
        'device': ble_manager.address
    }


@router.post('/ble/connect')
async def connect_bluetooth():
    """Etablit une connexion Bluetooth avec le robot"""
    try:
        result = await ble_manager.connect()
        
        if result.get('success'):
            return {
                'success': True,
                'message': 'Connecte au robot',
                'device': ble_manager.address
            }
        else:
            raise HTTPException(status_code=503, detail={
                'success': False,
                'message': result.get('message', 'Echec de la connexion au robot')
            })
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            'success': False,
            'error': str(e)
        })


@router.post('/ble/disconnect')
async def disconnect_bluetooth():
    """Ferme la connexion Bluetooth"""
    try:
        result = await ble_manager.disconnect()
        return {
            'success': result.get('success', False),
            'message': result.get('message', 'Deconnecte du robot')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            'success': False,
            'error': str(e)
        })


@router.get('/ble/scan')
async def scan_devices(timeout: float = 5.0):
    """Scanne les appareils Bluetooth a proximite"""
    try:
        devices = await ble_manager.scan_devices(timeout)
        return {
            'devices': devices,
            'count': len(devices)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            'success': False,
            'error': str(e)
        })


@router.post('/ble/message')
async def send_text_message(request: MessageRequest):
    """Envoie un message texte au robot"""
    try:
        success = await ble_manager.send_message(request.message)
        
        if success:
            return {
                'success': True,
                'message': f'Message "{request.message}" envoye'
            }
        else:
            raise HTTPException(status_code=500, detail={
                'success': False,
                'message': 'Echec de l\'envoi. Verifiez la connexion.'
            })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            'success': False,
            'error': str(e)
        })


@router.post('/ble/image')
async def send_led_image(request: ImageRequest):
    """Envoie une image predefinie a la matrice LED"""
    try:
        success = await ble_manager.send_image(request.name)
        
        if success:
            return {
                'success': True,
                'message': f'Image "{request.name}" envoyee'
            }
        else:
            raise HTTPException(status_code=400, detail={
                'success': False,
                'message': f'Image "{request.name}" inconnue ou erreur d\'envoi'
            })
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail={
            'success': False,
            'error': str(e)
        })


@router.get('/ble/services')
async def get_ble_services():
    """Récupère les services et caractéristiques BLE disponibles"""
    if not ble_manager.is_connected:
        raise HTTPException(status_code=503, detail={
            'success': False,
            'message': 'Non connecté au robot'
        })
    
    try:
        services_list = []
        for service in ble_manager.client.services:
            service_info = {
                'uuid': str(service.uuid),
                'characteristics': []
            }
            
            for char in service.characteristics:
                char_info = {
                    'uuid': str(char.uuid),
                    'properties': char.properties
                }
                service_info['characteristics'].append(char_info)
            
            services_list.append(service_info)
        
        return {
            'success': True,
            'services': services_list,
            'count': len(services_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            'success': False,
            'error': str(e)
        })