"""
DTOs para sincronización de inventario PMS.
"""

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass(frozen=True)
class InventoryChangeDTO:
    """
    DTO canónico para cambios de inventario.
    
    Formato único independiente del PMS origen.
    Usado internamente por pms-integration para normalizar
    datos de diferentes proveedores PMS.
    """
    id_propiedad: UUID
    id_categoria: UUID
    fecha: date
    cupos_totales: int
    cupos_disponibles: int
    event_timestamp: datetime
