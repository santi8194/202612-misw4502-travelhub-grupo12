# Arquitectura y Decisiones - user-web

Este documento define la arquitectura oficial adoptada para el microservicio frontend **user-web** de TravelHub.

## 1. Diseño y Estilos: Tailwind CSS
- **Decisión:** Mantener Tailwind CSS sobre la integración de librerías como Angular Material.
- **Justificación:** El proyecto tiene una identidad visual propia estilo "Airbnb/Booking" desarrollada con CSS custom (`clamp`, custom properties) y Tailwind. Angular Material imponía un esquema visual muy rígido que rompería la estética actual. Tailwind nos ofrece flexibilidad y nos permite construir sin ataduras. 
- **Patrón a usar:** Clases de utilidad en el HTML (`field-input`, `mt-4`) y variables globales en el CSS base para mantener consistencia.

## 2. Aplicación Client-Side Only (Sin SSR)
- **Decisión:** Remover Server-Side Rendering (SSR) y utilizar Angular en modo puramente cliente (SPA).
- **Justificación:** En el contexto de un proyecto académico/educativo, SSR introduce fricciones innecesarias y complejidad (chequeos recurrentes del objeto de la ventana `window`, control de `localStorage` vs servidor, entornos NodeJS adicionales). Simplificando a una SPA aseguramos agilidad, iteración robusta y compilación libre de errores del motor V8 de SSR.

## 3. Estado Reactivo: Signals First ("Zoneless Ready")
- **Decisión:** Todo el componente debe administrar su estado interno mutando variables reactivas con la nueva tecnología de **Signals**.
- **Justificación:** Los signals informan proactivamente a Angular **dónde exactamente** fue actualizado un valor en el DOM, disparando detecciones de cambio ultrarrápidas y granulares. Esto descarta la necesidad continua de Zone.js.
- **Patrón a usar:** Variables del modelo con `signal()`, calculadas con `computed()`, e interfaces puras con `input()` y `output()` en lugar de los decoradores `@Input` y `@Output` clásicos.

## 4. Standalone Components
- **Decisión:** Ningún componente usará `NgModule`.
- **Justificación:** Es el estándar maduro de Angular (desde v14) para eliminar boilerplate. Permite crear proyectos sin indirecciones: las dependencias que el componente necesite (`FormsModule`, otros componentes), las importa directamente él mismo en el array `imports`.

## 5. Fetching y Entornos Flexibles
- **Decisión:** El `BookingService` (y futuros) estarán inyectados con el `HttpClient` de Angular y el `apiBaseUrl` se inyectará de los `environments/`.
- **Justificación:** No podemos acoplar IPs locales. Todo URL del Gateway/Backend debe ubicarse en `environments/environment.ts` para desarrollo, o `.prod.ts` para despliegues; los servicios solo apuntan hacia allá y exponen la transacción mediante flujos reactivos asíncronos bajo el contrato `Observable<T>`.

## 6. Arquitectura por Capas y Lazy Loading
La estructura que se acatara en este repositorio debe mantener 4 esquemas organizativos dentro de `src/app/`:
- `core/`: Servicios singletons que tocan el backend, Stores de estado (`localStorage`), Guards e Interceptores HTTP funcionales (`HttpInterceptorFn`). No aloja vistas.
- `models/`: Archivos `.interface.ts` puros que detallan las firmas de la API y formularios del sitio.
- `pages/`: Las pantallas completas del cliente (ej. `guests-page`). Cada página será importada asíncronamente en el router con el patrón `loadComponent: () => import(...)`.
- `shared/`: Widgets modulares reusables. (`header`, `footer`, `search-bar`).
