"""
Seed completo para Catalog con datos de producción.

Este script crea desde cero:
- Configuración de impuestos por país
- Amenidades estándar
- 100 propiedades (hoteles) en Colombia y México
- Categorías de habitación con códigos PMS
- Inventario para los próximos 30 días
- Temporadas de precio

Ejecutar:
    python scripts/seed_full_catalog.py --purge  # Limpia e inserta
    python scripts/seed_full_catalog.py          # Solo inserta (sin limpiar)
"""

import sys
import argparse
import random
from pathlib import Path
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import NAMESPACE_DNS, UUID, uuid4, uuid5

# Agregar el directorio raíz al path para imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from modules.catalog.infrastructure.models import (
    ConfiguracionImpuestosPaisModel,
    PropiedadModel,
    CategoriaHabitacionModel,
    AmenidadModel,
    MediaModel,
    InventarioModel,
    TemporadaModel,
)
from modules.catalog.infrastructure.database import Base


# Configuración de base de datos (lee variables de entorno o usa defaults locales)
import os
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "catalog_db")

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


def _build_property_id(property_name: str) -> UUID:
    """Genera UUID determinista para propiedad."""
    return uuid5(NAMESPACE_DNS, f"catalog:propiedad:{property_name}")


def _build_category_id(property_name: str, category_type: str) -> UUID:
    """Genera UUID determinista para categoría."""
    return uuid5(NAMESPACE_DNS, f"categoria:{property_name}:{category_type}")


# ============================================================================
# DATOS DE CONFIGURACIÓN
# ============================================================================

# Configuración de impuestos por país (de la imagen 3)
TAXES_CONFIG = [
    {"pais": "Colombia", "moneda": "COP", "simbolo": "$", "locale": "es_CO", "decimales": 0, "tasa_usd": 4200.0, "impuesto": "IVA", "tasa": 0.19},
    {"pais": "Perú", "moneda": "PEN", "simbolo": "S/", "locale": "es_PE", "decimales": 2, "tasa_usd": 3.75, "impuesto": "IGV", "tasa": 0.18},
    {"pais": "Ecuador", "moneda": "USD", "simbolo": "$", "locale": "en_US", "decimales": 2, "tasa_usd": 1.0, "impuesto": "IVA", "tasa": 0.15},
    {"pais": "México", "moneda": "MXN", "simbolo": "$", "locale": "es_MX", "decimales": 2, "tasa_usd": 17.0, "impuesto": "IVA", "tasa": 0.16},
    {"pais": "Chile", "moneda": "CLP", "simbolo": "$", "locale": "es_CL", "decimales": 0, "tasa_usd": 950.0, "impuesto": "IVA", "tasa": 0.19},
    {"pais": "Argentina", "moneda": "USD", "simbolo": "$", "locale": "en_US", "decimales": 2, "tasa_usd": 1.0, "impuesto": "IVA", "tasa": 0.21},
    {"pais": "USA", "moneda": "USD", "simbolo": "$", "locale": "en_US", "decimales": 2, "tasa_usd": 1.0, "impuesto": "Hotel Tax", "tasa": 0.12},
]

# Amenidades estándar (de la imagen 2)
AMENITIES = [
    {"id": "amenity-pool", "nombre": "Piscina", "icono": "pool-icon"},
    {"id": "amenity-wifi", "nombre": "WiFi", "icono": "wifi-icon"},
    {"id": "amenity-spa", "nombre": "Spa", "icono": "spa-icon"},
    {"id": "amenity-kitchen", "nombre": "Cocina", "icono": "kitchen-icon"},
    {"id": "amenity-gym", "nombre": "Gym", "icono": "gym-icon"},
    {"id": "amenity-restaurant", "nombre": "Restaurante", "icono": "restaurant-icon"},
    {"id": "amenity-ac", "nombre": "Aire Acondicionado", "icono": "ac-icon"},
    {"id": "amenity-laundry", "nombre": "Lavandería", "icono": "laundry-icon"},
    {"id": "amenity-fireplace", "nombre": "Chimenea", "icono": "fire-icon"},
]

