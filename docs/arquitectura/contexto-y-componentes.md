# Contexto y componentes

## Actores externos

| Actor | Interacción principal |
| --- | --- |
| Usuario final | Busca hospedajes, reserva y consulta estado |
| Partner hotelero | Aprueba o rechaza reservas pendientes |
| Wompi | Procesa pagos y notifica cambios de transacción |
| PMS externo o simulado | Confirma reservas y reporta inventario |
| AWS | Aloja infraestructura remota |
| GitHub Actions | Ejecuta integración y despliegue continuo |

## Componentes internos

| Grupo | Componentes |
| --- | --- |
| Frontends | `user-web`, `partner-web`, `mobile-app` |
| Backend | `authservice`, `booking`, `catalog`, `notification`, `partner-management`, `payment`, `pms-integration`, `search`, `mock-pms` |
| Integración | RabbitMQ, Redis, bases de datos por servicio |
| Infraestructura | Docker Compose, Kubernetes, Terraform, workflows de CI/CD |

## Diagramas

- Contexto: [`diagramas/contexto.mmd`](./diagramas/contexto.mmd)
- Contenedores: [`diagramas/contenedores.mmd`](./diagramas/contenedores.mmd)

## Documentación relacionada

- Servicios: [`../microservicios/catalogo-servicios.md`](../microservicios/catalogo-servicios.md)
- APIs: [`../api/endpoints.md`](../api/endpoints.md)
