"""
Adaptador concreto para el Mock PMS de desarrollo.
"""

import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

from modules.pms.application.adapters.base_adapter import PMSAdapter
from modules.pms.application.dtos import InventoryChangeDTO


class MockPMSAdapter(PMSAdapter):
    """
    Adaptador para el Mock PMS usado en desarrollo.
    
    Traduce códigos PMS (hotel_code, room_type_code) a UUIDs de TravelHub
    usando el archivo de mapeo generado por el seed de Catalog.
    """

    def __init__(self, mapping_file: str = None):
        """
        Inicializa el adaptador con el archivo de mapeo.
        
        Args:
            mapping_file: Ruta al archivo pms_uuid_mapping_full.json
        """
        if mapping_file is None:
            base_path = Path(__file__).parent.parent.parent.parent.parent
            mapping_file = base_path / "data" / "pms_uuid_mapping_full.json"
        
        self.mapping = self._load_mapping(mapping_file)

    def _load_mapping(self, mapping_file: str) -> dict:
        """Carga el archivo de mapeo PMS → UUIDs."""
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("mappings", {})
        except FileNotFoundError:
            raise ValueError(
                f"Archivo de mapeo no encontrado: {mapping_file}. "
                "Ejecuta 'python3 scripts/generate_uuid_mapping_v2.py' en Backend/catalog"
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Error al parsear archivo de mapeo: {e}")

    def _get_uuids(self, hotel_code: str, room_type_code: str) -> tuple[UUID, UUID]:
        """
        Obtiene los UUIDs de propiedad y categoría desde el mapeo.
        
        Args:
            hotel_code: Código del hotel en el PMS (ej: "COL-HOTE-001")
            room_type_code: Código del tipo de habitación (ej: "RM001")
            
        Returns:
            Tupla (property_uuid, category_uuid)
            
        Raises:
            ValueError: Si no se encuentra el mapeo
        """
        if hotel_code not in self.mapping:
            raise ValueError(
                f"Hotel code '{hotel_code}' no encontrado en el mapeo PMS. "
                f"Códigos disponibles: {list(self.mapping.keys())[:10]}..."
            )
        
        hotel_mapping = self.mapping[hotel_code]
        
        if room_type_code not in hotel_mapping["rooms"]:
            raise ValueError(
                f"Room type '{room_type_code}' no encontrado para hotel '{hotel_code}'. "
                f"Room types disponibles: {list(hotel_mapping['rooms'].keys())}"
            )
        
        property_uuid = UUID(hotel_mapping["property_uuid"])
        category_uuid = UUID(hotel_mapping["rooms"][room_type_code]["category_uuid"])
        
        return property_uuid, category_uuid

    def normalize_webhook(self, raw_payload: dict) -> InventoryChangeDTO:
        """
        Normaliza un webhook del Mock PMS.
        
        Formato esperado del Mock PMS:
        {
            "hotel_code": "COL-HOTE-001",
            "room_type_code": "RM001",
            "date": "2026-05-10",
            "available_units": 12,
            "last_modified": "2026-05-09T10:30:00Z"
        }
        """
        try:
            hotel_code = raw_payload["hotel_code"]
            room_type_code = raw_payload["room_type_code"]
            fecha_str = raw_payload["date"]
            cupos = raw_payload["available_units"]
            timestamp_str = raw_payload["last_modified"]
            
            property_uuid, category_uuid = self._get_uuids(hotel_code, room_type_code)
            
            fecha = datetime.fromisoformat(fecha_str.replace('Z', '+00:00')).date()
            event_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
            return InventoryChangeDTO(
                id_propiedad=property_uuid,
                id_categoria=category_uuid,
                fecha=fecha,
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
                    "available_units": 12,
                    "last_modified": "2026-05-09T10:30:00Z"
                },
                ...
            ]
        }
        """
        try:
            changes = raw_response.get("changes", [])
            
            dtos = []
            for change in changes:
                dto = self.normalize_webhook(change)
                dtos.append(dto)
            
            return dtos
            
        except (KeyError, ValueError) as e:
            raise ValueError(f"Error al parsear respuesta de polling: {e}")