# Temporadas (de la imagen 1)
SEASONS = [
    {"nombre": "Verano", "fecha_inicio": "2026-06-01", "fecha_fin": "2026-08-31", "porcentaje": 25},
    {"nombre": "Navidad", "fecha_inicio": "2025-12-15", "fecha_fin": "2026-01-05", "porcentaje": 40},
    {"nombre": "Mitad de año", "fecha_inicio": "2026-06-15", "fecha_fin": "2026-07-15", "porcentaje": 30},
]

# ============================================================================
# GENERADOR DE PROPIEDADES
# ============================================================================

# Imágenes de Unsplash para hoteles
HOTEL_IMAGES = [
    "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1540518614846-7eded433c457?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800",
    "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800",
    "https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1560185127-6ed189bf02f4?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800",
    "https://images.unsplash.com/photo-1595576508898-0ad5c879a061?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800",
    "https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=800&q=80",
]

# Tipos de propiedades con sus características
PROPERTY_TYPES = {
    "Hotel": {"price_range": (150000, 500000), "capacity_range": (2, 6), "stars_range": (3, 5)},
    "Apartamento": {"price_range": (200000, 450000), "capacity_range": (4, 8), "stars_range": (3, 5)},
    "Resort": {"price_range": (500000, 900000), "capacity_range": (6, 10), "stars_range": (4, 5)},
    "Cabaña": {"price_range": (120000, 300000), "capacity_range": (4, 8), "stars_range": (3, 4)},
    "Hostal": {"price_range": (60000, 150000), "capacity_range": (2, 4), "stars_range": (2, 3)},
    "Finca": {"price_range": (180000, 350000), "capacity_range": (6, 12), "stars_range": (3, 4)},
}

# Ciudades con coordenadas
CITIES = {
    "Cartagena": {"estado": "Bolivar", "pais": "Colombia", "lat": 10.3910, "lng": -75.5346, "count": 40},
    "Bogotá": {"estado": "Cundinamarca", "pais": "Colombia", "lat": 4.6097, "lng": -74.0817, "count": 20},
    "Medellín": {"estado": "Antioquia", "pais": "Colombia", "lat": 6.2442, "lng": -75.5812, "count": 10},
    "Cancún": {"estado": "Quintana Roo", "pais": "México", "lat": 21.1619, "lng": -86.8515, "count": 10},
    "Ciudad de México": {"estado": "Ciudad de México", "pais": "México", "lat": 19.4326, "lng": -99.1332, "count": 10},
    "Cali": {"estado": "Valle del Cauca", "pais": "Colombia", "lat": 3.4516, "lng": -76.5320, "count": 4},
    "Santa Marta": {"estado": "Magdalena", "pais": "Colombia", "lat": 11.2408, "lng": -74.1990, "count": 3},
    "Barranquilla": {"estado": "Atlántico", "pais": "Colombia", "lat": 10.9685, "lng": -74.7813, "count": 3},
}

# Adjetivos para nombres
ADJECTIVES = ["Premium", "Boutique", "Imperial", "Real", "Express", "Eco", "Central", "Deluxe", "Grand", "Royal"]
DESCRIPTORS = ["Vista Mar", "Centro Histórico", "Zona Rosa", "Playa Dorada", "Colonial", "Moderno"]


