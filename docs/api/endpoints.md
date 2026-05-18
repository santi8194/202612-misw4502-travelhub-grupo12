# Catálogo global de endpoints

| Servicio | Método | Ruta | Descripción |
| --- | --- | --- | --- |
| `authservice` | `POST` | `/login` | Autenticación |
| `authservice` | `POST` | `/register` | Registro |
| `authservice` | `GET` | `/me` | Usuario autenticado |
| `booking` | `POST` | `/reserva` | Crear reserva |
| `booking` | `POST` | `/reserva/{id}/formalizar` | Formalizar reserva |
| `booking` | `GET` | `/reserva/{id}` | Consultar reserva |
| `booking` | `GET` | `/reserva/usuario/{id_usuario}` | Reservas por usuario |
| `catalog` | `GET` | `/catalog/health` | Salud del servicio |
| `catalog` | `POST` | `/catalog/properties` | Crear propiedad |
| `catalog` | `GET` | `/catalog/properties` | Listar propiedades |
| `catalog` | `GET` | `/catalog/categories/{id_categoria}` | Consultar categoría |
| `search` | `GET` | `/health` | Salud del servicio |
| `search` | `GET` | `/api/v1/search` | Buscar hospedajes |
| `search` | `GET` | `/api/v1/search/destinations` | Autocompletar destinos |
| `payment` | `POST` | `/payments` | Crear checkout |
| `payment` | `GET` | `/payments/by-reserva/{id_reserva}` | Consultar pago por reserva |
| `payment` | `POST` | `/webhook` | Recibir webhook Wompi |
| `partner-management` | `POST` | `/partner/reserva/{id}/aprobar` | Aprobar reserva |
| `partner-management` | `POST` | `/partner/reserva/{id}/rechazar` | Rechazar reserva |
| `pms-integration` | `POST` | `/confirmar-reserva` | Confirmar reserva en PMS |
| `pms-integration` | `POST` | `/cancelar-reserva` | Cancelar reserva en PMS |
| `pms-integration` | `POST` | `/webhooks/inventory` | Recibir inventario PMS |
| `notification` | `GET` | `/health` | Salud del servicio |
| `notification` | `GET` | `/notificaciones` | Listar notificaciones |
| `notification` | `PATCH` | `/notificaciones/{id}/leida` | Marcar notificación leída |
| `notification` | `POST` | `/notifications/reservations/status-email` | Encolar correo de estado |
| `mock-pms` | `GET` | `/api/inventory/changes` | Consultar cambios de inventario simulados |
| `mock-pms` | `POST` | `/force-webhook` | Forzar webhook de inventario |

## Alcance

Este catálogo resume rutas principales para orientación técnica. Los detalles de payload, autenticación y casos de uso específicos deben consultarse en el README local o en la colección Postman del servicio correspondiente.
