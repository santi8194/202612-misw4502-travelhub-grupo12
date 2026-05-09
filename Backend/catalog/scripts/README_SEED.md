# 🌱 Seed de Catalog - Guía de Uso

Este directorio contiene scripts para poblar la base de datos de Catalog con datos iniciales.

## 📋 Archivos Disponibles

### `seed_full_catalog.py` ⭐
Script completo que crea desde cero toda la base de datos con:
- ✅ Configuración de impuestos por país (Colombia, México, Perú, Ecuador, Chile, Argentina, USA)
- ✅ Amenidades estándar (Piscina, WiFi, Spa, Cocina, Gym, Restaurante, etc.)
- ✅ **100 propiedades** (hoteles) en Colombia y México
  - 70% concentradas en Cartagena, Bogotá y Medellín
  - Precios variados según tipo (Hostal: $60k-$150k, Hotel: $150k-$500k, Resort: $500k-$900k)
- ✅ Categorías de habitación con códigos PMS mapeables
- ✅ Inventario para los próximos 30 días
- ✅ Temporadas de precio (Verano, Navidad, Mitad de año)
- ✅ Imágenes de Unsplash

### `generate_uuid_mapping_v2.py`
Genera el mapeo completo de códigos PMS a UUIDs para las 100 propiedades.

## 🚀 Ejecución

### Prerequisitos
1. Base de datos PostgreSQL corriendo
2. Variables de entorno configuradas (o modificar el script)

### Opción 1: Con purga de datos (RECOMENDADO)
```bash
cd Backend/catalog
python3 scripts/seed_full_catalog.py --purge
```

### Opción 2: Sin purga (solo inserción)
```bash
cd Backend/catalog
python3 scripts/seed_full_catalog.py
```

### Opción 3: Ver ayuda
```bash
python3 scripts/seed_full_catalog.py --help
```

### Opción 2: Desde Docker
```bash
# Entrar al contenedor de catalog
docker exec -it <catalog-container-id> bash

# Ejecutar el seed
python scripts/seed_full_catalog.py
```

### Opción 3: Modificar configuración de DB
Si tu configuración de base de datos es diferente, edita las variables al inicio del script:

```python
DB_USER = "catalog_app"
DB_PASSWORD = "catalog_dev"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "catalog_db"
```

## 📊 Datos Generados

### Distribución de Propiedades (100 total)

| Ciudad | Cantidad | País | Porcentaje |
|--------|----------|------|------------|
| Cartagena | 40 | Colombia | 40% |
| Bogotá | 20 | Colombia | 20% |
| Medellín | 10 | Colombia | 10% |
| Cancún | 10 | México | 10% |
| Ciudad de México | 10 | México | 10% |
| Cali | 4 | Colombia | 4% |
| Santa Marta | 3 | Colombia | 3% |
| Barranquilla | 3 | Colombia | 3% |

### Tipos de Propiedad y Rangos de Precio

| Tipo | Rango de Precio | Capacidad | Estrellas |
|------|-----------------|-----------|-----------|
| Hostal | $60,000 - $150,000 | 2-4 pax | 2-3 ⭐ |
| Cabaña | $120,000 - $300,000 | 4-8 pax | 3-4 ⭐ |
| Hotel | $150,000 - $500,000 | 2-6 pax | 3-5 ⭐ |
| Finca | $180,000 - $350,000 | 6-12 pax | 3-4 ⭐ |
| Apartamento | $200,000 - $450,000 | 4-8 pax | 3-5 ⭐ |
| Resort | $500,000 - $900,000 | 6-10 pax | 4-5 ⭐ |

### Códigos PMS

- **Colombia**: `COL-HOTE-001` a `COL-FINC-080`
- **México**: `MEX-HOTE-081` a `MEX-RESO-100`

Cada código PMS es único y mapea a un UUID determinista.

### Temporadas Configuradas

| Nombre | Fecha Inicio | Fecha Fin | Incremento |
|--------|--------------|-----------|------------|
| Verano | 2026-06-01 | 2026-08-31 | +25% |
| Navidad | 2025-12-15 | 2026-01-05 | +40% |
| Mitad de año | 2026-06-15 | 2026-07-15 | +30% |

## 🔗 Integración con Mock PMS

Los códigos PMS (`CAT-HOTEL-01`, `CAT-HOSTAL-02`, etc.) están sincronizados con:
- `Backend/mock-pms/data/inventory.json` - Inventario del mock
- `Backend/mock-pms/data/pms_mapping.json` - Mapeo de códigos a UUIDs

Esto permite que el sistema de sincronización funcione correctamente entre:
```
Mock PMS → pms-integration → Catalog → Search
```

## 🎯 UUIDs Deterministas

Los UUIDs se generan de forma determinista usando `uuid5(NAMESPACE_DNS, nombre)`:

```python
# Propiedad
uuid5(NAMESPACE_DNS, "catalog:propiedad:Cabaña Real Medellín 171")

# Categoría
uuid5(NAMESPACE_DNS, "categoria:Cabaña Real Medellín 171:Cabaña")
```

Esto garantiza que:
- Los mismos datos siempre generan los mismos UUIDs
- Se puede ejecutar el seed múltiples veces
- Los UUIDs coinciden entre diferentes entornos

## ⚠️ Notas Importantes

1. **El script limpia todas las tablas antes de insertar**. Úsalo solo en desarrollo.
2. El inventario se genera para los próximos 30 días desde la fecha actual.
3. Las imágenes son URLs de Unsplash y requieren conexión a internet.
4. Cada propiedad tiene exactamente 1 categoría (como especificado en los requisitos).

## 🧪 Verificación

Después de ejecutar el seed, puedes verificar con:

```sql
-- Contar propiedades
SELECT COUNT(*) FROM propiedades;  -- Debe ser 9

-- Contar categorías
SELECT COUNT(*) FROM categorias_habitacion;  -- Debe ser 9

-- Contar inventario
SELECT COUNT(*) FROM inventario;  -- Debe ser 270 (9 categorías × 30 días)

-- Ver códigos PMS
SELECT codigo_mapeo_pms, nombre_comercial FROM categorias_habitacion;
```

## 📝 Logs Esperados

Al ejecutar el script verás:

```
🚀 Iniciando seed de Catalog...
============================================================
🗑️  Limpiando datos existentes...
✅ Datos limpiados

💰 Insertando configuración de impuestos...
✅ 7 configuraciones de impuestos insertadas

🏊 Insertando amenidades...
✅ 9 amenidades insertadas

🏨 Insertando propiedades y categorías...
  ✅ 1. Cabaña Real Medellín 171 (Cartagena, Colombia)
  ✅ 2. Apartamento Premium Medellín 172 (Cartagena, Colombia)
  ...
  ✅ 9. Hotel Premium Ciudad de México 179 (Ciudad de México, México)

✅ 9 propiedades insertadas con categorías, inventario y temporadas

============================================================
🎉 SEED COMPLETADO EXITOSAMENTE
============================================================
📊 Resumen:
   • Países configurados: 7
   • Amenidades: 9
   • Propiedades: 9
   • Categorías: 9
   • Inventario: 270 registros (30 días por categoría)
   • Temporadas: 27 registros
   • Imágenes: 18 registros
============================================================
```
