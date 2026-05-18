# TravelHub

TravelHub es una plataforma hotelera distribuida con aplicaciones web y móvil, servicios backend independientes e infraestructura para ejecución local y despliegue en AWS.

## Arquitectura en una mirada

El sistema se organiza en frontends, microservicios backend, mensajería asíncrona y una capa de infraestructura común. Los flujos de reserva combinan APIs síncronas con eventos sobre RabbitMQ para coordinar pago, confirmación PMS, aprobación manual y notificaciones.

- Visión general: [`docs/arquitectura/vision-general.md`](./docs/arquitectura/vision-general.md)
- Componentes: [`docs/arquitectura/contexto-y-componentes.md`](./docs/arquitectura/contexto-y-componentes.md)
- Flujos críticos: [`docs/arquitectura/flujos-criticos.md`](./docs/arquitectura/flujos-criticos.md)

## Estructura del repositorio

| Ruta | Contenido |
| --- | --- |
| `Backend/` | Microservicios de negocio y servicios de integración |
| `Frontend/` | Aplicaciones web, móvil y componentes compartidos |
| `Infraestructura/` | Docker, Kubernetes, Terraform y scripts operativos |
| `Gateway/` | Espacio reservado para gateway de API |
| `docs/` | Documentación central y transversal del sistema |

## Requisitos previos

- Git
- Docker y Docker Compose
- Python para desarrollo de servicios backend
- Node.js para frontends web
- Flutter para la aplicación móvil
- Terraform y `kubectl` para operación de infraestructura remota

Los requisitos específicos de cada componente se documentan en su README local.

## Arranque rápido local

La ruta recomendada para levantar el stack completo en local es Docker Compose:

1. Revisar [`Infraestructura/docker/README.md`](./Infraestructura/docker/README.md).
2. Preparar el archivo de entorno local correspondiente.
3. Ejecutar el compose base con el overlay local.

Para alternativas de despliegue y uso de Minikube, consultar [`docs/operacion/entornos.md`](./docs/operacion/entornos.md).

## Documentación

| Necesidad | Documento |
| --- | --- |
| Empezar a leer el sistema | [`docs/README.md`](./docs/README.md) |
| Entender arquitectura | [`docs/arquitectura/vision-general.md`](./docs/arquitectura/vision-general.md) |
| Consultar servicios | [`docs/microservicios/catalogo-servicios.md`](./docs/microservicios/catalogo-servicios.md) |
| Consultar APIs | [`docs/api/endpoints.md`](./docs/api/endpoints.md) |
| Desplegar u operar | [`docs/operacion/README.md`](./docs/operacion/README.md) |
| Revisar decisiones | [`docs/decisiones/README.md`](./docs/decisiones/README.md) |

## Estado resumido de componentes

| Componente | Estado documental |
| --- | --- |
| Backend | Servicios activos con README normalizado; `notification`, `partner-management` y `mock-pms` completados en esta base |
| Frontend | `user-web`, `partner-web` y `mobile-app` documentados; `shared-ui` existe como esqueleto |
| Infraestructura | Documentación operativa existente reutilizada y enlazada desde `docs/` |
| Gateway | Carpeta reservada sin implementación activa |

## Flujos principales

- Búsqueda de hospedajes.
- Reserva y coordinación por saga.
- Pago con Wompi.
- Confirmación PMS y actualización de inventario.
- Notificación de confirmación o cancelación.

Los flujos se documentan en [`docs/arquitectura/flujos-criticos.md`](./docs/arquitectura/flujos-criticos.md).

## Puntos de entrada por perfil

| Perfil | Lectura recomendada |
| --- | --- |
| Nuevo integrante | `README.md` → `docs/README.md` → arquitectura |
| Backend | catálogo de servicios → README del servicio correspondiente |
| Frontend | README local del frontend → APIs y flujos críticos |
| DevOps | `Infraestructura/README.md` → `docs/operacion/README.md` |
