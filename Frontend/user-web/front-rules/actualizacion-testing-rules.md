# Reglas de Pruebas Automáticas (Testing Rules)

Para garantizar la estabilidad del código de las vistas, componentes y estados visuales integrados tras la migración, todo el trabajo en `user-web` demanda pruebas unitarias rigurosas y blindadas contra los estilos CSS.

## 1. Cobertura de Pruebas (Coverage Mínimo `> 80%`)
- **Regla:** Todo componente UI (pantallas, templates listos) y lógicas aisladas del `core/` intervinientes (servicios de capa media, stores localStorage reactivos) **deben alcanzar, de piso estricto, un 80% de cobertura** de pruebas unitarias (`Line` y `Branch`).  

## 2. Invocación Virtual sin Módulo Clásico
- **Regla:** Al programar contra un componente Standalone se extingue la invocación sobre declaraciones masivas del entorno de `TestBed`.
- **Implementación:** Solo debes registrar la propia clase del componente sobre `imports` en el `configureTestingModule`.  No más dependencias ajenas en cascada. 

## 3. Selectores de Vista (`data-testid` obligatorio)
- **Regla:** Absolutamente prohibido seleccionar en una aserción contra el DOM utilizando reglas dependientes a clases de Tailwind o CSS (Ej: `fixture.debugElement.query(By.css('.btn-primary'))`). Los temas gráficos siempre rotan.
- **Implementación:** Colar en el componente objetivo a chequear el identificador universal para Cypress/Jasmine:
  ```html
  <button data-testid="continue-payment-btn">Continuar</button>
  ```
  ```typescript
  const btn = fixture.nativeElement.querySelector('[data-testid="continue-payment-btn"]');
  ```

## 4. Tests Unitarios a Peticiones HTTP
- **Regla:** Un servicio NO emitirá llamadas lógicas nunca con `HttpClientTestingModule`. Esta plataforma de Angular 13 ya se deprecó.
- **Implementación:** Se invocan proveedores `provideHttpClient()` en conjunto de la simulación de Mock HTTP funcional del interceptor moderno `provideHttpClientTesting()` provenientes del modulo `/testing`. 
- Se aserta sobre `HttpTestingController` usando sus apis modernas nativas asadas sobre la red, capturando peticiones vivas al server simuladas bajo la validación del mock prearmado.
