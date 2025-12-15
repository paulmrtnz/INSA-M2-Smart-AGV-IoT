"""
Configuration de la base de données SQLite
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Chemin vers la base de données
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'robot_data.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Création du moteur SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # Nécessaire pour SQLite
    echo=False  # Mettre à True pour voir les requêtes SQL
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

def init_db():
    """Initialise la base de données en créant toutes les tables"""
    from app.models.telemetry import Telemetry, Event, TelemetryStatistics, ConnectionLog
    Base.metadata.create_all(bind=engine)
    print(f"✓ Base de données initialisée : {DB_PATH}")

def get_db():
    """Générateur de session de base de données pour FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
