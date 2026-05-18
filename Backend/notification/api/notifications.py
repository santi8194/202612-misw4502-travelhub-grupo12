from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from config.db import get_db
from models.notification import Notificacion, DeviceToken

router = APIRouter(prefix="/notificaciones", tags=["notificaciones"])

class NotificacionResponse(BaseModel):
    id: str
    user_id: str
    tipo: str
    titulo: str
    cuerpo: str
    reserva_id: Optional[str] = None
    timestamp: datetime
    leida: bool

    class Config:
        orm_mode = True

class DeviceTokenRequest(BaseModel):
    user_id: str
    token: str

@router.get("", response_model=List[NotificacionResponse])
def get_notificaciones(userId: str, db: Session = Depends(get_db)):
    notifs = db.query(Notificacion).filter(Notificacion.user_id == userId).order_by(desc(Notificacion.timestamp)).all()
    return notifs

@router.patch("/{id}/leida")
def marcar_leida(id: str, db: Session = Depends(get_db)):
    notif = db.query(Notificacion).filter(Notificacion.id == id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notificacion no encontrada")
    
    notif.leida = True
    db.commit()
    return {"status": "success"}

@router.post("/device-token")
def save_device_token(request: DeviceTokenRequest, db: Session = Depends(get_db)):
    # Upsert logic
    dt = db.query(DeviceToken).filter(DeviceToken.user_id == request.user_id).first()
    if dt:
        dt.token = request.token
    else:
        dt = DeviceToken(user_id=request.user_id, token=request.token)
        db.add(dt)
    
    db.commit()
    return {"status": "success"}
