"""
Point d'entrée principal de l'application FastAPI
Utilise uvicorn comme serveur ASGI
"""
import os
from app import create_app

# Créer l'application
app = create_app()

if __name__ == '__main__':
    import uvicorn
    
    # Configuration du serveur
    host = os.environ.get('FLASK_HOST', '0.0.0.0')  # Garde le nom pour compatibilité
    port = int(os.environ.get('FLASK_PORT', 8000))
    
    print("\n" + "="*60)
    print("🤖 Serveur IoT Robot FastAPI - Démarrage")
    print("="*60)
    print(f"📡 URL: http://{host}:{port}")
    print(f"� Swagger UI: http://{host}:{port}/docs")
    print(f"� ReDoc: http://{host}:{port}/redoc")
    print("="*60 + "\n")
    
    # Démarrer uvicorn
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,  # Hot reload en développement
        log_level="info"
    )