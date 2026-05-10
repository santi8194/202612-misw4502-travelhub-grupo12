import json
import random
from datetime import datetime, timedelta, timezone
from seed_full_catalog import generate_properties

def generate_mock_inventory():
    print("🚀 Generando inventario para el Mock PMS basado en el Seed de Catálogo...")
    
    # Generamos las 100 propiedades garantizando el mismo orden y códigos
    properties = generate_properties(100)
    
    inventory_records = []
    
    # Fechas para simular disponibilidad
    hoy = datetime.now(timezone.utc)
    manana = hoy + timedelta(days=1)
    fechas = [hoy, manana]
    
    for prop in properties:
        for fecha in fechas:
            # Simulamos que cada hotel tiene entre 5 y 15 habitaciones en total
            total_units = random.randint(5, 15)
            # Las habitaciones disponibles son iguales o menores al total
            available_units = random.randint(0, total_units)
            
            record = {
                "hotel_code": prop["codigo_pms"],
                "hotel_name": prop["nombre"],
                "room_type_code": prop["room_type_code"],
                "date": fecha.strftime("%Y-%m-%d"),
                "total_units": total_units,
                "available_units": available_units,
                "last_modified": hoy.isoformat()
            }
            inventory_records.append(record)
            
    # Estructura del JSON que espera el mock-pms
    final_data = {
        "description": "Inventario simulado del Mock PMS - Generado automáticamente desde el seed",
        "last_updated": hoy.isoformat(),
        "total_properties": len(properties),
        "inventory": inventory_records
    }
    
    output_file = "inventory_100.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
        
    print("============================================================")
    print(f"✅ Generados {len(inventory_records)} registros de inventario (2 fechas por hotel).")
    print(f"✅ Archivo guardado localmente en: {output_file}")
    print(f"El primer hotel es: {inventory_records[0]['hotel_code']} - {inventory_records[0]['hotel_name']}")
    print("============================================================")
    print("⚠️ POR FAVOR: Copia este archivo a 'Backend/mock-pms/data/' para actualizar el Mock.")

if __name__ == "__main__":
    generate_mock_inventory()
