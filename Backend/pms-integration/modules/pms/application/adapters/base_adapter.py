"""
Interfaz base para adaptadores PMS.
"""

from abc import ABC, abstractmethod
from modules.pms.application.dtos import InventoryChangeDTO


class PMSAdapter(ABC):
    """
    Interfaz base para normalizar datos de proveedores PMS heterogéneos.
    
    Cada proveedor PMS (Opera, Mews, Mock, etc.) tiene su propio formato de datos.
    Los adaptadores traducen esos formatos al DTO canónico de TravelHub.
    """

    @abstractmethod
    def normalize_webhook(self, raw_payload: dict) -> InventoryChangeDTO:
        """
        Convierte un payload crudo de webhook al DTO canónico.
        
        Args:
            raw_payload: Datos crudos del webhook del PMS
            
        Returns:
            InventoryChangeDTO con UUIDs de TravelHub
            
        Raises:
            ValueError: Si el payload es inválido o faltan códigos en el mapeo
        """
        pass

    @abstractmethod
    def normalize_poll_response(self, raw_response: dict) -> list[InventoryChangeDTO]:
        """
        Convierte una respuesta de polling a una lista de DTOs canónicos.
        
        Args:
            raw_response: Respuesta cruda del endpoint de polling del PMS
            
        Returns:
            Lista de InventoryChangeDTO
            
        Raises:
            ValueError: Si la respuesta es inválida
        """
        pass
