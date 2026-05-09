"""
Handlers para eventos de RabbitMQ en Search.

Procesa eventos de Catalog y actualiza el índice de búsqueda.
"""

import asyncio
from datetime import date
from uuid import UUID
from typing import Any

from app.config import settings


async def handle_inventory_updated(data: dict[str, Any], pool: Any) -> None:
    """
    Maneja el evento InventarioActualizado de Catalog.
    
    Actualiza el JSONB de disponibilidad en la tabla hospedajes:
    - Si cupos_disponibles == 0: elimina la fecha del array
    - Si cupos_disponibles > 0: upsert en el array
    
    Args:
        data: Payload del evento InventarioActualizado
        pool: Pool de conexiones a PostgreSQL o None para SQLite
    """
    try:
        id_categoria = UUID(data["id_categoria"])
        fecha_str = data["fecha"]
        cupos_disponibles = data["cupos_disponibles"]
        
        fecha = date.fromisoformat(fecha_str)
        
        print(f"[SEARCH] Procesando InventarioActualizado: {id_categoria} @ {fecha} -> {cupos_disponibles} cupos")
        
        if settings.use_postgres_database:
            await _update_postgres_availability(pool, id_categoria, fecha, cupos_disponibles)
        else:
            await _update_sqlite_availability(id_categoria, fecha, cupos_disponibles)
        
        print(f"[SEARCH] Disponibilidad actualizada: {id_categoria} @ {fecha}")
        
    except KeyError as e:
        raise ValueError(f"Campo requerido faltante en evento: {e}")
    except Exception as e:
        print(f"[SEARCH] Error procesando InventarioActualizado: {e}")
        raise


async def _update_postgres_availability(pool: Any, id_categoria: UUID, fecha: date, cupos: int) -> None:
    """
    Actualiza disponibilidad en PostgreSQL usando JSONB.
    
    Args:
        pool: Pool de conexiones asyncpg
        id_categoria: UUID de la categoría
        fecha: Fecha del inventario
        cupos: Cupos disponibles
    """
    async with pool.acquire() as conn:
        if cupos == 0:
            await conn.execute(
                """
                UPDATE search.hospedajes
                SET disponibilidad = disponibilidad - $1
                WHERE id_categoria = $2
                """,
                fecha.isoformat(),
                id_categoria
            )
            print(f"[SEARCH] Fecha {fecha} eliminada del array (cupos=0)")
        else:
            await conn.execute(
                """
                UPDATE search.hospedajes
                SET disponibilidad = CASE
                    WHEN disponibilidad ? $1 THEN disponibilidad
                    ELSE disponibilidad || jsonb_build_array($1)
                END
                WHERE id_categoria = $2
                """,
                fecha.isoformat(),
                id_categoria
            )
            print(f"[SEARCH] Fecha {fecha} agregada/mantenida en array (cupos={cupos})")


async def _update_sqlite_availability(id_categoria: UUID, fecha: date, cupos: int) -> None:
    """
    Actualiza disponibilidad en SQLite parseando y modificando JSON.
    
    Args:
        id_categoria: UUID de la categoría
        fecha: Fecha del inventario
        cupos: Cupos disponibles
    """
    import sqlite3
    import json
    
    db_path = settings.sqlite_database_path
    conn = sqlite3.connect(db_path)
    
    try:
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT disponibilidad FROM hospedajes WHERE id_categoria = ?",
            (str(id_categoria),)
        )
        row = cursor.fetchone()
        
        if not row:
            print(f"[SEARCH] Categoría {id_categoria} no encontrada en SQLite")
            return
        
        disponibilidad = json.loads(row[0]) if row[0] else []
        fecha_str = fecha.isoformat()
        
        if cupos == 0:
            if fecha_str in disponibilidad:
                disponibilidad.remove(fecha_str)
                print(f"[SEARCH] Fecha {fecha} eliminada del array (cupos=0)")
        else:
            if fecha_str not in disponibilidad:
                disponibilidad.append(fecha_str)
                disponibilidad.sort()
                print(f"[SEARCH] Fecha {fecha} agregada al array (cupos={cupos})")
        
        cursor.execute(
            "UPDATE hospedajes SET disponibilidad = ? WHERE id_categoria = ?",
            (json.dumps(disponibilidad), str(id_categoria))
        )
        
        conn.commit()
        
    finally:
        conn.close()


async def handle_pricing_updated(data: dict[str, Any], pool: Any) -> None:
    """
    Maneja el evento TarifasActualizadas de Catalog.
    
    Actualiza el precio_base en la tabla hospedajes.
    
    Args:
        data: Payload del evento TarifasActualizadas
        pool: Pool de conexiones a PostgreSQL o None para SQLite
    """
    try:
        id_categoria = UUID(data["id_categoria"])
        precio_base = float(data["tarifa_base_monto"])
        moneda = data["moneda"]
        
        print(f"[SEARCH] Procesando TarifasActualizadas: {id_categoria} -> {precio_base} {moneda}")
        
        if settings.use_postgres_database:
            await _update_postgres_pricing(pool, id_categoria, precio_base, moneda)
        else:
            await _update_sqlite_pricing(id_categoria, precio_base, moneda)
        
        print(f"[SEARCH] Precio actualizado: {id_categoria}")
        
    except KeyError as e:
        raise ValueError(f"Campo requerido faltante en evento: {e}")
    except Exception as e:
        print(f"[SEARCH] Error procesando TarifasActualizadas: {e}")
        raise


async def _update_postgres_pricing(pool: Any, id_categoria: UUID, precio: float, moneda: str) -> None:
    """
    Actualiza precio en PostgreSQL.
    
    Args:
        pool: Pool de conexiones asyncpg
        id_categoria: UUID de la categoría
        precio: Precio base
        moneda: Código de moneda
    """
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE search.hospedajes
            SET precio_base = $1, moneda = $2
            WHERE id_categoria = $3
            """,
            precio,
            moneda,
            id_categoria
        )


async def _update_sqlite_pricing(id_categoria: UUID, precio: float, moneda: str) -> None:
    """
    Actualiza precio en SQLite.
    
    Args:
        id_categoria: UUID de la categoría
        precio: Precio base
        moneda: Código de moneda
    """
    import sqlite3
    
    db_path = settings.sqlite_database_path
    conn = sqlite3.connect(db_path)
    
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE hospedajes SET precio_base = ?, moneda = ? WHERE id_categoria = ?",
            (precio, moneda, str(id_categoria))
        )
        conn.commit()
    finally:
        conn.close()


def handle_event(data: dict[str, Any], routing_key: str, pool: Any = None) -> None:
    """
    Router de eventos que delega al handler apropiado.
    
    Args:
        data: Payload del evento
        routing_key: Routing key del mensaje
        pool: Pool de conexiones (solo para PostgreSQL)
    """
    event_type = data.get("type", "unknown")
    
    if routing_key == "catalog.inventory.updated" or event_type == "InventarioActualizado":
        asyncio.run(handle_inventory_updated(data, pool))
    elif routing_key == "catalog.category.pricing.updated" or event_type == "TarifasActualizadas":
        asyncio.run(handle_pricing_updated(data, pool))
    else:
        print(f"[SEARCH] Evento no reconocido: {event_type} / {routing_key}")
