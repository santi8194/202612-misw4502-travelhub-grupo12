"""
Script de verificación del seed de Catalog.

Verifica que el seed se haya ejecutado correctamente y muestra estadísticas.

Ejecutar:
    python3 scripts/verify_seed.py
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os

# Configuración de base de datos
DB_USER = os.getenv("DB_USER", "catalog_app")
DB_PASSWORD = os.getenv("DB_PASSWORD", "catalog_dev")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "catalog_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def verify_seed():
    """Verifica el seed y muestra estadísticas."""
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("=" * 80)
        print("🔍 VERIFICACIÓN DEL SEED DE CATALOG")
        print("=" * 80)
        print()
        
        # 1. Conteo general
        print("📊 CONTEO GENERAL")
        print("-" * 80)
        
        queries = {
            "Configuraciones de impuestos": "SELECT COUNT(*) FROM configuracion_impuestos_pais",
            "Amenidades": "SELECT COUNT(*) FROM amenidades",
            "Propiedades": "SELECT COUNT(*) FROM propiedades",
            "Categorías": "SELECT COUNT(*) FROM categorias_habitacion",
            "Inventario": "SELECT COUNT(*) FROM inventario",
            "Temporadas": "SELECT COUNT(*) FROM temporadas",
            "Imágenes (Media)": "SELECT COUNT(*) FROM media",
        }
        
        for label, query in queries.items():
            result = session.execute(text(query)).scalar()
            status = "✅" if result > 0 else "❌"
            print(f"{status} {label}: {result}")
        
        print()
        
        # 2. Propiedades por ciudad
        print("🌍 DISTRIBUCIÓN POR CIUDAD")
        print("-" * 80)
        
        query = text("""
            SELECT ciudad, pais, COUNT(*) as total
            FROM propiedades
            GROUP BY ciudad, pais
            ORDER BY total DESC
        """)
        
        results = session.execute(query).fetchall()
        for row in results:
            print(f"  • {row.ciudad}, {row.pais}: {row.total} propiedades")
        
        print()
        
        # 3. Códigos PMS
        print("🔑 CÓDIGOS PMS (Primeros 10)")
        print("-" * 80)
        
        query = text("""
            SELECT c.codigo_mapeo_pms, c.nombre_comercial, p.ciudad
            FROM categorias_habitacion c
            JOIN propiedades p ON c.id_propiedad = p.id_propiedad
            ORDER BY c.codigo_mapeo_pms
            LIMIT 10
        """)
        
        results = session.execute(query).fetchall()
        for row in results:
            print(f"  • {row.codigo_mapeo_pms}: {row.nombre_comercial} ({row.ciudad})")
        
        print()
        
        # 4. Inventario por categoría (muestra)
        print("📦 INVENTARIO (Primeras 5 categorías)")
        print("-" * 80)
        
        query = text("""
            SELECT 
                c.codigo_mapeo_pms,
                COUNT(i.id_inventario) as dias_inventario,
                SUM(i.cupos_totales) as total_cupos,
                SUM(i.cupos_disponibles) as cupos_disponibles
            FROM inventario i
            JOIN categorias_habitacion c ON i.id_categoria = c.id_categoria
            GROUP BY c.codigo_mapeo_pms
            ORDER BY c.codigo_mapeo_pms
            LIMIT 5
        """)
        
        results = session.execute(query).fetchall()
        for row in results:
            print(f"  • {row.codigo_mapeo_pms}: {row.dias_inventario} días, {row.total_cupos} cupos totales, {row.cupos_disponibles} disponibles")
        
        print()
        
        # 5. Rangos de precios
        print("💰 RANGOS DE PRECIOS")
        print("-" * 80)
        
        query = text("""
            SELECT 
                MIN(precio_base_noche) as min_precio,
                MAX(precio_base_noche) as max_precio,
                AVG(precio_base_noche)::numeric(10,2) as avg_precio
            FROM categorias_habitacion
        """)
        
        result = session.execute(query).fetchone()
        print(f"  • Precio mínimo: ${result.min_precio:,.0f}")
        print(f"  • Precio máximo: ${result.max_precio:,.0f}")
        print(f"  • Precio promedio: ${result.avg_precio:,.2f}")
        
        print()
        
        # 6. Temporadas
        print("📅 TEMPORADAS")
        print("-" * 80)
        
        query = text("""
            SELECT nombre, COUNT(*) as total_propiedades
            FROM temporadas
            GROUP BY nombre
            ORDER BY nombre
        """)
        
        results = session.execute(query).fetchall()
        for row in results:
            print(f"  • {row.nombre}: {row.total_propiedades} propiedades")
        
        print()
        
        # 7. Verificación de integridad
        print("🔍 VERIFICACIÓN DE INTEGRIDAD")
        print("-" * 80)
        
        # Propiedades sin categorías
        query = text("""
            SELECT COUNT(*) 
            FROM propiedades p
            LEFT JOIN categorias_habitacion c ON p.id_propiedad = c.id_propiedad
            WHERE c.id_categoria IS NULL
        """)
        orphan_props = session.execute(query).scalar()
        status = "✅" if orphan_props == 0 else "⚠️"
        print(f"{status} Propiedades sin categorías: {orphan_props}")
        
        # Categorías sin inventario
        query = text("""
            SELECT COUNT(*) 
            FROM categorias_habitacion c
            LEFT JOIN inventario i ON c.id_categoria = i.id_categoria
            WHERE i.id_inventario IS NULL
        """)
        orphan_cats = session.execute(query).scalar()
        status = "✅" if orphan_cats == 0 else "⚠️"
        print(f"{status} Categorías sin inventario: {orphan_cats}")
        
        # Categorías sin imágenes
        query = text("""
            SELECT COUNT(*) 
            FROM categorias_habitacion c
            LEFT JOIN media m ON c.id_categoria = m.id_categoria
            WHERE m.id_media IS NULL
        """)
        cats_no_images = session.execute(query).scalar()
        status = "✅" if cats_no_images == 0 else "⚠️"
        print(f"{status} Categorías sin imágenes: {cats_no_images}")
        
        print()
        print("=" * 80)
        print("✅ VERIFICACIÓN COMPLETADA")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print()
    verify_seed()
    print()
