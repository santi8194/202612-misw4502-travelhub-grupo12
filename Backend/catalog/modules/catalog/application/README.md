# Application Services - Catalog Microservice

Este módulo contiene los servicios de aplicación que orquestan los casos de uso del dominio.

## Estructura

```
application/
├── __init__.py
├── services.py
└── commands/
    ├── __init__.py
    ├── create_property.py
    ├── register_category_housing.py
    └── update_inventory.py
```

## Componentes

### CatalogApplicationService

Servicio principal que orquesta todas las operaciones del catálogo. Utiliza comandos internos para ejecutar la lógica del negocio.

**Métodos disponibles:**

1. **`crear_propiedad()`** - Crea una nueva propiedad

```python
from uuid import UUID
from decimal import Decimal

resultado = service.crear_propiedad(
    id_propiedad=UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479"),
    nombre="Hotel Boutique Las Palmas",
    estrellas=4,
    ciudad="Cartagena",
    pais="Colombia",
    latitud=10.42,
    longitud=-75.54,
    porcentaje_impuesto=Decimal("19.00")
)
```

2. **`registrar_categoria_habitacion()`** - Registra una categoría de habitación

```python
resultado = service.registrar_categoria_habitacion(
    id_propiedad=UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479"),
    id_categoria="cat-deluxe-001",
    codigo_mapeo_pms="ROOM-DLX-01",
    nombre_comercial="Habitación Deluxe con Vista al Mar",
    descripcion="Amplia habitación de 40m2 con balcón privado...",
    monto_precio_base=Decimal("350000.00"),
    moneda_precio_base="COP",
    capacidad_pax=4,
    dias_anticipacion=5,
    porcentaje_penalidad=Decimal("50.0")
)
```

3. **`actualizar_inventario()`** - Actualiza el inventario de una categoría

```python
from datetime import date

resultado = service.actualizar_inventario(
    id_propiedad=UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479"),
    id_categoria="cat-deluxe-001",
    id_inventario="inv-2026-05-10-dlx",
    fecha=date(2026, 5, 10),
    cupos_totales=10,
    cupos_disponibles=3
)
```

4. **`obtener_propiedad()`** - Obtiene información de una propiedad

```python
propiedad = service.obtener_propiedad(UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479"))
```

5. **`obtener_disponibilidad()`** - Obtiene disponibilidad de una categoría en una fecha

```python
disponibilidad = service.obtener_disponibilidad(
    id_propiedad=UUID("f47ac10b-58cc-4372-a567-0e02b2c3d479"),
    id_categoria="cat-deluxe-001",
    fecha=date(2026, 5, 10)
)
```

## Patrones de Diseño

### Command Pattern

Cada comando encapsula un caso de uso específico:

- **CreateProperty**: Crea una propiedad y emite `PropiedadCreada`
- **RegisterCategoryHousing**: Registra una categoría y emite `CategoriaHabitacionRegistrada`
- **UpdateInventory**: Actualiza inventario y emite `InventarioActualizado`

### Event Publishing

Todos los comandos publican eventos de dominio al completarse:

```python
self.event_bus.publish_event(
    routing_key=evento.routing_key,
    event_type=evento.type,
    payload=evento.to_dict()
)
```

Los eventos se publican a través de RabbitMQ con las siguientes claves:

- `catalog.property.created` - Cuando se crea una propiedad
- `catalog.category.registered` - Cuando se registra una categoría
- `catalog.inventory.updated` - Cuando se actualiza el inventario

## Integración con Dependencias

### Repositorio

El repositorio debe implementar:

- `obtain(id_propiedad: UUID) -> Propiedad | None`
- `save(propiedad: Propiedad) -> None`

### Event Bus

El event bus debe implementar:

- `publish_event(routing_key: str, event_type: str, payload: dict) -> None`

## Ejemplo de Uso Completo

```python
from modules.catalog.application import CatalogApplicationService
from modules.catalog.infrastructure.repository import PropertyRepository
from modules.catalog.infrastructure.services.event_bus import EventBus
from uuid import UUID
from datetime import date
from decimal import Decimal

# Inicializar dependencias
repository = PropertyRepository()
event_bus = EventBus()

# Crear servicio
catalog_service = CatalogApplicationService(repository, event_bus)

# Crear propiedad
resultado_propiedad = catalog_service.crear_propiedad(
    id_propiedad=UUID("550e8400-e29b-41d4-a716-446655440000"),
    nombre="Hotel Boutique Las Palmeras",
    estrellas=5,
    ciudad="Santa Marta",
    pais="Colombia",
    latitud=11.25,
    longitud=-74.20,
    porcentaje_impuesto=Decimal("19.00")
)

# Registrar categoría
resultado_categoria = catalog_service.registrar_categoria_habitacion(
    id_propiedad=UUID("550e8400-e29b-41d4-a716-446655440000"),
    id_categoria="suite-junior",
    codigo_mapeo_pms="SUITE-JR",
    nombre_comercial="Suite Junior Deluxe",
    descripcion="Elegante suite con vistas al mar",
    monto_precio_base=Decimal("250000.00"),
    moneda_precio_base="COP",
    capacidad_pax=2,
    dias_anticipacion=7,
    porcentaje_penalidad=Decimal("25.0")
)

# Actualizar inventario
resultado_inventario = catalog_service.actualizar_inventario(
    id_propiedad=UUID("550e8400-e29b-41d4-a716-446655440000"),
    id_categoria="suite-junior",
    id_inventario="inv-2026-06-01",
    fecha=date(2026, 6, 1),
    cupos_totales=5,
    cupos_disponibles=2
)
```

## Manejo de Errores

Los servicios retornan diccionarios con información del resultado. En caso de error, incluyen un campo `error`:

```python
{
    "error": "Property not found",
    "id_propiedad": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Testing

Cada comando puede testearse aisladamente proporcionando mocks del repositorio y event bus:

```python
from unittest.mock import Mock

repository_mock = Mock()
event_bus_mock = Mock()

create_command = CreateProperty(repository_mock, event_bus_mock)
resultado = create_command.execute(...)
```