def generate_properties(total_count=100):
    """Genera propiedades de forma programática con variación."""
    properties = []
    property_counter = 1
    
    for city_name, city_data in CITIES.items():
        city_count = city_data["count"]
        
        for i in range(city_count):
            # Seleccionar tipo de propiedad de forma balanceada
            type_name = list(PROPERTY_TYPES.keys())[property_counter % len(PROPERTY_TYPES)]
            type_config = PROPERTY_TYPES[type_name]
            
            # Generar características aleatorias dentro de rangos
            precio_base = random.randint(type_config["price_range"][0], type_config["price_range"][1])
            capacidad = random.randint(type_config["capacity_range"][0], type_config["capacity_range"][1])
            estrellas = random.randint(type_config["stars_range"][0], type_config["stars_range"][1])
            
            # Nombre único
            adjective = random.choice(ADJECTIVES)
            descriptor = random.choice(DESCRIPTORS) if random.random() > 0.5 else city_name
            nombre = f"{type_name} {adjective} {descriptor} {property_counter}"
            
            # Código PMS único
            prefix = "MEX" if city_data["pais"] == "México" else "COL"
            codigo_pms = f"{prefix}-{type_name.upper()[:4]}-{property_counter:03d}"
            room_code = f"RM{property_counter:03d}"
            
            # Variación de coordenadas para evitar duplicados
            lat_offset = random.uniform(-0.05, 0.05)
            lng_offset = random.uniform(-0.05, 0.05)
            
            # Seleccionar amenidades (3-6 aleatorias)
            num_amenities = random.randint(3, 6)
            amenidades_seleccionadas = random.sample([a["id"] for a in AMENITIES], num_amenities)
            
            # Seleccionar 2 imágenes aleatorias
            imagenes_seleccionadas = random.sample(HOTEL_IMAGES, 2)
            
            property_data = {
                "nombre": nombre,
                "ciudad": city_name,
                "estado_provincia": city_data["estado"],
                "pais": city_data["pais"],
                "estrellas": estrellas,
                "lat": round(city_data["lat"] + lat_offset, 4),
                "lng": round(city_data["lng"] + lng_offset, 4),
                "categoria_tipo": type_name,
                "categoria_nombre": f"{type_name} {adjective}",
                "descripcion": f"Excelente {type_name.lower()} en {city_name} con todas las comodidades",
                "precio_base": precio_base,
                "capacidad": capacidad,
                "codigo_pms": codigo_pms,
                "room_type_code": room_code,
                "amenidades": amenidades_seleccionadas,
                "imagenes": imagenes_seleccionadas,
            }
            
            properties.append(property_data)
            property_counter += 1
            
            if property_counter > total_count:
                return properties
    
    return properties


# Generar las 100 propiedades
PROPERTIES_DATA = generate_properties(100)

# ============================================================================
# PROPIEDADES LEGACY (COMENTADAS - REEMPLAZADAS POR GENERADOR)
# ============================================================================

