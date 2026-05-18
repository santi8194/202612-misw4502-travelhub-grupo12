# Catálogo de servicios y componentes

| Componente | Responsabilidad | Tipo | Documentación local |
| --- | --- | --- | --- |
| `authservice` | Autenticación y usuarios autenticados | Backend | [`README`](../../Backend/authservice/README.md) |
| `booking` | Reservas y orquestación de saga | Backend | [`README`](../../Backend/booking/README.md) |
| `catalog` | Propiedades, categorías, precios e inventario | Backend | [`README`](../../Backend/catalog/README.md) |
| `notification` | Notificaciones, correo y push | Backend | [`README`](../../Backend/notification/README.md) |
| `partner-management` | Aprobación manual de reservas | Backend | [`README`](../../Backend/partner-management/README.md) |
| `payment` | Checkout, tarjetas, webhook y eventos de pago | Backend | [`README`](../../Backend/payment/README.md) |
| `pms-integration` | Integración con PMS y normalización de inventario | Backend | [`README`](../../Backend/pms-integration/README.md) |
| `search` | Búsqueda y autocompletado de destinos | Backend | [`README`](../../Backend/search/README.md) |
| `mock-pms` | Simulación de PMS para pruebas | Backend auxiliar | [`README`](../../Backend/mock-pms/README.md) |
| `user-web` | Experiencia web de usuario final | Frontend | [`README`](../../Frontend/user-web/README.md) |
| `partner-web` | Experiencia web para partners | Frontend | [`README`](../../Frontend/partner-web/README.md) |
| `mobile-app` | Aplicación móvil Flutter | Frontend | [`README`](../../Frontend/mobile-app/README.md) |
| `shared-ui` | Espacio para componentes compartidos | Frontend auxiliar | [`README`](../../Frontend/shared-ui/README.md) |
| `Gateway` | Espacio reservado para gateway de API | Plataforma | [`README`](../../Gateway/README.md) |
| `Infraestructura` | Docker, Kubernetes, Terraform y scripts | Plataforma | [`README`](../../Infraestructura/README.md) |

## Relación entre componentes

- `booking` coordina el flujo distribuido de reserva.
- `payment`, `pms-integration`, `partner-management` y `notification` participan en la saga mediante eventos.
- `search` y `catalog` cubren consulta y disponibilidad.
- Los frontends consumen APIs backend y no contienen la lógica canónica de negocio.
