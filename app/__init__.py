"""
Application FastAPI pour le contrôle IoT via Bluetooth
FastAPI supporte nativement async/await - parfait pour Bluetooth
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path


def create_app():
    """
    Factory pour créer l'application FastAPI
    
    Returns:
        app: Instance FastAPI configurée
    """
    app = FastAPI(
        title="🤖 IoT Robot API",
        description="API de contrôle Bluetooth pour robot Arduino",
        version="2.0.0",
        docs_url="/docs",  # Swagger UI automatique
        redoc_url="/redoc"  # ReDoc automatique
    )
    
    # Configuration CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # En prod: spécifier les origines
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Servir les fichiers statiques
    static_path = Path(__file__).parent / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    
    # Initialiser la base de données
    from app.models.database import init_db
    init_db()
    
    # Enregistrement des routers (équivalent des blueprints Flask)
    from app.api import router as api_router
    app.include_router(api_router, prefix="/api", tags=["API"])
    
    # Routes HTML (dashboard, etc.)
    from app import routes
    routes.init_app(app)
    
    # Enregistrement des WebSockets
    from app.api.websocket_manager import manager
    from fastapi import WebSocket, WebSocketDisconnect
    import logging
    
    logger = logging.getLogger(__name__)
    
    @app.websocket("/ws/ble-notifications")
    async def websocket_endpoint(websocket: WebSocket):
        await manager.connect(websocket)
        try:
            while True:
                # Garder la connexion ouverte en attendant des messages
                data = await websocket.receive_text()
        except WebSocketDisconnect:
            manager.disconnect(websocket)
            logger.info("Client WebSocket déconnecté.")
        except Exception as e:
            logger.error(f"Erreur WebSocket inattendue: {e}")
            manager.disconnect(websocket)
    
    return app


__version__ = '2.0.0'
__author__ = 'paulmrtnz'
