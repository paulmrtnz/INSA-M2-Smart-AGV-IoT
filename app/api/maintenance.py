"""
Routes API pour la maintenance et l'optimisation de la base de données
"""
from fastapi import Query
from app.api import router
from app.models.maintenance import (
    cleanup_old_data, get_database_size, archive_old_data,
    rebuild_database, get_data_quality, export_data
)


@router.get('/database/size')
def get_db_size():
    """Récupère la taille et les statistiques de la base de données"""
    return get_database_size()


@router.get('/database/quality')
def get_db_quality():
    """Analyse la qualité des données"""
    return get_data_quality()


@router.post('/database/cleanup')
def cleanup_db(
    days: int = Query(30, ge=1, le=365),
    confirm: bool = Query(False)
):
    """
    Nettoie les données de plus de X jours
    
    Args:
        days: Nombre de jours à conserver (défaut: 30)
        confirm: Confirmation requise
    """
    if not confirm:
        return {
            'success': False,
            'message': 'Paramètre confirm=true requis',
            'action': 'cleanup',
            'preview': f'Supprimera les données de plus de {days} jours'
        }
    
    return cleanup_old_data(days)


@router.post('/database/archive')
def archive_db(
    days: int = Query(90, ge=1, le=365),
    confirm: bool = Query(False)
):
    """
    Archive les données de plus de X jours
    
    Args:
        days: Nombre de jours avant archivage
        confirm: Confirmation requise
    """
    if not confirm:
        return {
            'success': False,
            'message': 'Paramètre confirm=true requis',
            'action': 'archive',
            'preview': f'Archivera les données de plus de {days} jours'
        }
    
    return archive_old_data(days)


@router.post('/database/optimize')
def optimize_db(confirm: bool = Query(False)):
    """
    Optimise la base de données (VACUUM)
    Utile après suppressions massives
    
    Args:
        confirm: Confirmation requise
    """
    if not confirm:
        return {
            'success': False,
            'message': 'Paramètre confirm=true requis',
            'action': 'optimize',
            'preview': 'Défragmentera la base de données'
        }
    
    return rebuild_database()


@router.get('/database/export')
def export_db(
    format: str = Query('json', regex='^(json|csv)$'),
    limit: int = Query(1000, ge=10, le=10000)
):
    """
    Exporte les données
    
    Args:
        format: Format (json ou csv)
        limit: Nombre de records
    """
    return export_data(format, limit)


@router.get('/database/health')
def get_db_health():
    """Récupère l'état de santé général de la base de données"""
    size_info = get_database_size()
    quality_info = get_data_quality()
    
    health_score = 100
    warnings = []
    
    # Vérifications
    if size_info['success']:
        if size_info['size_mb']['total_estimated'] > 500:
            health_score -= 10
            warnings.append('Base de données volumineuse (> 500 MB)')
    
    if quality_info['success']:
        if quality_info['quality']['telemetry_completeness'] < 80:
            health_score -= 20
            warnings.append('Données incomplètes (< 80%)')
        
        if quality_info['quality']['unacknowledged_events'] > 100:
            health_score -= 15
            warnings.append('Trop d\'événements non reconnus (> 100)')
    
    return {
        'success': True,
        'health_score': max(0, health_score),
        'status': 'healthy' if health_score >= 80 else 'warning' if health_score >= 50 else 'critical',
        'warnings': warnings,
        'recommendations': [
            'Nettoyer les données de plus de 30 jours' if size_info['success'] and size_info['size_mb']['total_estimated'] > 100 else None,
            'Optimiser la base de données' if quality_info['success'] and quality_info['quality']['critical_events'] > 50 else None,
            'Reconnaître les événements en attente' if quality_info['success'] and quality_info['quality']['unacknowledged_events'] > 0 else None
        ]
    }
