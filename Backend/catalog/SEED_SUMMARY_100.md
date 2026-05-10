# 🌱 Resumen del Seed de Catalog - 100 Propiedades

## ✅ Archivos Creados/Actualizados

### 1. **`scripts/seed_full_catalog.py`** ⭐
Script principal que puebla la base de datos de Catalog desde cero con **100 propiedades**.

**Características:**
- Generación programática de propiedades con variación aleatoria
- Precios variados según tipo de propiedad ($60k - $900k)
- Distribución geográfica: 70% en Cartagena, Bogotá y Medellín
- Flag `--purge` para control de limpieza de datos
- UUIDs deterministas para consistencia

**Ejecución:**
```bash
# Con purga (recomendado para primera vez)
python3 scripts/seed_full_catalog.py --purge

# Sin purga (solo inserción)
python3 scripts/seed_full_catalog.py
```

### 2. **`scripts/generate_uuid_mapping_v2.py`**
Genera el mapeo completo de códigos PMS a UUIDs para las 100 propiedades.

**Ejecución:**
```bash
cd Backend/catalog/scripts
python3 generate_uuid_mapping_v2.py
```

**Salida:**
- `pms_uuid_mapping_full.json` - Mapeo completo en JSON
- Código Python de ejemplo para pms-integration
- Resumen por ciudad

### 3. **`scripts/README_SEED.md`**
Documentación completa actualizada con instrucciones para 100 propiedades.

## 📊 Distribución de Datos

### Por Ciudad (100 propiedades)

| Ciudad | Cantidad | País | Porcentaje | Coordenadas Base |
|--------|----------|------|------------|------------------|
| **Cartagena** | 40 | Colombia | 40% | 10.3910, -75.5346 |
| **Bogotá** | 20 | Colombia | 20% | 4.6097, -74.0817 |
| **Medellín** | 10 | Colombia | 10% | 6.2442, -75.5812 |
| **Cancún** | 10 | México | 10% | 21.1619, -86.8515 |
| **Ciudad de México** | 10 | México | 10% | 19.4326, -99.1332 |
| Cali | 4 | Colombia | 4% | 3.4516, -76.5320 |
| Santa Marta | 3 | Colombia | 3% | 11.2408, -74.1990 |
| Barranquilla | 3 | Colombia | 3% | 10.9685, -74.7813 |
| **TOTAL** | **100** | - | **100%** | - |

**Nota:** El 70% está concentrado en las 3 ciudades principales (Cartagena, Bogotá, Medellín) para facilitar búsquedas con resultados.

### Por Tipo de Propiedad

| Tipo | Rango de Precio | Capacidad | Estrellas | Cantidad Aprox. |
|------|-----------------|-----------|-----------|-----------------|
| **Hostal** | $60,000 - $150,000 | 2-4 pax | 2-3 ⭐ | ~17 |
| **Cabaña** | $120,000 - $300,000 | 4-8 pax | 3-4 ⭐ | ~17 |
| **Hotel** | $150,000 - $500,000 | 2-6 pax | 3-5 ⭐ | ~17 |
| **Finca** | $180,000 - $350,000 | 6-12 pax | 3-4 ⭐ | ~16 |
| **Apartamento** | $200,000 - $450,000 | 4-8 pax | 3-5 ⭐ | ~17 |
| **Resort** | $500,000 - $900,000 | 6-10 pax | 4-5 ⭐ | ~16 |

Los tipos se distribuyen de forma balanceada usando rotación.

### Datos Totales Generados

| Entidad | Cantidad | Descripción |
|---------|----------|-------------|
| Países configurados | 7 | Colombia, México, Perú, Ecuador, Chile, Argentina, USA |
| Amenidades | 9 | Piscina, WiFi, Spa, Cocina, Gym, Restaurante, AC, Lavandería, Chimenea |
| Propiedades | 100 | Hoteles, apartamentos, resorts, cabañas, hostales, fincas |
| Categorías | 100 | 1 categoría por propiedad |
| Inventario | 3,000 | 30 días × 100 categorías |
| Temporadas | 300 | 3 temporadas × 100 propiedades |
| Imágenes | 200 | 2 imágenes × 100 categorías |
| Reseñas | ~400 | 3-5 reseñas aleatorias por propiedad |

## 🎯 Códigos PMS

