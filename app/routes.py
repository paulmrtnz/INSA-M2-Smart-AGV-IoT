"""
Routes principales de l'application
Gere les pages HTML (dashboard, login, etc.)
Utilise Jinja2Templates pour FastAPI
"""
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Configuration Jinja2 pour FastAPI
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def init_app(app):
    """
    Initialise les routes principales dans l'application FastAPI
    
    Args:
        app: Instance FastAPI
    """
    
    @app.get('/', response_class=HTMLResponse)
    async def index(request: Request):
        """Page d'accueil du site"""
        return templates.TemplateResponse("index.html", {"request": request})
    
    @app.get('/dashboard', response_class=HTMLResponse)
    async def dashboard(request: Request):
        """Dashboard de controle du robot"""
        return templates.TemplateResponse("dashboard.html", {"request": request})

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: HTTPException):
        """Gestionnaire erreur 404"""
        return JSONResponse(
            status_code=404,
            content={'error': 'Page non trouvee', 'status': 404}
        )
    
    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc: HTTPException):
        """Gestionnaire erreur 500"""
        return JSONResponse(
            status_code=500,
            content={'error': 'Erreur serveur', 'status': 500}
        )
