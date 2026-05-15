"""
Adaptador concreto para el Mock PMS de desarrollo.
"""

from datetime import datetime

from modules.pms.application.adapters.base_adapter import PMSAdapter
from modules.pms.application.dtos import InventoryChangeDTO


class MockPMSAdapter(PMSAdapter):
    """
    Adaptador para el Mock PMS usado en desarrollo.
    
    Genera el codigo_mapeo_pms como string compuesto hotel_code:room_type_code.
    Catalog es responsable de resolver el UUID de la categoría usando ese código.
    No requiere archivos de mapeo externos.
    """

    def normalize_webhook(self, raw_payload: dict) -> InventoryChangeDTO:
        """
        Normaliza un webhook del Mock PMS.
        
        Formato esperado del Mock PMS:
        {
            "hotel_code": "COL-HOTE-001",
            "room_type_code": "RM001",
            "date": "2026-05-10",
            "total_units": 15,
            "available_units": 12,
            "last_modified": "2026-05-09T10:30:00Z"
        }
        """
        try:
            hotel_code = raw_payload["hotel_code"]
            room_type_code = raw_payload["room_type_code"]
            fecha_str = raw_payload["date"]
            cupos_totales = raw_payload["total_units"]
            cupos = raw_payload["available_units"]
            timestamp_str = raw_payload["last_modified"]

            codigo_mapeo_pms = f"{hotel_code}:{room_type_code}"

            fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00')).date()
            event_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))

            return InventoryChangeDTO(
                codigo_mapeo_pms=codigo_mapeo_pms,
                fecha=fecha,
                cupos_totales=cupos_totales,
                cupos_disponibles=cupos,
                event_timestamp=event_timestamp
            )

        except KeyError as e:
            raise ValueError(f"Campo requerido faltante en webhook: {e}")
        except ValueError as e:
            raise ValueError(f"Error al parsear webhook: {e}")

    def normalize_poll_response(self, raw_response: dict) -> list[InventoryChangeDTO]:
        """
        Normaliza la respuesta del endpoint de polling del Mock PMS.
        
        Formato esperado:
        {
            "provider": "mock-pms",
            "changes": [
                {
                    "hotel_code": "COL-HOTE-001",
                    "room_type_code": "RM001",
                    "date": "2026-05-10",
                    "total_units": 15,
                    "available_units": 12,
                    "last_modified": "2026-05-09T10:30:00Z"
                },
                ...
            ]
        }
        """
        try:
            return [self.normalize_webhook(change) for change in raw_response.get("changes", [])]
        except (KeyError, ValueError) as e:
            raise ValueError(f"Error al parsear respuesta de polling: {e}")
