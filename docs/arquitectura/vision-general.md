# Visión general de arquitectura

## Propósito

TravelHub separa la experiencia de usuario, la lógica de negocio y la operación técnica en componentes independientes para permitir evolución por dominio y despliegue flexible.

## Estilo arquitectónico

- Frontends separados para usuario final, partner hotelero y aplicación móvil.
- Microservicios backend por capacidad de negocio.
- Comunicación síncrona por HTTP para consultas y comandos directos.
- Comunicación asíncrona por RabbitMQ para coordinación de procesos distribuidos.
- Persistencia desacoplada por servicio y configuración por entorno.

## Capacidades principales

| Capacidad | Componentes principales |
| --- | --- |
| Autenticación | `authservice` |
| Catálogo e inventario | `catalog`, `pms-integration` |
| Búsqueda | `search` |
| Reservas | `booking` |
| Pagos | `payment` |
| Gestión manual por partner | `partner-management` |
| Notificaciones | `notification` |

## Principios de organización

- Cada servicio mantiene su responsabilidad de dominio.
- La documentación operativa se mantiene cerca del código.
- Las reglas transversales se consolidan en documentación central.
- Los flujos distribuidos se hacen explícitos mediante contratos de eventos.

## Lecturas relacionadas

- Componentes y dependencias: [`contexto-y-componentes.md`](./contexto-y-componentes.md)
- Flujos críticos: [`flujos-criticos.md`](./flujos-criticos.md)
- Catálogo de servicios: [`../microservicios/catalogo-servicios.md`](../microservicios/catalogo-servicios.md)
