# Plan de Pruebas E2E: Búsqueda y Descubrimiento (HU-Web-01)

Este documento detalla los escenarios de prueba automatizados con Cypress para validar el flujo de búsqueda de hospedaje en el portal web de TravelHub.

## 1. Información General
- **ID de Funcionalidad:** HU-Web-01
- **Componentes Involucrados:** `HeroSearchForm`, `SearchResultsPage`, `CompactSearchBar`, `SearchService`
- **Herramienta:** Cypress + Mocks (Fixtures)

---

## 2. Escenarios de Prueba

### Escenario A: Flujo Exitoso de Búsqueda (Happy Path)
**Objetivo:** Validar que un usuario puede buscar hospedaje seleccionando un destino sugerido, fechas y cantidad de huéspedes.
- **Precondiciones:** La aplicación está en la página principal (`/`).
- **Pasos:**
    1. Ingresar "Bor" en el campo de ubicación.
    2. Esperar y seleccionar la sugerencia "Bordeaux, Nouvelle-Aquitaine, Francia".
    3. Seleccionar una fecha de ingreso (mañana) y salida (mañana + 3 días).
    4. Incrementar la cantidad de huéspedes a 2.
    5. Hacer clic en el botón de búsqueda.
- **Resultado Esperado:** 
    - Redirección a `/resultados` con los parámetros correctos.
    - El título de resultados muestra "Stays in Bordeaux".
    - Se visualizan exactamente 2 cards de hospedaje (según mock).

### Escenario B: Búsqueda sin Resultados
**Objetivo:** Validar el comportamiento del sistema cuando el backend no retorna hospedajes disponibles.
- **Precondiciones:** La aplicación está en la página principal.
- **Pasos:**
    1. Realizar una búsqueda completa (Ubicación, Fechas, Huéspedes).
    2. Simular respuesta del servidor con 0 resultados.
- **Resultado Esperado:** 
    - Visualización del componente "Empty State" con el mensaje "No se encontraron hospedajes".
    - El botón de retorno redirige de nuevo a la página principal.

### Escenario C: Validaciones de Front-End (Caja Negra)
**Objetivo:** Validar que el formulario previene búsquedas incompletas y respeta las reglas de negocio.
- **Precondiciones:** La aplicación está en la página principal.
- **Pasos:**
    1. Intentar hacer clic en buscar sin ingresar ubicación.
    2. Intentar disminuir la cantidad de huéspedes por debajo de 1.
- **Resultado Esperado:** 
    - Aparición de tooltip de error visual indicando "Introduce un destino".
    - El contador de huéspedes no debe descender de 1.

### Escenario D: Verificación de Buscador Compacto y Retorno
**Objetivo:** Validar que la página de resultados refleja los datos de búsqueda en la barra superior y permite la edición.
- **Precondiciones:** Navegar directamente a una URL de resultados con parámetros (ej. `ciudad=Cancun&huespedes=4`).
- **Pasos:**
    1. Verificar que la barra compacta superior muestre "Cancun" y "4 huéspedes".
    2. Hacer clic sobre la barra compacta.
- **Resultado Esperado:** 
    - Redirección a la página principal.
    - El formulario principal debe estar precargado con los datos "Cancun" y "4".

---

## 3. Configuración Técnica de Soporte
- **Video:** Habilitado en cada ejecución (`video: true`).
- **Reportes:** Generación automática de archivos JUnit XML en `cypress/results/`.
- **Mocks:**
    - `search-destinations.json`: Simula autocompletado.
    - `search-results.json`: Simula lista de hoteles encontrados.
