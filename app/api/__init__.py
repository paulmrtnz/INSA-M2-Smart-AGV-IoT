"""
Module API - Endpoints RESTful pour le controle du robot
"""
from fastapi import APIRouter

router = APIRouter()

from app.api import routes, bluetooth, diagnostic, telemetry, maintenance

__all__ = ['router']
