from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, Text
import uuid
from config.db import Base

def generate_uuid():
    return str(uuid.uuid4())

class Notificacion(Base):
    __tablename__ = "notificaciones"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, index=True)
    tipo = Column(String, nullable=False) # 'confirmed', 'discount', 'checkin_reminder', 'profile_update'
    titulo = Column(String, nullable=False)
    cuerpo = Column(Text, nullable=False)
    reserva_id = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    leida = Column(Boolean, default=False)

class DeviceToken(Base):
    __tablename__ = "device_tokens"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False, unique=True, index=True)
    token = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
