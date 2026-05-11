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
    
    La columna disponibilidad es una lista de objetos {"fecha": "YYYY-MM-DD", "cupos": N}.
    La lógica es:
      1. Filtrar y eliminar el objeto con la fecha indicada (si existe).
      2. Si cupos > 0: agregar el nuevo objeto {"fecha": ..., "cupos": ...}.
      3. Si cupos == 0: solo eliminar (la fecha queda sin disponibilidad).
    Las demás fechas del array quedan intactas.
    
    Args:
        pool: Pool de conexiones asyncpg
        id_categoria: UUID de la categoría
        fecha: Fecha del inventario
        cupos: Cupos disponibles
    """
    fecha_str = fecha.isoformat()
    async with pool.acquire() as conn:
        if cupos == 0:
            # Eliminar el objeto con esa fecha; el resto del array queda intacto
            await conn.execute(
                """
                UPDATE search.hospedajes
                SET disponibilidad = (
                    SELECT COALESCE(jsonb_agg(elem ORDER BY elem->>'fecha'), '[]'::jsonb)
                    FROM jsonb_array_elements(disponibilidad) AS elem
                    WHERE elem->>'fecha' != $1::text
                )
                WHERE id_categoria = $2::uuid
                """,
                fecha_str,
                id_categoria,
            )
            print(f"[SEARCH] Fecha {fecha} eliminada del array (cupos=0)")
        else:
            # Eliminar objeto existente con esa fecha y agregar el actualizado
            await conn.execute(
                """
                UPDATE search.hospedajes
                SET disponibilidad = (
                    SELECT COALESCE(jsonb_agg(elem ORDER BY elem->>'fecha'), '[]'::jsonb)
                    FROM jsonb_array_elements(disponibilidad) AS elem
                    WHERE elem->>'fecha' != $1::text
                ) || jsonb_build_array(
                    jsonb_build_object('fecha', $1::text, 'cupos', $3::int)
                )
                WHERE id_categoria = $2::uuid
                """,
                fecha_str,
                id_categoria,
                cupos,
            )
            print(f"[SEARCH] Disponibilidad actualizada: {fecha} -> {cupos} cupos")


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
        
        # Filtrar el objeto existente con esa fecha; el resto queda intacto
        disponibilidad = [elem for elem in disponibilidad if isinstance(elem, dict) and elem.get("fecha") != fecha_str]
        
        if cupos == 0:
            print(f"[SEARCH] Fecha {fecha} eliminada del array (cupos=0)")
        else:
            disponibilidad.append({"fecha": fecha_str, "cupos": cupos})
            disponibilidad.sort(key=lambda e: e["fecha"])
            print(f"[SEARCH] Disponibilidad actualizada: {fecha} -> {cupos} cupos")
        
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


def handle_event(data: dict[str, Any], routing_key: str, pool: Any = None, loop: Any = None) -> None:
    """
    Router de eventos que delega al handler apropiado.
    
    Cuando se invoca desde un hilo daemon (consumer de RabbitMQ), se debe
    pasar el loop principal para usar run_coroutine_threadsafe y evitar el
    CancelledError que ocurre al llamar asyncio.run() desde un hilo diferente
    al que creó el pool de asyncpg.
    
    Args:
        data: Payload del evento
        routing_key: Routing key del mensaje
        pool: Pool de conexiones (solo para PostgreSQL)
        loop: Event loop principal de la aplicación (opcional)
    """
    event_type = data.get("type", "unknown")
    
    coro = None
    if routing_key == "catalog.inventory.updated" or event_type == "InventarioActualizado":
        coro = handle_inventory_updated(data, pool)
    elif routing_key == "catalog.category.pricing.updated" or event_type == "TarifasActualizadas":
        coro = handle_pricing_updated(data, pool)
    else:
        print(f"[SEARCH] Evento no reconocido: {event_type} / {routing_key}")
        return
    
    if loop and loop.is_running():
        # Ejecutar la corutina en el loop principal desde el hilo del consumer
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        try:
            future.result(timeout=10)
        except Exception as e:
            print(f"[SEARCH] Error en tarea asíncrona del evento: {e}")
            raise
    else:
        # Fallback para ejecución directa (tests, scripts)
        asyncio.run(coro)
