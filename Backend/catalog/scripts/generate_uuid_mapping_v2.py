"""
Genera el mapeo completo de códigos PMS a UUIDs para pms-integration.

Este script calcula los UUIDs deterministas de las 100 propiedades del seed
y los exporta en formato JSON y Python.

Ejecutar:
    cd Backend/catalog/scripts
    python3 generate_uuid_mapping_v2.py
"""

import sys
from pathlib import Path
from uuid import NAMESPACE_DNS, uuid5
import json

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

# Importar las propiedades generadas del seed
try:
    from seed_full_catalog import PROPERTIES_DATA
except ImportError:
    print("❌ Error: No se pudo importar seed_full_catalog.py")
    print("   Asegúrate de ejecutar este script desde Backend/catalog/scripts/")
    sys.exit(1)


def _build_property_id(property_name: str) -> str:
    """Genera UUID determinista para propiedad."""
    return str(uuid5(NAMESPACE_DNS, f"catalog:propiedad:{property_name}"))


def _build_category_id(property_name: str, category_type: str) -> str:
    """Genera UUID determinista para categoría."""
    return str(uuid5(NAMESPACE_DNS, f"categoria:{property_name}:{category_type}"))


def generate_mapping():
    """Genera el mapeo completo de códigos PMS a UUIDs."""
    
    mapping = {
        "description": "Mapeo de códigos PMS del Mock a UUIDs reales de TravelHub Catalog",
        "generated_with": "uuid5(NAMESPACE_DNS, key)",
        "total_properties": len(PROPERTIES_DATA),
        "mappings": {}
    }
    
    print("=" * 80)
    print(f"MAPEO DE CÓDIGOS PMS A UUIDs DE CATALOG ({len(PROPERTIES_DATA)} PROPIEDADES)")
    print("=" * 80)
    print()
    
    # Generar mapeo para todas las propiedades
    for idx, prop in enumerate(PROPERTIES_DATA, 1):
        property_uuid = _build_property_id(prop["nombre"])
        category_uuid = _build_category_id(prop["nombre"], prop["categoria_tipo"])
        
        # Agregar al diccionario de mapeo
        mapping["mappings"][prop["codigo_pms"]] = {
            "hotel_code": prop["codigo_pms"],
            "hotel_name": prop["nombre"],
            "ciudad": prop["ciudad"],
            "pais": prop["pais"],
            "property_uuid": property_uuid,
            "rooms": {
                prop["room_type_code"]: {
                    "room_type_code": prop["room_type_code"],
                    "category_type": prop["categoria_tipo"],
                    "category_uuid": category_uuid
                }
            }
        }
        
        # Imprimir solo las primeras 10 y las últimas 5 para no saturar
        if idx <= 10 or idx > len(PROPERTIES_DATA) - 5:
            print(f"🏨 {idx}. {prop['nombre']}")
            print(f"   Ciudad: {prop['ciudad']}, {prop['pais']}")
            print(f"   Código PMS: {prop['codigo_pms']}")
            print(f"   Property UUID: {property_uuid}")
            print(f"   Category UUID: {category_uuid}")
            print()
        elif idx == 11:
            print(f"... ({len(PROPERTIES_DATA) - 15} propiedades más) ...\n")
    
    # Guardar a archivo JSON
    output_file = "pms_uuid_mapping_full.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    print("=" * 80)
    print(f"✅ Mapeo completo guardado en: {output_file}")
    print(f"   Total de propiedades: {len(PROPERTIES_DATA)}")
    print("=" * 80)
    print()
    
    # Generar código Python para pms-integration (primeras 20 para ejemplo)
    print("=" * 80)
    print("CÓDIGO PYTHON PARA pms-integration (PRIMERAS 20 PROPIEDADES)")
    print("=" * 80)
    print()
    print("```python")
    print("from uuid import UUID")
    print()
    print("# Mapeo de códigos Mock PMS a UUIDs de TravelHub")
    print("# NOTA: Este es un ejemplo con las primeras 20 propiedades.")
    print("# Para el mapeo completo, consultar pms_uuid_mapping_full.json")
    print("PMS_MAPPING = {")
    
    for prop in PROPERTIES_DATA[:20]:
        property_uuid = _build_property_id(prop["nombre"])
        category_uuid = _build_category_id(prop["nombre"], prop["categoria_tipo"])
        
        print(f'    "{prop["codigo_pms"]}": {{')
        print(f'        "id_propiedad": UUID("{property_uuid}"),')
        print(f'        "rooms": {{')
        print(f'            "{prop["room_type_code"]}": UUID("{category_uuid}"),')
        print(f'        }}')
        print(f'    }},')
    
    print("    # ... (80 propiedades más en el archivo JSON)")
    print("}")
    print("```")
    print()
    
    # Resumen por ciudad
    print("=" * 80)
    print("RESUMEN POR CIUDAD")
    print("=" * 80)
    cities = {}
    for prop in PROPERTIES_DATA:
        city = prop["ciudad"]
        if city not in cities:
            cities[city] = 0
        cities[city] += 1
    
    for city, count in sorted(cities.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {city}: {count} propiedades")
    print()


if __name__ == "__main__":
    generate_mapping()