"""
PROPERTIES_DATA_OLD = [
    # COLOMBIA - Cartagena
    {
        "nombre": "Cabaña Real Medellín 171",
        "ciudad": "Cartagena",
        "estado_provincia": "Bolivar",
        "pais": "Colombia",
        "estrellas": 4,
        "lat": 10.3910,
        "lng": -75.5346,
        "categoria_tipo": "Cabaña",
        "categoria_nombre": "Cabaña Real Medellín 171",
        "descripcion": "Confortable opción en Medellín",
        "precio_base": 180000,
        "capacidad": 4,
        "codigo_pms": "CAT-HOTEL-01",
        "room_type_code": "STND",
        "amenidades": ["amenity-wifi", "amenity-pool", "amenity-ac"],
        "imagenes": [
            "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=800&q=80",
        ],
    },
    {
        "nombre": "Apartamento Premium Medellín 172",
        "ciudad": "Cartagena",
        "estado_provincia": "Bolivar",
        "pais": "Colombia",
        "estrellas": 5,
        "lat": 10.3920,
        "lng": -75.5350,
        "categoria_tipo": "Apartamento",
        "categoria_nombre": "Apartamento Premium Medellín 172",
        "descripcion": "Confortable opción en Medellín",
        "precio_base": 320000,
        "capacidad": 6,
        "codigo_pms": "CAT-HOSTAL-02",
        "room_type_code": "COMP",
        "amenidades": ["amenity-wifi", "amenity-kitchen", "amenity-laundry"],
        "imagenes": [
            "https://images.unsplash.com/photo-1540518614846-7eded433c457?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800",
        ],
    },
    {
        "nombre": "Resort Premium Bogotá 173",
        "ciudad": "Cartagena",
        "estado_provincia": "Bolivar",
        "pais": "Colombia",
        "estrellas": 5,
        "lat": 10.3930,
        "lng": -75.5360,
        "categoria_tipo": "Resort",
        "categoria_nombre": "Resort Premium Bogotá 173",
        "descripcion": "Confortable opción en Bogotá",
        "precio_base": 550000,
        "capacidad": 8,
        "codigo_pms": "CAT-CABANA-03",
        "room_type_code": "PRIV",
        "amenidades": ["amenity-pool", "amenity-spa", "amenity-restaurant", "amenity-gym"],
        "imagenes": [
            "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800",
            "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80",
        ],
    },
    # COLOMBIA - Bogotá
    {
        "nombre": "Hotel Eco Medellín 174",
        "ciudad": "Bogotá",
        "estado_provincia": "Cundinamarca",
        "pais": "Colombia",
        "estrellas": 4,
        "lat": 4.6097,
        "lng": -74.0817,
        "categoria_tipo": "Hotel",
        "categoria_nombre": "Hotel Eco Medellín 174",
        "descripcion": "Confortable opción en Medellín",
        "precio_base": 210000,
        "capacidad": 4,
        "codigo_pms": "CAT-HOTEL-04",
        "room_type_code": "ECO",
        "amenidades": ["amenity-wifi", "amenity-restaurant", "amenity-gym"],
        "imagenes": [
            "https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1560185127-6ed189bf02f4?auto=format&fit=crop&w=800&q=80",
        ],
    },
    {
        "nombre": "Resort Imperial Cartagena 175",
        "ciudad": "Bogotá",
        "estado_provincia": "Cundinamarca",
        "pais": "Colombia",
        "estrellas": 5,
        "lat": 4.6107,
        "lng": -74.0827,
        "categoria_tipo": "Resort",
        "categoria_nombre": "Resort Imperial Cartagena 175",
        "descripcion": "Confortable opción en Cartagena",
        "precio_base": 680000,
        "capacidad": 10,
        "codigo_pms": "CAT-RESORT-05",
        "room_type_code": "IMPR",
        "amenidades": ["amenity-pool", "amenity-spa", "amenity-restaurant", "amenity-gym", "amenity-ac"],
        "imagenes": [
            "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800",
            "https://images.unsplash.com/photo-1595576508898-0ad5c879a061?auto=format&fit=crop&w=800&q=80",
        ],
    },
    # COLOMBIA - Medellín
    {
        "nombre": "Hotel Premium Bogotá 176",
        "ciudad": "Medellín",
        "estado_provincia": "Antioquia",
        "pais": "Colombia",
        "estrellas": 5,
        "lat": 6.2442,
        "lng": -75.5812,
        "categoria_tipo": "Hotel",
        "categoria_nombre": "Hotel Premium Bogotá 176",
        "descripcion": "Confortable opción en Bogotá",
        "precio_base": 380000,
        "capacidad": 4,
        "codigo_pms": "CAT-HOTEL-06",
        "room_type_code": "PREM",
        "amenidades": ["amenity-wifi", "amenity-pool", "amenity-spa", "amenity-restaurant"],
        "imagenes": [
            "https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800",
            "https://images.unsplash.com/photo-1505691938895-1758d7feb511?auto=format&fit=crop&w=800&q=80",
        ],
    },
    {
        "nombre": "Finca Express Cartagena 177",
        "ciudad": "Medellín",
        "estado_provincia": "Antioquia",
        "pais": "Colombia",
        "estrellas": 3,
        "lat": 6.2452,
        "lng": -75.5822,
        "categoria_tipo": "Finca",
        "categoria_nombre": "Finca Express Cartagena 177",
        "descripcion": "Confortable opción en Cartagena",
        "precio_base": 150000,
        "capacidad": 8,
        "codigo_pms": "CAT-FINCA-07",
        "room_type_code": "EXPR",
        "amenidades": ["amenity-wifi", "amenity-fireplace", "amenity-kitchen"],
        "imagenes": [
            "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1566665797739-1674de7a421a?auto=format&fit=crop&w=800&q=80",
        ],
    },
    # MÉXICO - Cancún
    {
        "nombre": "Resort Boutique Cancún 178",
        "ciudad": "Cancún",
        "estado_provincia": "Quintana Roo",
        "pais": "México",
        "estrellas": 5,
        "lat": 21.1619,
        "lng": -86.8515,
        "categoria_tipo": "Resort",
        "categoria_nombre": "Resort Boutique Cancún 178",
        "descripcion": "Resort de lujo frente al mar Caribe",
        "precio_base": 850000,
        "capacidad": 6,
        "codigo_pms": "MEX-RESORT-01",
        "room_type_code": "BTQE",
        "amenidades": ["amenity-pool", "amenity-spa", "amenity-restaurant", "amenity-gym", "amenity-ac"],
        "imagenes": [
            "https://images.unsplash.com/photo-1540518614846-7eded433c457?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800",
        ],
    },
    {
        "nombre": "Hotel Premium Ciudad de México 179",
        "ciudad": "Ciudad de México",
        "estado_provincia": "Ciudad de México",
        "pais": "México",
        "estrellas": 4,
        "lat": 19.4326,
        "lng": -99.1332,
        "categoria_tipo": "Hotel",
        "categoria_nombre": "Hotel Premium Ciudad de México 179",
        "descripcion": "Hotel moderno en el corazón de la ciudad",
        "precio_base": 420000,
        "capacidad": 4,
        "codigo_pms": "MEX-HOTEL-02",
        "room_type_code": "CDMX",
        "amenidades": ["amenity-wifi", "amenity-restaurant", "amenity-gym", "amenity-ac"],
        "imagenes": [
            "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=800",
            "https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=800&q=80",
        ],
    },
]
"""


