# Reglas del Sistema (Coding Rules)

Para garantizar consistencia a lo largo de TravelHub `user-web`, se exige este estándar de codificación. Todo PR o Commit que no respete total o parcialmente estas normativas estará sujeto a refactorización obligatoria.

## 1. Tipado Estricto: Prohibido `any`
- **Regla:** Ningún modelo, respuesta HTTP, formulario, o variable local debe estar declarada bajo el tipo de escape abstracto `any`.
- **Implementación:** Al declarar objetos de negocio, construir el esqueleto como una `interface` (EJ: `GuestForm` en `models/guest.interface.ts`). El tipo `class` no debe usarse para el dominio (para no cargar el `JS` por instanciación al transpilar).
- **Fallback:** Para datos misteriosos de un backend no documentado, usar `unknown` e ingeniar un chequeo seguro con un "Type Guard".

## 2. Inyección Funcional de Dependencias
- **Regla:** Todo servicio o componente se inyecta con la función nativa de Angular `inject()`.
- **Ejemplo Correcto:** `private readonly bookingService = inject(BookingService);`
- **Por qué evitar el constructor:** `inject()` remueve necesidad de importar dependencias repetidas vez tras vez a lo largo de componentes heredados.

## 3. Control de Bloques de Vista Analíticos Modernos
- **Regla:** Quedan obsoletas las directivas estructurales ligadas en el template (`*ngIf`, `*ngFor`).
- **Implementación:** El `HTML` alojará las instrucciones bloque (`@if() {} @else {}` y el `@for()` con clave `track` imperativa para máxima velocidad DOM).

## 4. Consumo Reactivo, Sin Fugas
- **Regla:** Limitar al máximo las llamadas con el `.subscribe()`. 
- **Implementación:** Se favorecerá siempre que sea factible mapear el observable a una Señal angular nativa mediante la herramienta `toSignal()` permitiendo renderizar síncronamente hacia el `@html`, dejando que interaccione automáticamente e impidiendo fugas de memoria, por sobre un seteo manual sobre un `subscribe` interno y variables de clase tradicionales. 

## 5. Intercepción Centralizada y Global
- **Regla:** Se manejará la gestión de errores transaccionales en un Interceptor global.
- **Implementación:** Existe un `error.interceptor.ts`. Cualquier validación genérica 401, 500 o fallos de red (`status 0 | timeout`) se atienden allí antes de pasarle localmente el objeto fallido al servicio que originó la pre-reserva HTTP. Su registro lo inyecta obligatoriamente `withInterceptors([])`.

## 6. Nomenclatura Angular 20
- Componentes y modales perderán en el arbol local el apellido verbose: `header.component.ts`. 
- Nos mudamos al modo sintético de nueva generación: `header.ts`.
