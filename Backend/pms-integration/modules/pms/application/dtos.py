"""
DTOs para sincronización de inventario PMS.
"""

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class InventoryChangeDTO:
    """
    DTO canónico para cambios de inventario.
    
    Formato único independiente del PMS origen.
    Usado internamente por pms-integration para normalizar
    datos de diferentes proveedores PMS.
    El campo codigo_mapeo_pms viaja como string compuesto
    hotel_code:room_type_code. Catalog resuelve el UUID internamente.
    """
    codigo_mapeo_pms: str
    fecha: date
    cupos_totales: int
    cupos_disponibles: int
    event_timestamp: datetime
