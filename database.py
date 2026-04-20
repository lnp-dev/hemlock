from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

# PostgreSQL database URL
SQLALCHEMY_DATABASE_URL = "postgresql://scamadmin:scampassword@localhost:5434/detection_logs"

Base = declarative_base()

class DetectionLog(Base):
    __tablename__ = "detection_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String)
    trigger_layer = Column(String) # e.g., "Layer 1 - User Agent"
    payload_served = Column(String) # "Clean" or "Poisoned"

# Create engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
