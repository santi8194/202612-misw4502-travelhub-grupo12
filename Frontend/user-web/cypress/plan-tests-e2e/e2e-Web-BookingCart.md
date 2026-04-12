# Plan de Pruebas E2E: Carrito de Reserva (HU-Web-BookingCart)

Este documento detalla los escenarios de prueba automatizados con Cypress para validar el flujo de carrito de reserva en el portal web de TravelHub.

## 1. Información General
- **ID de Funcionalidad:** HU-Web-BookingCart
- **Componentes Involucrados:** `BookingCartPage`, `BookingCartForm`, `BookingCartSummary`, `BookingCartStepper`, `BookingService`
- **Herramienta:** Cypress + Mocks (Fixtures)

---

## 2. Escenarios de Prueba

### Escenario A: Carga del resumen y diligenciamiento del huésped
**Objetivo:** Validar que la página carga la reserva, calcula el resumen y permite completar el formulario del huésped.
- **Precondiciones:** Navegar a `/booking/:id_reserva` con respuestas mockeadas de reserva, categoría, catálogo y propiedad.
- **Pasos:**
    1. Abrir la URL del carrito de reserva.
    2. Esperar la carga del resumen y del timer de hold.
    3. Completar nombre, apellido, email, celular y solicitud detallada.
- **Resultado Esperado:**
    - Se muestra el stepper, el formulario y el resumen con propiedad, ubicación, fechas, huéspedes y total.
    - El botón de continuar permanece habilitado mientras el hold está activo.

### Escenario B: Creación exitosa del hold
**Objetivo:** Validar que el frontend envía la solicitud de hold con los datos esperados de la reserva.
- **Precondiciones:** La reserva fue cargada correctamente y el hold inicial sigue vigente.
- **Pasos:**
    1. Interceptar la creación de hold con un mock exitoso.
    2. Hacer clic en "Continuar con el pago".
- **Resultado Esperado:**
    - Se ejecuta `POST /api/reserva` con `id_categoria`, fechas y ocupación correctas.
    - No se muestra alerta de error y el timer continúa visible.

### Escenario C: Expiración del hold
**Objetivo:** Validar el comportamiento del carrito cuando el tiempo del hold expira.
- **Precondiciones:** La reserva fue cargada y el reloj del navegador está controlado por Cypress.
- **Pasos:**
    1. Interceptar el endpoint de expiración del backend.
    2. Avanzar el reloj 15 minutos.
- **Resultado Esperado:**
    - Se invoca la expiración de la reserva en backend.
    - Se visualiza el estado expirado del timer.
    - El botón de continuar queda deshabilitado y se muestra la alerta de hold expirado.

### Escenario D: Retorno al detalle de propiedad
**Objetivo:** Validar que la acción "Volver" reconstruye la navegación al detalle de la propiedad con los parámetros originales.
- **Precondiciones:** La reserva y la propiedad fueron cargadas exitosamente.
- **Pasos:**
    1. Interceptar la carga de categorías de la propiedad.
    2. Hacer clic en el enlace "Volver".
- **Resultado Esperado:**
    - Redirección a `/property/:property_id`.
    - La URL conserva `id_categoria`, `fecha_inicio`, `fecha_fin` y `huespedes`.

### Escenario E: Error al crear el hold
**Objetivo:** Validar el manejo de error cuando backend rechaza la creación del hold.
- **Precondiciones:** La reserva fue cargada correctamente.
- **Pasos:**
    1. Interceptar `POST /api/reserva` con respuesta `409`.
    2. Hacer clic en "Continuar con el pago".
- **Resultado Esperado:**
    - Se muestra la alerta "No hay cupos disponibles".
    - El botón vuelve a quedar habilitado para permitir un nuevo intento.

---

## 3. Configuración Técnica de Soporte
- **Mocks:**
    - `booking-cart-booking.json`: Datos base de la reserva.
    - `booking-cart-catalog.json`: Payload del catálogo por categoría.
    - `booking-cart-category.json`: Detalle de la categoría reservada.
    - `booking-cart-property.json`: Detalle de la propiedad.
    - `booking-cart-property-categories.json`: Categorías requeridas al regresar al detalle.
    - `booking-cart-create-hold-success.json`: Respuesta exitosa al crear hold.
    - `booking-cart-expire-success.json`: Respuesta de expiración.
    - `booking-cart-create-hold-error.json`: Respuesta de error por falta de cupos.