"""
Modèles de données pour la télémétrie et les événements
Structure optimisée pour l'historisation complète
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text, Index, CheckConstraint
from datetime import datetime
from app.models.database import Base


class Telemetry(Base):
    """
    Table pour stocker les paquets de télémétrie reçus du robot
    Optimisée pour l'historisation avec index sur les requêtes fréquentes
    """
    __tablename__ = "telemetry"
    
    # Clés primaires et identifiants
    id = Column(Integer, primary_key=True, autoincrement=True)
    packet_id = Column(String(36), unique=True, nullable=True, index=True)  # UUID du paquet
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # Quand reçu
    
    # Données de télémétrie
    uptime_s = Column(Integer, nullable=True)  # Temps de fonctionnement en secondes
    mode = Column(String(20), nullable=True, index=True)  # "auto" ou "manual"
    distance_cm = Column(Float, nullable=True)  # Distance ultrason en cm
    obstacle_events = Column(Integer, nullable=True, default=0)  # Nombre d'obstacles
    last_ir_cmd = Column(String(20), nullable=True)  # Dernière commande IR (hex)
    speed_pwm = Column(Integer, nullable=True)
    dist_traveled_cm = Column(Float, nullable=True, default=0)  # Distance parcourue
    
    # Métadonnées
    battery_level = Column(Integer, nullable=True)
    signal_strength = Column(Integer, nullable=True)  # RSSI
    packet_raw = Column(Text, nullable=True)  # Paquet JSON brut reçu
    checksum = Column(String(64), nullable=True)  # Hash SHA256 du paquet
    
    # Flags de traitement
    processed = Column(Boolean, default=False)
    archived = Column(Boolean, default=False)
    
    # Index composés pour les requêtes fréquentes
    __table_args__ = (
        Index('idx_telemetry_timestamp_mode', 'timestamp', 'mode'),
        Index('idx_telemetry_received_at', 'received_at'),
        Index('idx_telemetry_mode_timestamp', 'mode', 'timestamp'),
        CheckConstraint('speed_pwm >= 0 AND speed_pwm <= 255'),
        CheckConstraint('battery_level >= 0 AND battery_level <= 100'),
    )
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id': self.id,
            'packet_id': self.packet_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'uptime_s': self.uptime_s,
            'mode': self.mode,
            'distance_cm': self.distance_cm,
            'obstacle_events': self.obstacle_events,
            'last_ir_cmd': self.last_ir_cmd,
            'speed_pwm': self.speed_pwm,
            'dist_traveled_cm': self.dist_traveled_cm,
            'battery_level': self.battery_level,
            'signal_strength': self.signal_strength,
            'processed': self.processed,
            'archived': self.archived
        }


class Event(Base):
    """
    Table pour stocker les événements spéciaux du robot
    Optimisée pour le tracking d'événements avec historique complet
    """
    __tablename__ = "events"
    
    # Clés primaires et identifiants
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(36), unique=True, nullable=True, index=True)  # UUID unique
    
    # Timestamps
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Type et catégorie d'événement
    event_type = Column(String(50), nullable=False, index=True)  
    # Types: "mode_change", "lights_toggle", "obstacle_detected", "emergency_stop", "battery_low", "connection"
    
    category = Column(String(20), nullable=False, default='info', index=True)
    # Catégories: "info", "warning", "critical", "error"
    
    # Détails de l'événement
    description = Column(String(255), nullable=True)
    value = Column(String(100), nullable=True)  # Valeur avant le changement
    new_value = Column(String(100), nullable=True)  # Valeur après le changement
    
    # Contexte additionnel
    source = Column(String(50), nullable=True)  # D'où vient l'événement (ex: "bluetooth", "sensor")
    raw_data = Column(Text, nullable=True)  # Données brutes
    
    # État de l'événement
    severity_level = Column(Integer, default=1)  # 1=info, 2=warning, 3=critical, 4=emergency
    acknowledged = Column(Boolean, default=False)
    processed = Column(Boolean, default=False)
    
    # Index composés
    __table_args__ = (
        Index('idx_event_timestamp_type', 'timestamp', 'event_type'),
        Index('idx_event_category_severity', 'category', 'severity_level'),
        Index('idx_event_received_at', 'received_at'),
        Index('idx_event_type_timestamp', 'event_type', 'timestamp'),
    )
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id': self.id,
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'received_at': self.received_at.isoformat() if self.received_at else None,
            'event_type': self.event_type,
            'category': self.category,
            'description': self.description,
            'value': self.value,
            'new_value': self.new_value,
            'source': self.source,
            'severity_level': self.severity_level,
            'acknowledged': self.acknowledged,
            'processed': self.processed
        }


class TelemetryStatistics(Base):
    """
    Table pour stocker les statistiques agrégées par heure/jour
    Permet une analyse rapide sans scanner tous les paquets
    """
    __tablename__ = "telemetry_statistics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    period_start = Column(DateTime, nullable=False, index=True)  # Début de la période
    period_type = Column(String(10), nullable=False)  # "hour" ou "day"
    
    # Statistiques
    packet_count = Column(Integer, default=0)
    avg_speed_pwm = Column(Float, nullable=True)
    max_speed_pwm = Column(Integer, nullable=True)
    min_speed_pwm = Column(Integer, nullable=True)
    
    avg_distance_cm = Column(Float, nullable=True)
    total_distance_cm = Column(Float, default=0)
    
    obstacle_count = Column(Integer, default=0)
    avg_battery = Column(Float, nullable=True)
    
    mode_auto_time = Column(Integer, default=0)  # Temps en mode auto (secondes)
    mode_manual_time = Column(Integer, default=0)  # Temps en mode manuel (secondes)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_stats_period_start_type', 'period_start', 'period_type'),
    )
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id': self.id,
            'period_start': self.period_start.isoformat(),
            'period_type': self.period_type,
            'packet_count': self.packet_count,
            'avg_speed_pwm': self.avg_speed_pwm,
            'max_speed_pwm': self.max_speed_pwm,
            'min_speed_pwm': self.min_speed_pwm,
            'avg_distance_cm': self.avg_distance_cm,
            'total_distance_cm': self.total_distance_cm,
            'obstacle_count': self.obstacle_count,
            'avg_battery': self.avg_battery,
            'mode_auto_time': self.mode_auto_time,
            'mode_manual_time': self.mode_manual_time,
            'last_updated': self.last_updated.isoformat()
        }


class ConnectionLog(Base):
    """
    Table pour logger toutes les connexions/déconnexions
    Utile pour l'audit et le troubleshooting
    """
    __tablename__ = "connection_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Informations de connexion
    device_address = Column(String(20), nullable=False, index=True)  # Adresse MAC
    device_name = Column(String(100), nullable=True)
    
    # Type d'événement
    event = Column(String(20), nullable=False)  # "connect", "disconnect", "reconnect", "error"
    reason = Column(String(255), nullable=True)  # Raison de déconnexion
    error_message = Column(Text, nullable=True)
    
    # État
    duration_seconds = Column(Integer, nullable=True)  # Durée de connexion
    signal_strength = Column(Integer, nullable=True)
    
    __table_args__ = (
        Index('idx_connection_timestamp', 'timestamp'),
        Index('idx_connection_device_event', 'device_address', 'event'),
    )
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'device_address': self.device_address,
            'device_name': self.device_name,
            'event': self.event,
            'reason': self.reason,
            'duration_seconds': self.duration_seconds,
            'signal_strength': self.signal_strength
        }
