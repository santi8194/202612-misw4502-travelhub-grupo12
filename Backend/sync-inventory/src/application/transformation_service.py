from __future__ import annotations

from typing import Any

from src.domain.enums import ResourceType


class PMSDataTransformer:
    def transform(
        self,
        resource_type: ResourceType,
        raw_record: dict[str, Any],
    ) -> dict[str, Any]:
        if resource_type is ResourceType.PROPERTY:
            return self._transform_property(raw_record)
        if resource_type is ResourceType.ROOM_TYPE:
            return self._transform_room_type(raw_record)
        if resource_type is ResourceType.AVAILABILITY:
            return self._transform_availability(raw_record)
        if resource_type is ResourceType.RATE:
            return self._transform_rate(raw_record)
        raise ValueError(f"Unsupported resource type: {resource_type}")

    def _transform_property(self, raw_record: dict[str, Any]) -> dict[str, Any]:
        return {
            "idPropiedad": raw_record["property_id"],
            "nombre": raw_record["nombre"],
            "estrellas": raw_record["estrellas"],
            "ubicacion": {
                "ciudad": raw_record["ubicacion"]["ciudad"],
                "pais": raw_record["ubicacion"]["pais"],
                "coordenadas": {
                    "lat": raw_record["ubicacion"]["coordenadas"]["lat"],
                    "lng": raw_record["ubicacion"]["coordenadas"]["lng"],
                },
            },
            "porcentajeImpuesto": raw_record["porcentaje_impuesto"],
        }

    def _transform_room_type(self, raw_record: dict[str, Any]) -> dict[str, Any]:
        return {
            "idPropiedad": raw_record["property_id"],
            "idCategoria": raw_record["category_id"],
            "codigoMapeoPms": raw_record["codigo_mapeo_pms"],
            "nombreComercial": raw_record["nombre_comercial"],
            "descripcion": raw_record["descripcion"],
            "precioBase": self._transform_precio_base(raw_record["precio_base"]),
            "capacidadPax": raw_record["capacidad_pax"],
            "politicaCancelacion": self._transform_politica_cancelacion(
                raw_record["politica_cancelacion"]
            ),
            "amenidades": [
                self._transform_amenidad(amenidad)
                for amenidad in raw_record["amenidades"]
            ],
            "media": [self._transform_media(media) for media in raw_record["media"]],
        }

    def _transform_availability(self, raw_record: dict[str, Any]) -> dict[str, Any]:
        return {
            "idPropiedad": raw_record["property_id"],
            "idCategoria": raw_record["category_id"],
            "idInventario": raw_record["inventory_id"],
            "fecha": raw_record["fecha"],
            "cuposTotales": raw_record["cupos_totales"],
            "cuposDisponibles": raw_record["cupos_disponibles"],
        }

    def _transform_rate(self, raw_record: dict[str, Any]) -> dict[str, Any]:
        return {
            "idPropiedad": raw_record["property_id"],
            "idCategoria": raw_record["category_id"],
            "codigoMapeoPms": raw_record["codigo_mapeo_pms"],
            "precioBase": self._transform_precio_base(raw_record["precio_base"]),
        }

    def _transform_precio_base(self, raw_record: dict[str, Any]) -> dict[str, Any]:
        return {
            "monto": raw_record["monto"],
            "moneda": raw_record["moneda"],
        }

    def _transform_politica_cancelacion(self, raw_record: dict[str, Any]) -> dict[str, Any]:
        return {
            "diasAnticipacion": raw_record["dias_anticipacion"],
            "porcentajePenalidad": raw_record["porcentaje_penalidad"],
        }

    def _transform_amenidad(self, raw_record: dict[str, Any]) -> dict[str, Any]:
        return {
            "idAmenidad": raw_record["id_amenidad"],
            "nombre": raw_record["nombre"],
            "icono": raw_record["icono"],
        }

    def _transform_media(self, raw_record: dict[str, Any]) -> dict[str, Any]:
        return {
            "idMedia": raw_record["id_media"],
            "urlFull": raw_record["url_full"],
            "tipo": raw_record["tipo"],
            "orden": raw_record["orden"],
        }
