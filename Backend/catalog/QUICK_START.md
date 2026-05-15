# 🚀 Quick Start - Seed de Catalog (100 Propiedades)

## ⚡ Inicio Rápido

### 1️⃣ Ejecutar el Seed

```bash
cd Backend/catalog

# Primera vez o para limpiar datos existentes
python3 scripts/seed_full_catalog.py --purge
```

**Tiempo estimado:** 30-60 segundos

### 2️⃣ Verificar el Seed

```bash
python3 scripts/verify_seed.py
```

### 3️⃣ Generar Mapeo de UUIDs (Opcional)

```bash
cd scripts
python3 generate_uuid_mapping_v2.py
```

Esto genera `pms_uuid_mapping_full.json` con el mapeo completo para pms-integration.

---

## 📊 ¿Qué se Crea?

| Entidad | Cantidad | Descripción |
|---------|----------|-------------|
| 🏨 **Propiedades** | **100** | Hoteles, apartamentos, resorts, cabañas, hostales, fincas |
| 🏷️ Categorías | 100 | 1 categoría por propiedad |
| 📦 Inventario | 3,000 | 30 días × 100 categorías |
| 📅 Temporadas | 300 | 3 temporadas × 100 propiedades |
| 🎨 Imágenes | 200 | 2 imágenes × 100 categorías |
| 🏊 Amenidades | 9 | Piscina, WiFi, Spa, etc. |
| 💰 Impuestos | 7 | Configuración por país |

---

## 🌍 Distribución Geográfica

```
Cartagena (Colombia)    ████████████████████████████████████████  40 (40%)
Bogotá (Colombia)       ████████████████████                      20 (20%)
Medellín (Colombia)     ██████████                                10 (10%)
Cancún (México)         ██████████                                10 (10%)
CDMX (México)           ██████████                                10 (10%)
Otras ciudades          ██████                                    10 (10%)
```

**70% concentrado en Cartagena, Bogotá y Medellín** para facilitar búsquedas con resultados.

---

## 💵 Rangos de Precios

| Tipo | Precio | Estrellas |
|------|--------|-----------|
| 🏠 Hostal | $60k - $150k | ⭐⭐ |
| 🏡 Cabaña | $120k - $300k | ⭐⭐⭐ |
| 🏨 Hotel | $150k - $500k | ⭐⭐⭐⭐ |
| 🌾 Finca | $180k - $350k | ⭐⭐⭐ |
| 🏢 Apartamento | $200k - $450k | ⭐⭐⭐⭐ |
| 🏖️ Resort | $500k - $900k | ⭐⭐⭐⭐⭐ |

---

## 🔑 Códigos PMS

- **Colombia:** `COL-HOTE-001` a `COL-FINC-080`
- **México:** `MEX-HOTE-081` a `MEX-RESO-100`
- **Room Codes:** `RM001` a `RM100`

Cada código mapea a un UUID determinista único.

---

## ✅ Verificación Rápida

```sql
-- Contar propiedades por ciudad
SELECT ciudad, COUNT(*) as total
FROM propiedades
GROUP BY ciudad
ORDER BY total DESC;

-- Verificar inventario
SELECT COUNT(*) FROM inventario;  -- Debe ser 3000

-- Ver códigos PMS
SELECT codigo_mapeo_pms, nombre_comercial 
FROM categorias_habitacion 
ORDER BY codigo_mapeo_pms 
LIMIT 10;
```

---

## 🔧 Opciones del Seed

### Con Purga (Recomendado)
```bash
python3 scripts/seed_full_catalog.py --purge
```
✅ Limpia todos los datos existentes  
✅ Inserta datos frescos  
⚠️ Solo usar en desarrollo

### Sin Purga
```bash
python3 scripts/seed_full_catalog.py
```
✅ Solo inserta datos  
⚠️ Puede causar errores de duplicados

### Ver Ayuda
```bash
python3 scripts/seed_full_catalog.py --help
```

---

## 📁 Archivos Importantes

```
Backend/catalog/
├── scripts/
│   ├── seed_full_catalog.py          ⭐ Script principal
│   ├── generate_uuid_mapping_v2.py   🔑 Generador de mapeo
│   ├── verify_seed.py                ✅ Verificación
│   └── README_SEED.md                📖 Documentación completa
├── SEED_SUMMARY_100.md               📊 Resumen detallado
├── QUICK_START.md                    🚀 Esta guía
└── pms_uuid_mapping_full.json        🗺️ Mapeo generado
```

---

## 🎯 Próximos Pasos

1. ✅ **Seed ejecutado** → Base de datos poblada con 100 propiedades
2. ⏭️ **Actualizar Mock PMS** → Usar `inventory_100.json`
3. ⏭️ **Implementar pms-integration** → Usar mapeo de UUIDs
4. ⏭️ **Probar búsquedas** → Buscar en Cartagena debe retornar ~40 resultados

---

## 🆘 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'sqlalchemy'"
```bash
# Instalar dependencias
pip install -r requirements.txt
```

### Error: "could not connect to server"
```bash
# Verificar que PostgreSQL esté corriendo
docker ps | grep postgres

# O iniciar el contenedor
docker-compose up -d catalog-db
```

### Error: "relation does not exist"
```bash
# Ejecutar migraciones primero
alembic upgrade head
```

---

## 📞 Contacto y Documentación

- **Documentación completa:** `scripts/README_SEED.md`
- **Resumen detallado:** `SEED_SUMMARY_100.md`
- **Verificación:** `python3 scripts/verify_seed.py`

---

**Última actualización:** Mayo 2026  
**Versión:** 2.0 (100 propiedades con generación programática)
