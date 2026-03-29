from __future__ import annotations

import asyncio
import copy
import random
from datetime import datetime, timedelta, timezone

from src.domain.enums import ResourceType
from src.domain.models import SyncBatchEvent


class MockPMSAdapter:
    source_system = "mock-pms"

    def __init__(self, seed: int = 42) -> None:
        self._rng = random.Random(seed)
        self._lock = asyncio.Lock()
        self._event_counter = 0
        self._properties = [
            {
                "property_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
                "nombre": "Hotel Boutique Las Palmas",
                "estrellas": 4,
                "ubicacion": {
                    "ciudad": "Cartagena",
                    "pais": "Colombia",
                    "coordenadas": {"lat": 10.42, "lng": -75.54},
                },
                "porcentaje_impuesto": 19.0,
                "updated_at": self._timestamp(),
            },
            {
                "property_id": "9f1c2a88-6a40-4f41-92fa-3c6d5bd91f00",
                "nombre": "Eco Hotel Sierra Nevada",
                "estrellas": 5,
                "ubicacion": {
                    "ciudad": "Santa Marta",
                    "pais": "Colombia",
                    "coordenadas": {"lat": 11.24, "lng": -74.21},
                },
                "porcentaje_impuesto": 19.0,
                "updated_at": self._timestamp(),
            },
        ]
        self._room_types = [
            {
                "property_id": self._properties[0]["property_id"],
                "category_id": "c987d654-1111-4ef9-a222-1234567890ab",
                "codigo_mapeo_pms": "ROOM-DLX-01",
                "nombre_comercial": "Habitacion Deluxe con Vista al Mar",
                "descripcion": "Amplia habitacion de 40m2 con balcon privado y zona de descanso.",
                "precio_base": {"monto": 350000.0, "moneda": "COP"},
                "capacidad_pax": 4,
                "politica_cancelacion": {
                    "dias_anticipacion": 5,
                    "porcentaje_penalidad": 50.0,
                },
                "amenidades": [
                    {
                        "id_amenidad": "am3n-1122-3344",
                        "nombre": "Aire Acondicionado",
                        "icono": "fa-snowflake",
                    },
                    {
                        "id_amenidad": "am3n-2233-4455",
                        "nombre": "Wifi",
                        "icono": "fa-wifi",
                    },
                ],
                "media": [
                    {
                        "id_media": "m3d1a-9876-abcd",
                        "url_full": "https://cdn.travelhub.com/h/hotel/deluxe.jpg",
                        "tipo": "IMAGEN_GALERIA",
                        "orden": 1,
                    },
                    {
                        "id_media": "m3d1a-9876-efgh",
                        "url_full": "https://cdn.travelhub.com/h/hotel/deluxe-cover.jpg",
                        "tipo": "FOTO_PORTADA",
                        "orden": 2,
                    },
                ],
                "updated_at": self._timestamp(),
            },
            {
                "property_id": self._properties[0]["property_id"],
                "category_id": "c987d654-2222-4ef9-a222-1234567890ab",
                "codigo_mapeo_pms": "ROOM-STD-02",
                "nombre_comercial": "Habitacion Estandar Familiar",
                "descripcion": "Habitacion funcional con dos camas dobles y escritorio de trabajo.",
                "precio_base": {"monto": 280000.0, "moneda": "COP"},
                "capacidad_pax": 4,
                "politica_cancelacion": {
                    "dias_anticipacion": 3,
                    "porcentaje_penalidad": 30.0,
                },
                "amenidades": [
                    {
                        "id_amenidad": "am3n-3344-5566",
                        "nombre": "TV",
                        "icono": "fa-tv",
                    },
                    {
                        "id_amenidad": "am3n-4455-6677",
                        "nombre": "Desayuno Incluido",
                        "icono": "fa-mug-hot",
                    },
                ],
                "media": [
                    {
                        "id_media": "m3d1a-1111-abcd",
                        "url_full": "https://cdn.travelhub.com/h/hotel/standard.jpg",
                        "tipo": "IMAGEN_GALERIA",
                        "orden": 1,
                    }
                ],
                "updated_at": self._timestamp(),
            },
            {
                "property_id": self._properties[1]["property_id"],
                "category_id": "c987d654-3333-4ef9-a222-1234567890ab",
                "codigo_mapeo_pms": "ROOM-SUI-03",
                "nombre_comercial": "Suite Premium con Terraza",
                "descripcion": "Suite amplia con terraza privada, minibar y vista a la montana.",
                "precio_base": {"monto": 520000.0, "moneda": "COP"},
                "capacidad_pax": 3,
                "politica_cancelacion": {
                    "dias_anticipacion": 7,
                    "porcentaje_penalidad": 60.0,
                },
                "amenidades": [
                    {
                        "id_amenidad": "am3n-5566-7788",
                        "nombre": "Minibar",
                        "icono": "fa-wine-bottle",
                    },
                    {
                        "id_amenidad": "am3n-6677-8899",
                        "nombre": "Bata de Bano",
                        "icono": "fa-person-booth",
                    },
                ],
                "media": [
                    {
                        "id_media": "m3d1a-2222-abcd",
                        "url_full": "https://cdn.travelhub.com/h/hotel/suite.jpg",
                        "tipo": "IMAGEN_GALERIA",
                        "orden": 1,
                    }
                ],
                "updated_at": self._timestamp(),
            },
        ]
        today = datetime.now(tz=timezone.utc).date()
        self._availability = [
            {
                "property_id": room_type["property_id"],
                "category_id": room_type["category_id"],
                "inventory_id": f"inv-{today + timedelta(days=offset)}-{room_type['codigo_mapeo_pms'].lower()}",
                "fecha": str(today + timedelta(days=offset)),
                "cupos_totales": 10 if room_type["codigo_mapeo_pms"] != "ROOM-SUI-03" else 6,
                "cupos_disponibles": max(0, (8 - offset) if room_type["codigo_mapeo_pms"] != "ROOM-SUI-03" else (4 - offset)),
                "updated_at": self._timestamp(),
            }
            for room_type in self._room_types
            for offset in range(3)
        ]
        self._rates = [
            {
                "property_id": room_type["property_id"],
                "category_id": room_type["category_id"],
                "codigo_mapeo_pms": room_type["codigo_mapeo_pms"],
                "precio_base": copy.deepcopy(room_type["precio_base"]),
                "updated_at": self._timestamp(),
            }
            for room_type in self._room_types
        ]

    async def fetch_properties(self) -> list[dict]:
        return await self._snapshot(self._properties)

    async def fetch_room_types(self) -> list[dict]:
        return await self._snapshot(self._room_types)

    async def fetch_availability(self) -> list[dict]:
        return await self._snapshot(self._availability)

    async def fetch_rates(self) -> list[dict]:
        return await self._snapshot(self._rates)

    async def generate_event(
        self,
        resource_type: ResourceType | None = None,
    ) -> SyncBatchEvent:
        async with self._lock:
            target_resource = resource_type or self._rng.choice(list(ResourceType))
            event_id = self._next_event_id(target_resource)
            if target_resource is ResourceType.PROPERTY:
                record = self._mutate_property(event_id)
            elif target_resource is ResourceType.ROOM_TYPE:
                record = self._mutate_room_type(event_id)
            elif target_resource is ResourceType.AVAILABILITY:
                record = self._mutate_availability(event_id)
            else:
                record = self._mutate_rate(event_id)

        return SyncBatchEvent(
            resource_type=target_resource,
            records=[copy.deepcopy(record)],
            source_event_id=event_id,
            source_system=self.source_system,
            occurred_at=datetime.now(tz=timezone.utc),
            trigger="event-simulation",
        )

    async def _snapshot(self, source: list[dict]) -> list[dict]:
        async with self._lock:
            return copy.deepcopy(source)

    def _mutate_property(self, event_id: str) -> dict:
        record = self._rng.choice(self._properties)
        record["estrellas"] = max(1, min(5, record["estrellas"] + self._rng.choice([-1, 1])))
        record["updated_at"] = self._timestamp()
        record["event_id"] = event_id
        return record

    def _mutate_room_type(self, event_id: str) -> dict:
        record = self._rng.choice(self._room_types)
        suffix = self._rng.choice(["Renovada", "Premium", "Signature"])
        record["nombre_comercial"] = f"{record['nombre_comercial'].split(' con ')[0]} {suffix}"
        record["capacidad_pax"] = max(1, min(6, record["capacidad_pax"] + self._rng.choice([-1, 1])))
        record["updated_at"] = self._timestamp()
        record["event_id"] = event_id
        return record

    def _mutate_availability(self, event_id: str) -> dict:
        record = self._rng.choice(self._availability)
        delta = self._rng.choice([-2, -1, 1, 2])
        record["cupos_disponibles"] = max(0, min(record["cupos_totales"], record["cupos_disponibles"] + delta))
        record["updated_at"] = self._timestamp()
        record["event_id"] = event_id
        return record

    def _mutate_rate(self, event_id: str) -> dict:
        record = self._rng.choice(self._rates)
        delta = self._rng.choice([-20000.0, -10000.0, 10000.0, 25000.0])
        record["precio_base"]["monto"] = round(max(120000.0, record["precio_base"]["monto"] + delta), 2)
        record["updated_at"] = self._timestamp()
        record["event_id"] = event_id
        return record

    def _next_event_id(self, resource_type: ResourceType) -> str:
        self._event_counter += 1
        return f"{self.source_system}-{resource_type.value}-{self._event_counter:06d}"

    def _timestamp(self) -> str:
        return datetime.now(tz=timezone.utc).isoformat()
