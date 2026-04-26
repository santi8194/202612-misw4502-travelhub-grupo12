import uuid
import json
from datetime import date, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# --- Configuration ---
DB_USER = "catalog_app"
DB_PASSWORD = "catalog_dev"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "catalog_db"

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# IDs must match Search results to allow detailed view navigation
# We'll use deterministic UUIDs based on names to ensure they match if generated again
def get_uuid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, name))

# Data from search seed
PROPERTIES = [
    {
        "id": "1198587d-8f96-5f36-96b5-0968997a488e", # Deterministic ID for "Hotel Boutique Las Palmas"
        "nombre": "Hotel Boutique Las Palmas",
        "ciudad": "Cartagena",
        "estado_provincia": "Bolívar",
        "pais": "Colombia",
        "latitud": 10.3910,
        "longitud": -75.5346,
        "estrellas": 5,
        "precio": 450000,
        "capacidad": 4,
        "amenidades": [("P01", "Piscina", "pool"), ("W01", "WiFi", "wifi"), ("S01", "Spa", "spa"), ("R01", "Restaurante", "restaurant"), ("G01", "Gym", "fitness_center")],
        "imagen": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80",
    },
    {
        "id": "243354dc-baa1-5dca-8a1a-4290740a6672", # Deterministic ID for "Hostal El Viajero"
        "nombre": "Hostal El Viajero",
        "ciudad": "Bogotá",
        "estado_provincia": "Cundinamarca",
        "pais": "Colombia",
        "latitud": 4.6097,
        "longitud": -74.0817,
        "estrellas": 3,
        "precio": 85000,
        "capacidad": 2,
        "amenidades": [("W01", "WiFi", "wifi"), ("C01", "Cocina compartida", "kitchen"), ("L01", "Lavandería", "local_laundry_service")],
        "imagen": "https://images.unsplash.com/photo-1555854816-802f188095e4?auto=format&fit=crop&w=800&q=80",
    },
    {
        "id": "6112048f-3665-5c1a-8a1a-4290740a6672", # Deterministic ID for "Cabaña Montaña Mágica"
        "nombre": "Cabaña Montaña Mágica",
        "ciudad": "Medellín",
        "estado_provincia": "Antioquia",
        "pais": "Colombia",
        "latitud": 4.6380,
        "longitud": -75.5680,
        "estrellas": 4,
        "precio": 220000,
        "capacidad": 6,
        "amenidades": [("CH01", "Chimenea", "fireplace"), ("B01", "BBQ", "outdoor_grill"), ("J01", "Jardín", "park"), ("W01", "WiFi", "wifi")],
        "imagen": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=800&q=80",
    }
]

def seed():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    print("Cleaning up existing data...")
    session.execute(text("TRUNCATE TABLE media CASCADE"))
    session.execute(text("TRUNCATE TABLE inventario CASCADE"))
    session.execute(text("TRUNCATE TABLE categoria_amenidad CASCADE"))
    session.execute(text("TRUNCATE TABLE categorias_habitacion CASCADE"))
    session.execute(text("TRUNCATE TABLE amenidades CASCADE"))
    session.execute(text("TRUNCATE TABLE propiedades CASCADE"))
    session.commit()

    print("Seeding properties and categories...")
    
    # Global amenities tracking
    seeded_amenities = set()

    for p in PROPERTIES:
        # 1. Insert Property
        prop_id = p["id"]
        session.execute(text("""
            INSERT INTO propiedades (id_propiedad, nombre, estrellas, ciudad, estado_provincia, pais, latitud, longitud, porcentaje_impuesto)
            VALUES (:id, :nombre, :estrellas, :ciudad, :estado, :pais, :lat, :lon, :tax)
        """), {
            "id": prop_id, "nombre": p["nombre"], "estrellas": p["estrellas"], 
            "ciudad": p["ciudad"], "estado": p["estado_provincia"], "pais": p["pais"],
            "lat": p["latitud"], "lon": p["longitud"], "tax": 19.0
        })

        # 2. Insert Amenities for this property
        for am_id, am_name, am_icon in p["amenidades"]:
            if am_id not in seeded_amenities:
                session.execute(text("""
                    INSERT INTO amenidades (id_amenidad, nombre, icono)
                    VALUES (:id, :nombre, :icono)
                """), {"id": am_id, "nombre": am_name, "icono": am_icon})
                seeded_amenities.add(am_id)

        # 3. Create a default Category for this property
        cat_id = str(uuid.uuid4())
        session.execute(text("""
            INSERT INTO categorias_habitacion (id_categoria, id_propiedad, codigo_mapeo_pms, nombre_comercial, descripcion, 
                                             precio_base_monto, precio_base_moneda, precio_base_cargo_servicio, 
                                             capacidad_pax, dias_anticipacion, porcentaje_penalidad)
            VALUES (:id, :prop_id, :code, :name, :desc, :price, :currency, :fee, :pax, :days, :penalty)
        """), {
            "id": cat_id, "prop_id": prop_id, "code": f"PMS-{prop_id[:8]}", 
            "name": f"Habitación Estándar {p['nombre']}", "desc": f"Hermosa habitación en {p['nombre']}",
            "price": p["precio"], "currency": "COP", "fee": 15000, "pax": p["capacidad"],
            "days": 1, "penalty": 10.0
        })

        # 4. Link Category with its Amenities
        for am_id, _, _ in p["amenidades"]:
            session.execute(text("""
                INSERT INTO categoria_amenidad (id_categoria, id_amenidad)
                VALUES (:cat_id, :am_id)
            """), {"cat_id": cat_id, "am_id": am_id})

        # 5. Add Media
        session.execute(text("""
            INSERT INTO media (id_media, id_categoria, url_full, tipo, orden)
            VALUES (:id, :cat_id, :url, :tipo, :orden)
        """), {
            "id": str(uuid.uuid4()), "cat_id": cat_id, "url": p["imagen"], "tipo": "IMAGEN_GALERIA", "orden": 1
        })

        # 6. Add Inventory for the next 30 days
        today = date.today()
        for i in range(30):
            inv_date = (today + timedelta(days=i)).isoformat()
            session.execute(text("""
                INSERT INTO inventario (id_inventario, id_categoria, fecha, cupos_totales, cupos_disponibles)
                VALUES (:id, :cat_id, :fecha, :total, :avail)
            """), {
                "id": str(uuid.uuid4()), "cat_id": cat_id, "fecha": inv_date, "total": 10, "avail": 10
            })

    session.commit()
    print("Catalog seeding complete!")

if __name__ == "__main__":
    seed()
