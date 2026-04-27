# Plan de Pruebas E2E: Detalle de Habitación (HU-Web-RoomDetail)

Este documento detalla los escenarios de prueba automatizados con Cypress para validar la vista de detalle de habitación (`RoomDetailPage`) en el portal web de TravelHub. Esta vista muestra la información específica de una categoría (habitación), permitiendo al usuario visualizar galerías, amenidades, reseñas y realizar la reserva.

## 1. Información General
- **ID de Funcionalidad:** HU-Web-RoomDetail
- **Ruta de la vista:** `/category/:category_id`
- **Componentes Involucrados:** `RoomDetailPage`, `CatalogService`, `BookingService`
- **Herramienta:** Cypress + Mocks (Fixtures)

---

## 2. Escenarios de Prueba

### Escenario A: Renderizado y Visualización de Información (Happy Path)
**Objetivo:** Validar que la página carga y muestra correctamente todos los elementos de la habitación a partir de los datos del backend.
- **Precondiciones:** El usuario navega a `/category/CAT-123`.
- **Pasos:**
    1. Interceptar `GET **/catalog/categories/CAT-123/view-detail` y responder con el mock `room-detail-success.json`.
    2. Esperar a que desaparezca el estado de carga (`[data-testid="room-detail-loading"]`).
    3. Validar el título de la habitación (`[data-testid="room-detail-title"]`).
    4. Validar que la cuadrícula de imágenes cargue las fotos de la galería (`[data-testid="room-image-grid"]`).
    5. Validar la renderización de amenidades (`[data-testid="room-amenities"]`).
    6. Hacer clic en "Ver más" de la descripción (`[data-testid="room-description"] button`) y verificar que se expanda el texto.
    7. Validar que la sección de reseñas y políticas se muestran correctamente.
- **Resultado Esperado:** La interfaz refleja fielmente la respuesta del backend, y la interacción del acordeón de descripción funciona.

### Escenario B: Inicialización con Parámetros URL (Deep Linking)
**Objetivo:** Validar que al ingresar desde una búsqueda previa (URL con query params), el formulario de reserva se pre-cargue y calcule el precio inmediatamente.
- **Precondiciones:** El usuario navega a `/category/CAT-123?fecha_inicio=2026-10-10&fecha_fin=2026-10-15&huespedes=2`.
- **Pasos:**
    1. Interceptar y responder con el mock exitoso.
    2. Verificar los inputs del "Booking Box".
- **Resultado Esperado:**
    - Input Entrada muestra `2026-10-10`.
    - Input Salida muestra `2026-10-15`.
    - Input Huéspedes muestra `2`.
    - La sección de desglose de precio (`[data-testid="room-price-breakdown"]`) es visible, mostrando el cálculo correcto (Ej: 5 noches x Precio Base + Tarifa de Servicio).
    - El botón "Reservar" está habilitado.

### Escenario C: Validaciones Dinámicas del Formulario de Reserva
**Objetivo:** Asegurar que el usuario no pueda reservar fechas inválidas o que rompan las reglas del negocio.
- **Precondiciones:** El usuario se encuentra en la vista sin fechas seleccionadas.
- **Pasos:**
    1. Intentar hacer clic en el botón "Reservar" (debe estar deshabilitado).
    2. Seleccionar una fecha de entrada en el pasado (El navegador lo restringe vía `min`, pero validamos el input).
    3. Seleccionar una fecha de salida igual o anterior a la fecha de entrada.
- **Resultado Esperado:** 
    - El botón de reserva (`[data-testid="room-reservar-btn"]`) debe permanecer deshabilitado a menos que haya entrada válida, salida > entrada y huéspedes > 0.
    - El desglose de precios debe ocultarse cuando las fechas son inválidas.

### Escenario D: Flujo de Creación de Reserva Exitoso
**Objetivo:** Validar la comunicación con el `BookingService` al iniciar una reserva y la redirección.
- **Precondiciones:** Parámetros de reserva válidos diligenciados.
- **Pasos:**
    1. Interceptar `POST **/api/reserva` y responder con el mock `room-detail-booking-success.json` (Devuelve `id_reserva: "RES-999"`).
    2. Hacer clic en "Reservar".
- **Resultado Esperado:**
    - El botón cambia temporalmente al estado "Reservando...".
    - El usuario es redirigido a la vista del carrito `/booking/RES-999`.

### Escenario E: Manejo de Errores de Reserva (Backend Error)
**Objetivo:** Asegurar que los fallos del backend al intentar reservar (ej. sin disponibilidad) se notifiquen al usuario.
- **Precondiciones:** Parámetros de reserva válidos diligenciados.
- **Pasos:**
    1. Interceptar `POST **/api/reserva` y simular un status `409 Conflict` por falta de inventario (fixture: `room-detail-booking-error.json`).
    2. Hacer clic en "Reservar".
- **Resultado Esperado:**
    - El proceso se detiene.
    - Aparece el mensaje de error del backend en la vista de reserva (`[data-testid="room-booking-error"]`).
    - El usuario no es redirigido.

### Escenario F: Estado de Error (Error API Detail)
**Objetivo:** Validar la vista de error cuando el detalle de la habitación falla al cargar.
- **Precondiciones:** Navegar a `/category/CAT-ERROR`.
- **Pasos:**
    1. Interceptar `GET **/catalog/categories/*/view-detail` simulando un error `500 Server Error`.
- **Resultado Esperado:**
    - Se oculta el loading skeleton.
    - Se muestra la tarjeta de error (`[data-testid="room-detail-error"]`) con un mensaje adecuado.
    - Se muestra el enlace para "Volver a resultados".

---

## 3. Fixtures (Mocks) Requeridos
Se deben crear los siguientes archivos en `cypress/fixtures/`:
1. `room-detail-success.json`: Respuesta exitosa con galería, amenidades completas, tarifas y reseñas.
2. `room-detail-booking-success.json`: Respuesta POST `/api/reserva` exitosa con `id_reserva`.
3. `room-detail-booking-error.json`: Respuesta POST `/api/reserva` con conflicto de disponibilidad o tarifa.
