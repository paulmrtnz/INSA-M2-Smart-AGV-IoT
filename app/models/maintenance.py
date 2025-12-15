"""
Utilitaires de maintenance et d'optimisation de la base de données
"""
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.database import SessionLocal
from app.models.telemetry import Telemetry, Event, ConnectionLog

logger = logging.getLogger(__name__)


def cleanup_old_data(days: int = 30) -> dict:
    """
    Nettoie les données de plus de X jours
    
    Args:
        days: Nombre de jours à conserver
    
    Returns:
        Dict avec statistiques de nettoyage
    """
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        telemetry_deleted = db.query(Telemetry).filter(
            Telemetry.timestamp < cutoff
        ).delete()
        
        events_deleted = db.query(Event).filter(
            Event.timestamp < cutoff
        ).delete()
        
        logs_deleted = db.query(ConnectionLog).filter(
            ConnectionLog.timestamp < cutoff
        ).delete()
        
        db.commit()
        
        result = {
            'success': True,
            'timestamp': datetime.utcnow().isoformat(),
            'deleted': {
                'telemetry': telemetry_deleted,
                'events': events_deleted,
                'connection_logs': logs_deleted,
                'total': telemetry_deleted + events_deleted + logs_deleted
            },
            'cutoff_date': cutoff.isoformat(),
            'days_retained': days
        }
        
        logger.info(f"✓ Nettoyage BDD: {result['deleted']['total']} entrées supprimées (> {days} jours)")
        return result
    
    except Exception as e:
        logger.error(f"✗ Erreur nettoyage BDD: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


def get_database_size() -> dict:
    """Récupère la taille et les statistiques de la base de données"""
    db = SessionLocal()
    try:
        telemetry_count = db.query(Telemetry).count()
        events_count = db.query(Event).count()
        logs_count = db.query(ConnectionLog).count()
        
        # Taille estimée en MB (approximation)
        telemetry_size_mb = (telemetry_count * 0.5) / 1024  # ~500 bytes par paquet
        events_size_mb = (events_count * 0.3) / 1024  # ~300 bytes par événement
        total_size_mb = telemetry_size_mb + events_size_mb
        
        oldest_data = db.query(Telemetry).order_by(Telemetry.timestamp).first()
        latest_data = db.query(Telemetry).order_by(Telemetry.timestamp.desc()).first()
        
        span_days = 0
        if oldest_data and latest_data:
            span_days = (latest_data.timestamp - oldest_data.timestamp).days
        
        return {
            'success': True,
            'records': {
                'telemetry': telemetry_count,
                'events': events_count,
                'connection_logs': logs_count,
                'total': telemetry_count + events_count + logs_count
            },
            'size_mb': {
                'telemetry': round(telemetry_size_mb, 2),
                'events': round(events_size_mb, 2),
                'total_estimated': round(total_size_mb, 2)
            },
            'time_span': {
                'oldest': oldest_data.timestamp.isoformat() if oldest_data else None,
                'latest': latest_data.timestamp.isoformat() if latest_data else None,
                'days': span_days
            }
        }
    
    except Exception as e:
        logger.error(f"✗ Erreur calcul taille BDD: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


def archive_old_data(days: int = 90) -> dict:
    """
    Archive les données de plus de X jours (marque comme archivées)
    
    Args:
        days: Nombre de jours avant archivage
    
    Returns:
        Nombre de records archivés
    """
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        archived = db.query(Telemetry).filter(
            Telemetry.timestamp < cutoff,
            Telemetry.archived == False
        ).update({'archived': True})
        
        db.commit()
        
        logger.info(f"✓ Archivage: {archived} paquets marqués comme archivés")
        return {
            'success': True,
            'archived_count': archived,
            'cutoff_date': cutoff.isoformat()
        }
    
    except Exception as e:
        logger.error(f"✗ Erreur archivage: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


def rebuild_database() -> dict:
    """
    Reconstruit la base de données (vacuum et réindex)
    Utile après suppressions massives
    """
    try:
        from app.models.database import engine
        
        # SQLite VACUUM
        with engine.connect() as conn:
            conn.execute("VACUUM")
            conn.commit()
        
        logger.info("✓ Optimisation BDD terminée (VACUUM)")
        return {
            'success': True,
            'message': 'Base de données optimisée'
        }
    
    except Exception as e:
        logger.error(f"✗ Erreur optimisation: {e}")
        return {'success': False, 'error': str(e)}


def get_data_quality() -> dict:
    """
    Analyse la qualité des données
    """
    db = SessionLocal()
    try:
        total_telemetry = db.query(Telemetry).count()
        complete_telemetry = db.query(Telemetry).filter(
            Telemetry.uptime_s != None,
            Telemetry.mode != None,
            Telemetry.speed_pwm != None
        ).count()
        
        total_events = db.query(Event).count()
        critical_events = db.query(Event).filter(
            Event.severity_level >= 3
        ).count()
        
        unacknowledged = db.query(Event).filter(
            Event.acknowledged == False
        ).count()
        
        quality = {
            'telemetry_completeness': round((complete_telemetry / total_telemetry * 100) if total_telemetry > 0 else 0, 2),
            'critical_events': critical_events,
            'unacknowledged_events': unacknowledged,
            'total_records': total_telemetry + total_events
        }
        
        return {
            'success': True,
            'quality': quality,
            'health': 'good' if quality['telemetry_completeness'] > 95 else 'warning' if quality['telemetry_completeness'] > 80 else 'critical'
        }
    
    except Exception as e:
        logger.error(f"✗ Erreur analyse qualité: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


def export_data(format: str = 'json', limit: int = 1000) -> dict:
    """
    Exporte les données dans différents formats
    
    Args:
        format: Format de sortie (json, csv)
        limit: Nombre de records à exporter
    
    Returns:
        Données exportées
    """
    db = SessionLocal()
    try:
        if format == 'json':
            telemetry = db.query(Telemetry).order_by(Telemetry.timestamp.desc()).limit(limit).all()
            events = db.query(Event).order_by(Event.timestamp.desc()).limit(limit).all()
            
            return {
                'success': True,
                'format': 'json',
                'telemetry': [t.to_dict() for t in telemetry],
                'events': [e.to_dict() for e in events]
            }
        
        elif format == 'csv':
            import csv
            import io
            
            # Export télémétrie
            telemetry = db.query(Telemetry).order_by(Telemetry.timestamp.desc()).limit(limit).all()
            
            output = io.StringIO()
            if telemetry:
                writer = csv.DictWriter(output, fieldnames=telemetry[0].to_dict().keys())
                writer.writeheader()
                for t in telemetry:
                    writer.writerow(t.to_dict())
            
            return {
                'success': True,
                'format': 'csv',
                'data': output.getvalue(),
                'records': len(telemetry)
            }
        
        else:
            return {'success': False, 'error': 'Format non supporté'}
    
    except Exception as e:
        logger.error(f"✗ Erreur export: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        db.close()


if __name__ == '__main__':
    # Test des fonctions de maintenance
    logging.basicConfig(level=logging.INFO)
    
    print("📊 Analyse Base de Données")
    print("=" * 60)
    
    print("\n1️⃣ Taille de la BDD:")
    size = get_database_size()
    if size['success']:
        print(f"   Télémétrie: {size['records']['telemetry']} records")
        print(f"   Événements: {size['records']['events']} records")
        print(f"   Logs: {size['records']['connection_logs']} records")
        print(f"   Taille estimée: {size['size_mb']['total_estimated']} MB")
    
    print("\n2️⃣ Qualité des données:")
    quality = get_data_quality()
    if quality['success']:
        print(f"   Complétude: {quality['quality']['telemetry_completeness']}%")
        print(f"   Santé: {quality['health']}")
    
    print("\n3️⃣ Événements critiques:")
    print(f"   {quality['quality']['critical_events']} événements critiques")
    print(f"   {quality['quality']['unacknowledged_events']} non reconnus")
    
    print("\n" + "=" * 60)