### Formato de Códigos

```
{PAIS}-{TIPO}-{NUMERO}

Ejemplos:
- COL-HOTE-001  (Hotel en Colombia, propiedad #1)
- COL-APAR-015  (Apartamento en Colombia, propiedad #15)
- MEX-RESO-085  (Resort en México, propiedad #85)
```

### Room Type Codes

Cada categoría tiene un código único: `RM001` a `RM100`

## 🔗 Integración con Mock PMS

### Archivos Relacionados

1. **`Backend/mock-pms/data/inventory_100.json`**
   - Se genera automáticamente desde `generate_inventory_mock.py`
   - Contiene las 100 propiedades perfectamente sincronizadas

2. **`Backend/mock-pms/data/pms_mapping.json`**
   - Mapeo de códigos PMS a UUIDs
   - Generado por `generate_uuid_mapping_v2.py`

### Flujo de Sincronización

```
Mock PMS (inventory.json)
    ↓ webhook/polling
pms-integration (usa pms_uuid_mapping_full.json)
    ↓ evento PMSInventoryUpdated
Catalog (actualiza inventario)
    ↓ evento InventarioActualizado
Search (actualiza índice)
```

## 🚀 Guía de Ejecución

### 1. Primera Vez (Con Purga)

```bash
cd Backend/catalog

# Purgar datos existentes e insertar seed
python3 scripts/seed_full_catalog.py --purge
```

**Salida esperada:**
```
🚀 Iniciando seed de Catalog...
============================================================
⚠️  MODO PURGA ACTIVADO - Se eliminarán todos los datos existentes
============================================================
🗑️  Limpiando datos existentes...
✅ Datos limpiados

💰 Insertando configuración de impuestos...
✅ 7 configuraciones de impuestos insertadas

🏊 Insertando amenidades...
✅ 9 amenidades insertadas

🏨 Insertando propiedades y categorías...
  ✅ 1. Hotel Premium Vista Mar 1 (Cartagena, Colombia)
  ✅ 2. Apartamento Boutique Centro Histórico 2 (Cartagena, Colombia)
  ...
  ✅ 100. Finca Royal Barranquilla 100 (Barranquilla, Colombia)

✅ 100 propiedades insertadas con categorías, inventario y temporadas

============================================================
🎉 SEED COMPLETADO EXITOSAMENTE
============================================================
📊 Resumen:
   • Países configurados: 7
   • Amenidades: 9
   • Propiedades: 100
   • Categorías: 100
   • Inventario: 3000 registros (30 días por categoría)
   • Temporadas: 300 registros
   • Imágenes: 200 registros
============================================================
```

### 2. Generar Mapeo de UUIDs

```bash
cd Backend/catalog/scripts
python3 generate_uuid_mapping_v2.py
```

Esto genera `pms_uuid_mapping_full.json` con el mapeo completo.

### 3. Verificar en Base de Datos

```sql
-- Contar propiedades por ciudad
SELECT ciudad, COUNT(*) as total
FROM propiedades
GROUP BY ciudad
ORDER BY total DESC;

-- Verificar códigos PMS
SELECT codigo_mapeo_pms, nombre_comercial, p.ciudad
FROM categorias_habitacion c
JOIN propiedades p ON c.id_propiedad = p.id_propiedad
ORDER BY codigo_mapeo_pms
LIMIT 20;

-- Verificar inventario
SELECT 
    c.codigo_mapeo_pms,
    COUNT(i.id_inventario) as dias_inventario,
    SUM(i.cupos_totales) as total_cupos
FROM inventario i
JOIN categorias_habitacion c ON i.id_categoria = c.id_categoria
GROUP BY c.codigo_mapeo_pms
ORDER BY c.codigo_mapeo_pms
LIMIT 10;

-- Resumen general
SELECT 
    'Propiedades' as entidad, COUNT(*) as total FROM propiedades
UNION ALL
SELECT 'Categorías', COUNT(*) FROM categorias_habitacion
UNION ALL
SELECT 'Inventario', COUNT(*) FROM inventario
UNION ALL
SELECT 'Temporadas', COUNT(*) FROM temporadas
UNION ALL
SELECT 'Imágenes', COUNT(*) FROM media;
```

## 🎨 Características de Generación

### Variación Aleatoria

