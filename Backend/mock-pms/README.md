# Mock PMS

## Propósito

Servicio auxiliar para simular un proveedor PMS durante desarrollo y pruebas.

## Responsabilidad dentro del sistema

Expone cambios de inventario simulados y permite forzar webhooks hacia la integración PMS.

## Dependencias

- Datos locales en `data/`
- Consumidores externos de sus endpoints de prueba

## Requisitos

- Python
- Dependencias de `requirements.txt`

## Configuración

La configuración es mínima y se mantiene local al servicio.

## Ejecución local

```bash
pip install -r requirements.txt
python main.py
```

## Pruebas

```bash
pytest
```

## Endpoints principales

- `GET /health`
- `GET /api/inventory/changes`
- `POST /force-webhook`

## Eventos publicados y consumidos

No publica eventos directamente; actúa como fuente simulada para `pms-integration`.

## Persistencia

Usa archivos de datos locales para simular cambios de inventario.

## Documentación relacionada

- [`../../docs/arquitectura/flujos-criticos.md`](../../docs/arquitectura/flujos-criticos.md)
- [`../../docs/api/endpoints.md`](../../docs/api/endpoints.md)
