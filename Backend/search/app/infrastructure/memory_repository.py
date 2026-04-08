"""Mocks de repositorios en memoria para pruebas de despliegue."""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from decimal import Decimal
from typing import List, Dict

from app.application.ports import DestinationRepository, HospedajeRepository
from app.domain.entities import Coordenadas, Disponibilidad, Hospedaje
from app.domain.strategies import RankingStrategy


class MemoryDestinationRepository(DestinationRepository):
    """Implementación falsa del repositorio de destinos en memoria."""

    def __init__(self):
        self._destinations = [
            {"ciudad": "Bogota", "estado_provincia": "Bogota D.C.", "pais": "Colombia"},
            {"ciudad": "Medellin", "estado_provincia": "Antioquia", "pais": "Colombia"},
            {"ciudad": "Miami", "estado_provincia": "Florida", "pais": "USA"},
            {"ciudad": "Nueva York", "estado_provincia": "Nueva York", "pais": "USA"},
            {"ciudad": "Madrid", "estado_provincia": "Madrid", "pais": "Espana"},
        ]

    async def autocomplete(self, prefix: str) -> List[dict]:
        """Sugerencias simples por prefijo en memoria."""
        prefix_lower = prefix.lower()
        results = [
            d for d in self._destinations
            if d["ciudad"].lower().startswith(prefix_lower)
        ]
        return results[:10]


class MemoryHospedajeRepository(HospedajeRepository):
    """Implementación falsa del repositorio de hospedajes en memoria."""

    def __init__(self):
        # Crear un hospedaje mock de prueba para Bogota
        base_date = date.today()
        disp_bogota = [
            Disponibilidad(fecha=base_date + timedelta(days=i), cupos=5)
            for i in range(30)
        ]
        
        self._hospedajes = [
            Hospedaje(
                id_propiedad=uuid.uuid4(),
                id_categoria=uuid.uuid4(),
                propiedad_nombre="Hotel Mock Bogota",
                categoria_nombre="Hotel",
                imagen_principal_url="https://via.placeholder.com/300",
                amenidades_destacadas=["WiFi", "Piscina"],
                estrellas=5,
                rating_promedio=4.8,
                ciudad="Bogota",
                estado_provincia="Bogota D.C.",
                pais="Colombia",
                coordenadas=Coordenadas(lat=4.6097, lon=-74.0817),
                capacidad_pax=4,
                precio_base=Decimal("150000.00"),
                moneda="COP",
                es_reembolsable=True,
                disponibilidad=disp_bogota
            ),
            Hospedaje(
                id_propiedad=uuid.uuid4(),
                id_categoria=uuid.uuid4(),
                propiedad_nombre="Hostal Mock Medellin",
                categoria_nombre="Hostal",
                imagen_principal_url="https://via.placeholder.com/300",
                amenidades_destacadas=["WiFi"],
                estrellas=3,
                rating_promedio=4.1,
                ciudad="Medellin",
                estado_provincia="Antioquia",
                pais="Colombia",
                coordenadas=Coordenadas(lat=6.2442, lon=-75.5812),
                capacidad_pax=2,
                precio_base=Decimal("80000.00"),
                moneda="COP",
                es_reembolsable=False,
                disponibilidad=disp_bogota
            )
        ]

    async def buscar(
        self,
        ciudad: str,
        estado_provincia: str,
        pais: str,
        fecha_inicio: date,
        fecha_fin: date,
        huespedes: int,
        strategy: RankingStrategy,
    ) -> List[Hospedaje]:
        """Busqueda simulada en memoria."""
        resultados = []
        
        # Filtro basico por ubicacion
        for h in self._hospedajes:
            # Tolerancia basica en busqueda
            c_valido = h.ciudad.lower() == ciudad.lower()
            p_valido = h.pais.lower() == pais.lower()
            
            if c_valido and p_valido:
                # Validar huespedes
                if huespedes > h.capacidad_pax:
                    continue
                    
                # Validar fechas
                dias_requeridos = (fecha_fin - fecha_inicio).days + 1
                disp_valida = 0
                
                for d in h.disponibilidad:
                    if fecha_inicio <= d.fecha <= fecha_fin and d.cupos >= 1:
                        disp_valida += 1
                        
                if disp_valida >= dias_requeridos:
                    resultados.append(h)
                    
        # Ordenar (Mock simple)
        if hasattr(strategy, "sort_field"): # Simple mock sorting idea if possible
            sort_field = getattr(strategy, "sort_field", "precio_base")
            resultados.sort(key=lambda x: getattr(x, sort_field, x.precio_base))
            
        return resultados