El seed genera propiedades con variación aleatoria en:

1. **Nombres**: Combinación de tipo + adjetivo + descriptor
   - Adjetivos: Premium, Boutique, Imperial, Real, Express, Eco, Central, Deluxe, Grand, Royal
   - Descriptores: Vista Mar, Centro Histórico, Zona Rosa, Playa Dorada, Colonial, Moderno

2. **Precios**: Aleatorios dentro del rango del tipo de propiedad

3. **Capacidad**: Aleatoria dentro del rango del tipo

4. **Estrellas**: Aleatorias dentro del rango del tipo

5. **Amenidades**: 3-6 amenidades seleccionadas aleatoriamente

6. **Coordenadas**: Variación de ±0.05 grados para evitar duplicados exactos

7. **Imágenes**: 2 imágenes seleccionadas aleatoriamente de un pool de 11

### UUIDs Deterministas

Los UUIDs se generan usando `uuid5(NAMESPACE_DNS, nombre)`:

```python
# Propiedad
uuid5(NAMESPACE_DNS, "catalog:propiedad:Hotel Premium Vista Mar 1")

# Categoría
uuid5(NAMESPACE_DNS, "categoria:Hotel Premium Vista Mar 1:Hotel")
```

**Ventajas:**
- Mismos datos → mismos UUIDs
- Ejecutable múltiples veces
- Consistencia entre entornos
- Mapeo predecible para pms-integration

## 📝 Notas Importantes

### ⚠️ Modo Purga

- El flag `--purge` **elimina TODOS los datos** de las tablas
- Solo usar en desarrollo
- En producción, usar migraciones apropiadas

### 🔄 Re-ejecución

- Sin `--purge`: Puede causar errores de duplicados si los datos ya existen
- Con `--purge`: Limpia y vuelve a insertar todo

### 🌐 Imágenes

- URLs de Unsplash
- Requieren conexión a internet para visualizarse
- Son URLs públicas y estables

### 📅 Inventario

- Se genera para los próximos 30 días desde `date.today()`
- Cada día tiene cupos aleatorios entre 5-15
- Cupos disponibles = cupos totales inicialmente

## 🔧 Personalización

### Cambiar Cantidad de Propiedades

Edita la llamada en `seed_full_catalog.py`:

```python
# Generar las 100 propiedades
PROPERTIES_DATA = generate_properties(100)  # Cambiar a 50, 200, etc.
```

### Cambiar Distribución por Ciudad

Edita el diccionario `CITIES`:

```python
CITIES = {
    "Cartagena": {"estado": "Bolivar", "pais": "Colombia", "lat": 10.3910, "lng": -75.5346, "count": 50},  # Cambiar count
    # ...
}
```

### Agregar Nuevas Ciudades

```python
CITIES = {
    # ... ciudades existentes
    "Bucaramanga": {"estado": "Santander", "pais": "Colombia", "lat": 7.1193, "lng": -73.1227, "count": 5},
}
```

## ✅ Checklist de Verificación

Después de ejecutar el seed:

- [ ] Propiedades insertadas: 100
- [ ] Categorías insertadas: 100
- [ ] Inventario: 3,000 registros
- [ ] Temporadas: 300 registros
- [ ] Cartagena tiene 40 propiedades
- [ ] Bogotá tiene 20 propiedades
- [ ] Medellín tiene 10 propiedades
- [ ] Códigos PMS únicos (COL-*, MEX-*)
- [ ] UUIDs generados correctamente
- [ ] Imágenes asignadas (2 por categoría)
- [ ] Amenidades asignadas (3-6 por propiedad)

## 🎯 Próximos Pasos

1. ✅ **Seed ejecutado** - Base de datos poblada
2. ⏭️ **Actualizar Mock PMS** - Sincronizar inventory.json con muestra de propiedades
3. ⏭️ **Implementar pms-integration** - Usar mapeo de UUIDs generado
4. ⏭️ **Probar webhooks** - Verificar flujo Mock PMS → Catalog
5. ⏭️ **Sincronizar Search** - Eventos Catalog → Search
6. ⏭️ **Probar búsquedas** - Verificar que Cartagena retorna ~40 resultados

---

**Última actualización:** Mayo 2026  
**Versión del seed:** 2.0 (100 propiedades con generación programática)