def seed_database(purge=False):
    """Ejecuta el seed completo de la base de datos.
    
    Args:
        purge: Si es True, limpia todas las tablas antes de insertar.
    """
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        if purge:
            print("🗑️  Limpiando datos existentes...")
            
            # Limpiar en orden inverso de dependencias
            session.execute(text("TRUNCATE TABLE categoria_amenidad CASCADE"))
            session.execute(text("TRUNCATE TABLE resenas CASCADE"))
            session.execute(text("TRUNCATE TABLE temporadas CASCADE"))
            session.execute(text("TRUNCATE TABLE inventario CASCADE"))
            session.execute(text("TRUNCATE TABLE media CASCADE"))
            session.execute(text("TRUNCATE TABLE categorias_habitacion CASCADE"))
            session.execute(text("TRUNCATE TABLE propiedades CASCADE"))
            session.execute(text("TRUNCATE TABLE amenidades CASCADE"))
            session.execute(text("TRUNCATE TABLE configuracion_impuestos_pais CASCADE"))
            session.commit()
            print("✅ Datos limpiados")
        else:
            print("ℹ️  Modo inserción (sin purga). Use --purge para limpiar datos existentes.")

        # 1. Insertar configuración de impuestos
        print("\n💰 Insertando configuración de impuestos...")
        for tax in TAXES_CONFIG:
            config = ConfiguracionImpuestosPaisModel(
                pais=tax["pais"],
                moneda=tax["moneda"],
                simbolo_moneda=tax["simbolo"],
                locale=tax["locale"],
                decimales=tax["decimales"],
                tasa_usd=Decimal(str(tax["tasa_usd"])),
                impuesto_nombre=tax["impuesto"],
                impuesto_tasa=Decimal(str(tax["tasa"])),
            )
            session.add(config)
        session.commit()
        print(f"✅ {len(TAXES_CONFIG)} configuraciones de impuestos insertadas")

        # 2. Insertar amenidades
        print("\n🏊 Insertando amenidades...")
        amenidades_dict = {}
        for amenity in AMENITIES:
            amenidad = AmenidadModel(
                id_amenidad=amenity["id"],
                nombre=amenity["nombre"],
                icono=amenity["icono"],
            )
            session.add(amenidad)
            amenidades_dict[amenity["id"]] = amenidad
        session.commit()
        print(f"✅ {len(AMENITIES)} amenidades insertadas")

        # 3. Insertar propiedades, categorías, inventario, etc.
        print("\n🏨 Insertando propiedades y categorías...")
        
        today = date.today()
        
        for idx, prop_data in enumerate(PROPERTIES_DATA, start=1):
            # Crear propiedad
            property_id = _build_property_id(prop_data["nombre"])
            
            propiedad = PropiedadModel(
                id_propiedad=property_id,
                nombre=prop_data["nombre"],
                estrellas=prop_data["estrellas"],
                ciudad=prop_data["ciudad"],
                estado_provincia=prop_data["estado_provincia"],
                pais=prop_data["pais"],
                latitud=prop_data["lat"],
                longitud=prop_data["lng"],
                porcentaje_impuesto=Decimal("19.00") if prop_data["pais"] == "Colombia" else Decimal("16.00"),
            )
            session.add(propiedad)
            
            # Crear categoría
            category_id = _build_category_id(prop_data["nombre"], prop_data["categoria_tipo"])
            
            categoria = CategoriaHabitacionModel(
                id_categoria=category_id,
                id_propiedad=property_id,
                codigo_mapeo_pms=prop_data["codigo_pms"],
                nombre_comercial=prop_data["categoria_nombre"],
                descripcion=prop_data["descripcion"],
                precio_base_monto=Decimal(str(prop_data["precio_base"])),
                precio_base_moneda="COP",
                precio_base_cargo_servicio=Decimal("15000"),
                capacidad_pax=prop_data["capacidad"],
                dias_anticipacion=3,
                porcentaje_penalidad=Decimal("25.00"),
                # Tarifas diferenciadas
                tarifa_fin_de_semana_monto=Decimal(str(prop_data["precio_base"] * 1.15)),
                tarifa_fin_de_semana_moneda="COP",
                tarifa_fin_de_semana_cargo_servicio=Decimal("17000"),
                tarifa_temporada_alta_monto=Decimal(str(prop_data["precio_base"] * 1.30)),
                tarifa_temporada_alta_moneda="COP",
                tarifa_temporada_alta_cargo_servicio=Decimal("20000"),
            )
            session.add(categoria)
            
            # Asociar amenidades
            for amenity_id in prop_data["amenidades"]:
                if amenity_id in amenidades_dict:
                    categoria.amenidades.append(amenidades_dict[amenity_id])
            
            # Agregar imágenes
            for img_idx, img_url in enumerate(prop_data["imagenes"], start=1):
                media = MediaModel(
                    id_media=f"media-{category_id}-{img_idx}",
                    id_categoria=category_id,
                    url_full=img_url,
                    tipo="FOTO_PORTADA" if img_idx == 1 else "IMAGEN_GALERIA",
                    orden=img_idx,
                )
                session.add(media)
            
            # Crear inventario para los próximos 30 días
            for day_offset in range(30):
                inv_date = (today + timedelta(days=day_offset)).isoformat()
                inventario = InventarioModel(
                    id_inventario=f"inv-{category_id}-{day_offset}",
                    id_categoria=category_id,
                    fecha=inv_date,
                    cupos_totales=10,
                    cupos_disponibles=10 if day_offset % 2 == 0 else 5,  # Variación para testing
                )
                session.add(inventario)
            
            # Agregar temporadas a la propiedad
            for season in SEASONS:
                temporada = TemporadaModel(
                    id_temporada=uuid4(),
                    id_propiedad=property_id,
                    nombre=season["nombre"],
                    fecha_inicio=season["fecha_inicio"],
                    fecha_fin=season["fecha_fin"],
                    porcentaje=Decimal(str(season["porcentaje"])),
                )
                session.add(temporada)
            
            print(f"  ✅ {idx}. {prop_data['nombre']} ({prop_data['ciudad']}, {prop_data['pais']})")
        
        session.commit()
        print(f"\n✅ {len(PROPERTIES_DATA)} propiedades insertadas con categorías, inventario y temporadas")
        
        # Resumen final
        print("\n" + "="*60)
        print("🎉 SEED COMPLETADO EXITOSAMENTE")
        print("="*60)
        print(f"📊 Resumen:")
        print(f"   • Países configurados: {len(TAXES_CONFIG)}")
        print(f"   • Amenidades: {len(AMENITIES)}")
        print(f"   • Propiedades: {len(PROPERTIES_DATA)}")
        print(f"   • Categorías: {len(PROPERTIES_DATA)}")
        print(f"   • Inventario: {len(PROPERTIES_DATA) * 30} registros (30 días por categoría)")
        print(f"   • Temporadas: {len(PROPERTIES_DATA) * len(SEASONS)} registros")
        print(f"   • Imágenes: {sum(len(p['imagenes']) for p in PROPERTIES_DATA)} registros")
        print("="*60)
        
    except Exception as e:
        session.rollback()
        print(f"\n❌ Error durante el seed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Seed de Catalog con 100 propiedades",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python scripts/seed_full_catalog.py --purge   # Limpia e inserta
  python scripts/seed_full_catalog.py           # Solo inserta (sin limpiar)
        """
    )
    parser.add_argument(
        "--purge",
        action="store_true",
        help="Limpia todas las tablas antes de insertar datos"
    )
    
    args = parser.parse_args()
    
    print("🚀 Iniciando seed de Catalog...")
    print("="*60)
    if args.purge:
        print("⚠️  MODO PURGA ACTIVADO - Se eliminarán todos los datos existentes")
    print("="*60)
    
    seed_database(purge=args.purge)
