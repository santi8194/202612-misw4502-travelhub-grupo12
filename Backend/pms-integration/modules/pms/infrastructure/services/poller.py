"""
Motor de polling para sincronización periódica con el Mock PMS.
"""

import httpx
import os
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from modules.pms.infrastructure.database import SessionLocal
from modules.pms.infrastructure.models import SyncCursorModel
from modules.pms.infrastructure.services.event_bus import EventBus
from modules.pms.application.commands.sync_inventory import SyncInventory
from modules.pms.application.adapters import get_adapter


MOCK_PMS_URL = os.getenv("MOCK_PMS_URL", "http://mock-pms:8080")
POLLING_INTERVAL_SECONDS = int(os.getenv("POLLING_INTERVAL_SECONDS", "120"))
ENABLE_POLLING = os.getenv("ENABLE_POLLING", "true").lower() == "true"


class InventoryPoller:
    """
    Servicio de polling que consulta periódicamente el Mock PMS.
    
    Cada 2 minutos (configurable), consulta el endpoint /api/inventory/changes
    del Mock PMS para obtener cambios desde el último cursor.
    """

    def __init__(self):
        """Inicializa el poller con el scheduler y dependencias."""
        self.scheduler = BackgroundScheduler()
        self.event_bus = EventBus()
        self.adapter = get_adapter("mock")
        self.provider_name = "mock"

    def _get_cursor(self, db: Session) -> datetime:
        """
        Obtiene el cursor de sincronización desde la BD.
        
        Args:
            db: Sesión de base de datos
            
        Returns:
            Timestamp del último sync, o epoch si es la primera vez
        """
        cursor = db.query(SyncCursorModel).filter_by(
            provider_name=self.provider_name
        ).first()
        
        if cursor:
            return cursor.last_sync_timestamp
        else:
            return datetime(2020, 1, 1, tzinfo=timezone.utc)

    def _update_cursor(self, db: Session, timestamp: datetime) -> None:
        """
        Actualiza el cursor de sincronización en la BD.
        
        Args:
            db: Sesión de base de datos
            timestamp: Nuevo timestamp del cursor
        """
        cursor = db.query(SyncCursorModel).filter_by(
            provider_name=self.provider_name
        ).first()
        
        if cursor:
            cursor.last_sync_timestamp = timestamp
        else:
            cursor = SyncCursorModel(
                provider_name=self.provider_name,
                last_sync_timestamp=timestamp
            )
            db.add(cursor)
        
        db.commit()

    def _poll_changes(self) -> None:
        """
        Ejecuta un ciclo de polling: consulta el PMS y procesa cambios.
        """
        db = SessionLocal()
        
        try:
            cursor = self._get_cursor(db)
            cursor_iso = cursor.isoformat()
            
            print(f"[POLLER] Consultando Mock PMS desde {cursor_iso}")
            
            url = f"{MOCK_PMS_URL}/api/inventory/changes"
            params = {"since": cursor_iso}
            
            response = httpx.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            
            data = response.json()
            changes = data.get("changes", [])
            
            if not changes:
                print(f"[POLLER] No hay cambios desde {cursor_iso}")
                return
            
            print(f"[POLLER] Procesando {len(changes)} cambios")
            
            dtos = self.adapter.normalize_poll_response(data)
            
            sync_command = SyncInventory(self.event_bus)
            
            latest_timestamp = cursor
            for dto in dtos:
                sync_command.execute(dto)
                
                if dto.event_timestamp > latest_timestamp:
                    latest_timestamp = dto.event_timestamp
            
            self._update_cursor(db, latest_timestamp)
            
            print(f"[POLLER] Cursor actualizado a {latest_timestamp.isoformat()}")
            
        except httpx.HTTPError as e:
            print(f"[POLLER] Error HTTP consultando Mock PMS: {e}")
        except Exception as e:
            print(f"[POLLER] Error en polling: {e}")
        finally:
            db.close()

    def start(self) -> None:
        """Inicia el scheduler de polling."""
        if not ENABLE_POLLING:
            print("[POLLER] Polling deshabilitado (ENABLE_POLLING=false)")
            return
        
        print(f"[POLLER] Iniciando polling cada {POLLING_INTERVAL_SECONDS}s")
        
        self.scheduler.add_job(
            self._poll_changes,
            'interval',
            seconds=POLLING_INTERVAL_SECONDS,
            id='inventory_poll',
            replace_existing=True
        )
        
        self.scheduler.start()
        
        self._poll_changes()

    def stop(self) -> None:
        """Detiene el scheduler de polling."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            print("[POLLER] Polling detenido")


_poller_instance = None


def get_poller() -> InventoryPoller:
    """Obtiene la instancia singleton del poller."""
    global _poller_instance
    if _poller_instance is None:
        _poller_instance = InventoryPoller()
    return _poller_instance
