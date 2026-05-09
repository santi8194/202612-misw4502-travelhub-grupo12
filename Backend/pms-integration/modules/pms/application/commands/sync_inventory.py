"""
Comando para sincronizar cambios de inventario del PMS.
"""

from modules.pms.application.dtos import InventoryChangeDTO
from modules.pms.domain.events import PMSInventoryUpdated
from modules.pms.infrastructure.services.event_bus import EventBus


class SyncInventory:
    """
    Use case para procesar cambios de inventario del PMS.
    
    Recibe un DTO normalizado y publica un evento PMSInventoryUpdated
    que será consumido por Catalog.
    """

    def __init__(self, event_bus: EventBus):
        """
        Inicializa el comando con el event bus.
        
        Args:
            event_bus: Bus de eventos para publicar PMSInventoryUpdated
        """
        self.event_bus = event_bus

    def execute(self, dto: InventoryChangeDTO) -> None:
        """
        Ejecuta la sincronización de inventario.
        
        Args:
            dto: DTO con los datos normalizados del cambio de inventario
        """
        event = PMSInventoryUpdated(
            id_propiedad=dto.id_propiedad,
            id_categoria=dto.id_categoria,
            fecha=dto.fecha,
            cupos_disponibles=dto.cupos_disponibles,
            event_timestamp=dto.event_timestamp
        )
        
        self.event_bus.publish_event(
            routing_key=event.routing_key,
            event_type=event.type,
            payload=event.to_dict()
        )
        
        print(f"[SYNC] Publicado PMSInventoryUpdated: {dto.id_categoria} @ {dto.fecha} -> {dto.cupos_disponibles} cupos")
