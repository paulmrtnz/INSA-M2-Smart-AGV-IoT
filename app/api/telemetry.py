"""
Routes API pour les données de télémétrie et événements
"""
from fastapi import Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_
from typing import List, Optional
from datetime import datetime, timedelta

from app.api import router
from app.models.database import get_db
from app.models.telemetry import Telemetry, Event, TelemetryStatistics, ConnectionLog


@router.get('/telemetry/latest')
def get_latest_telemetry(
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Récupère le(s) dernier(s) paquet(s) de télémétrie
    
    Args:
        limit: Nombre maximum d'entrées à retourner (défaut: 50)
    """
    telemetries = db.query(Telemetry).order_by(desc(Telemetry.timestamp)).limit(limit).all()
    
    if not telemetries:
        return {
            'success': False,
            'message': 'Aucune télémétrie disponible',
            'data': []
        }
    
    return {
        'success': True,
        'count': len(telemetries),
        'data': [t.to_dict() for t in telemetries]
    }


@router.get('/telemetry/history')
def get_telemetry_history(
    limit: int = Query(100, ge=1, le=1000),
    hours: Optional[int] = Query(None, ge=1),
    mode: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Récupère l'historique de télémétrie avec filtres avancés
    
    Args:
        limit: Nombre maximum d'entrées (défaut: 100)
        hours: Filtrer les X dernières heures (optionnel)
        mode: Filtrer par mode ("auto" ou "manual")
    """
    query = db.query(Telemetry).order_by(desc(Telemetry.timestamp))
    
    if hours:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(Telemetry.timestamp >= cutoff)
    
    if mode:
        query = query.filter(Telemetry.mode == mode.lower())
    
    telemetries = query.limit(limit).all()
    
    return {
        'success': True,
        'count': len(telemetries),
        'data': [t.to_dict() for t in telemetries]
    }


@router.get('/telemetry/stats')
def get_telemetry_stats(
    hours: Optional[int] = Query(24),
    db: Session = Depends(get_db)
):
    """
    Récupère des statistiques détaillées sur les données de télémétrie
    
    Args:
        hours: Statistiques sur les X dernières heures (défaut: 24)
    """
    cutoff = datetime.utcnow() - timedelta(hours=hours if hours else 24)
    recent = db.query(Telemetry).filter(Telemetry.timestamp >= cutoff)
    
    all_telemetry = db.query(Telemetry)
    
    # Calculer les statistiques
    stats = {
        'period_hours': hours or 24,
        'total_records': all_telemetry.count(),
        'last_period_records': recent.count(),
        
        # Vitesse
        'avg_speed_pwm': recent.with_entities(func.avg(Telemetry.speed_pwm)).scalar() or 0,
        'max_speed_pwm': recent.with_entities(func.max(Telemetry.speed_pwm)).scalar() or 0,
        'min_speed_pwm': recent.with_entities(func.min(Telemetry.speed_pwm)).scalar() or 0,
        
        # Distance
        'total_distance_cm': recent.with_entities(func.sum(Telemetry.dist_traveled_cm)).scalar() or 0,
        'avg_distance_cm': recent.with_entities(func.avg(Telemetry.distance_cm)).scalar() or 0,
        
        # Obstacle
        'obstacle_count': recent.with_entities(func.sum(Telemetry.obstacle_events)).scalar() or 0,
        
        # Batterie
        'avg_battery': recent.with_entities(func.avg(Telemetry.battery_level)).scalar() or 0,
        'min_battery': recent.with_entities(func.min(Telemetry.battery_level)).scalar() or 0,
        
        # Uptime
        'max_uptime': recent.with_entities(func.max(Telemetry.uptime_s)).scalar() or 0,
        
        # Mode
        'mode_auto_count': recent.filter(Telemetry.mode == 'auto').count(),
        'mode_manual_count': recent.filter(Telemetry.mode == 'manual').count(),
    }
    
    # Dernier état connu
    latest = db.query(Telemetry).order_by(desc(Telemetry.timestamp)).first()
    if latest:
        stats['current_mode'] = latest.mode
        stats['current_speed_pwm'] = latest.speed_pwm
        stats['current_distance_cm'] = latest.distance_cm
        stats['last_update'] = latest.timestamp.isoformat()
    
    # Distance totale en km
    stats['total_distance_km'] = round(stats['total_distance_cm'] / 100000, 2)
    
    return {
        'success': True,
        'stats': stats
    }


@router.get('/telemetry/total-stats')
def get_total_telemetry_stats(
    db: Session = Depends(get_db)
):
    """
    Récupère les statistiques TOTALES sur TOUTE la durée de la base de données
    (Distance totale, Temps de fonctionnement total, Obstacles)
    """
    all_telemetry = db.query(Telemetry).all()
    
    if not all_telemetry:
        return {
            'success': True,
            'total_distance_m': 0,
            'total_uptime_hours': 0,
            'total_obstacles': 0,
            'total_records': 0,
            'first_record': None,
            'last_record': None
        }
    
    # Distance totale en mètres (somme de dist_traveled_cm divisée par 100)
    total_distance_cm = db.query(func.sum(Telemetry.dist_traveled_cm)).scalar() or 0
    total_distance_m = round(total_distance_cm / 100, 2)
    
    # Temps de fonctionnement total (maximum uptime_s enregistré)
    max_uptime_s = db.query(func.max(Telemetry.uptime_s)).scalar() or 0
    total_uptime_hours = round(max_uptime_s / 3600, 2)
    
    # Nombre total d'obstacles
    total_obstacles = db.query(func.sum(Telemetry.obstacle_events)).scalar() or 0
    
    # Timestamps
    first_record = db.query(Telemetry).order_by(Telemetry.timestamp).first()
    last_record = db.query(Telemetry).order_by(desc(Telemetry.timestamp)).first()
    
    return {
        'success': True,
        'total_distance_m': total_distance_m,
        'total_uptime_hours': total_uptime_hours,
        'total_obstacles': int(total_obstacles) if total_obstacles else 0,
        'total_records': len(all_telemetry),
        'first_record': first_record.timestamp.isoformat() if first_record else None,
        'last_record': last_record.timestamp.isoformat() if last_record else None
    }


@router.get('/telemetry/trend')
def get_telemetry_trend(
    field: str = Query('speed_pwm'),
    minutes: int = Query(60, ge=1, le=1440),
    db: Session = Depends(get_db)
):
    """
    Récupère la tendance d'un champ de télémétrie
    
    Args:
        field: Champ à analyser (speed_pwm, distance_cm, etc.)
        minutes: Historique en minutes
    """
    cutoff = datetime.utcnow() - timedelta(minutes=minutes)
    
    query = db.query(
        Telemetry.timestamp,
        getattr(Telemetry, field)
    ).filter(
        Telemetry.timestamp >= cutoff
    ).order_by(Telemetry.timestamp)
    
    data = query.all()
    
    return {
        'success': True,
        'field': field,
        'minutes': minutes,
        'data_points': len(data),
        'trend': [
            {
                'timestamp': t[0].isoformat(),
                'value': t[1]
            } for t in data
        ]
    }


@router.get('/events/latest')
def get_latest_events(
    limit: int = Query(20, ge=1, le=100),
    event_type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    hours: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Récupère les derniers événements avec filtres avancés
    
    Args:
        limit: Nombre d'événements (défaut: 20)
        event_type: Filtrer par type
        category: Filtrer par catégorie (info, warning, critical)
        hours: Dernières X heures
    """
    query = db.query(Event).order_by(desc(Event.timestamp))
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    if category:
        query = query.filter(Event.category == category)
    
    if hours:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(Event.timestamp >= cutoff)
    
    events = query.limit(limit).all()
    
    return {
        'success': True,
        'count': len(events),
        'data': [e.to_dict() for e in events]
    }


@router.get('/events/types')
def get_event_types(db: Session = Depends(get_db)):
    """Liste tous les types d'événements enregistrés"""
    types = db.query(Event.event_type).distinct().all()
    
    return {
        'success': True,
        'types': [t[0] for t in types if t[0]]
    }


@router.get('/events/summary')
def get_events_summary(
    hours: int = Query(24),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Résumé des événements par catégorie et liste des derniers événements
    
    Args:
        hours: Historique en heures
        limit: Nombre maximum d'événements à retourner
    """
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    events_query = db.query(Event).filter(Event.timestamp >= cutoff)
    
    summary = {
        'info': events_query.filter(Event.category == 'info').count(),
        'warning': events_query.filter(Event.category == 'warning').count(),
        'critical': events_query.filter(Event.category == 'critical').count(),
        'total': events_query.count(),
        'period_hours': hours,
        'unacknowledged': events_query.filter(Event.acknowledged == False).count()
    }
    
    # Récupérer les derniers événements
    latest_events = db.query(Event).order_by(desc(Event.timestamp)).limit(limit).all()
    
    return {
        'success': True,
        'summary': summary,
        'events': [e.to_dict() for e in latest_events]
    }


@router.get('/events/critical')
def get_critical_events(
    hours: int = Query(24),
    db: Session = Depends(get_db)
):
    """Récupère tous les événements critiques des X dernières heures"""
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    events = db.query(Event).filter(
        and_(
            Event.timestamp >= cutoff,
            Event.severity_level >= 3
        )
    ).order_by(desc(Event.timestamp)).all()
    
    return {
        'success': True,
        'count': len(events),
        'critical_events': [e.to_dict() for e in events]
    }


@router.get('/connection/log')
@router.get('/connection/history')  # Alias pour la compatibilité
def get_connection_log(
    limit: int = Query(50, ge=1, le=500),
    hours: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Récupère l'historique de connexion"""
    query = db.query(ConnectionLog).order_by(desc(ConnectionLog.timestamp))
    
    if hours:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        query = query.filter(ConnectionLog.timestamp >= cutoff)
    
    logs = query.limit(limit).all()
    
    return {
        'success': True,
        'count': len(logs),
        'connections': [log.to_dict() for log in logs],
        'data': [log.to_dict() for log in logs]
    }


@router.post('/connection/log')
def log_connection(
    device_address: str,
    event: str,  # "connect", "disconnect", "reconnect", "error"
    device_name: Optional[str] = None,
    reason: Optional[str] = None,
    duration_seconds: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Enregistre un événement de connexion"""
    try:
        log_entry = ConnectionLog(
            device_address=device_address,
            device_name=device_name,
            event=event,
            reason=reason,
            duration_seconds=duration_seconds,
            timestamp=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
        
        return {
            'success': True,
            'id': log_entry.id,
            'message': f'Connexion enregistrée: {event}'
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail={
            'success': False,
            'error': str(e)
        })


@router.delete('/telemetry/clear')
def clear_telemetry(
    confirm: bool = Query(False),
    older_than_hours: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Efface les données de télémétrie
    
    Args:
        confirm: Confirmation requise (=true)
        older_than_hours: Ne supprimer que les données plus anciennes (optionnel)
    """
    if not confirm:
        raise HTTPException(status_code=400, detail={
            'success': False,
            'message': 'Paramètre confirm=true requis'
        })
    
    query = db.query(Telemetry)
    
    if older_than_hours:
        cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)
        query = query.filter(Telemetry.timestamp < cutoff)
    
    count = query.delete()
    db.commit()
    
    return {
        'success': True,
        'message': f'{count} entrées de télémétrie supprimées',
        'deleted_count': count
    }


@router.delete('/events/clear')
def clear_events(
    confirm: bool = Query(False),
    older_than_hours: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Efface les événements
    
    Args:
        confirm: Confirmation requise (=true)
        older_than_hours: Ne supprimer que les anciens (optionnel)
    """
    if not confirm:
        raise HTTPException(status_code=400, detail={
            'success': False,
            'message': 'Paramètre confirm=true requis'
        })
    
    query = db.query(Event)
    
    if older_than_hours:
        cutoff = datetime.utcnow() - timedelta(hours=older_than_hours)
        query = query.filter(Event.timestamp < cutoff)
    
    count = query.delete()
    db.commit()
    
    return {
        'success': True,
        'message': f'{count} événements supprimés',
        'deleted_count': count
    }


@router.patch('/events/{event_id}/acknowledge')
def acknowledge_event(
    event_id: int,
    db: Session = Depends(get_db)
):
    """Marquer un événement comme reconnu"""
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=404, detail='Événement non trouvé')
    
    event.acknowledged = True
    db.commit()
    
    return {
        'success': True,
        'message': 'Événement reconnu',
        'event': event.to_dict()
    }


@router.get('/database/info')
def get_database_info(db: Session = Depends(get_db)):
    """Récupère des informations sur la base de données"""
    telemetry_count = db.query(Telemetry).count()
    events_count = db.query(Event).count()
    connection_logs_count = db.query(ConnectionLog).count()
    
    oldest_telemetry = db.query(Telemetry).order_by(Telemetry.timestamp).first()
    latest_telemetry = db.query(Telemetry).order_by(desc(Telemetry.timestamp)).first()
    
    return {
        'success': True,
        'database': {
            'telemetry_records': telemetry_count,
            'events_records': events_count,
            'connection_logs': connection_logs_count,
            'total_records': telemetry_count + events_count + connection_logs_count,
            'oldest_telemetry': oldest_telemetry.timestamp.isoformat() if oldest_telemetry else None,
            'latest_telemetry': latest_telemetry.timestamp.isoformat() if latest_telemetry else None,
            'telemetry_span_days': (latest_telemetry.timestamp - oldest_telemetry.timestamp).days if oldest_telemetry and latest_telemetry else 0
        }
    }

