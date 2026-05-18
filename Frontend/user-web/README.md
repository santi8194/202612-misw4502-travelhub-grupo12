# User Web

## Propósito

Aplicación web para usuario final.

## Stack

- Angular
- Cypress
- Tailwind CSS

## Requisitos

- Node.js
- Dependencias de `package.json`

## Configuración

La configuración de entorno se mantiene dentro del proyecto frontend.

## Ejecución local

```bash
npm install
npm start
```

## Pruebas

```bash
npm test
npm run e2e
```

## Estructura relevante

- `src/`: aplicación Angular
- `cypress/`: pruebas E2E
- `docs/`: reglas funcionales específicas
- `front-rules/`: reglas de arquitectura y testing

## Dependencias con backend

Consume principalmente `authservice`, `search`, `catalog`, `booking` y `payment`.

## Documentación relacionada

- [`./docs/regla_estados_cruzada.md`](./docs/regla_estados_cruzada.md)
- [`./front-rules/actualizacion-arquitectura.md`](./front-rules/actualizacion-arquitectura.md)
- [`../../docs/api/endpoints.md`](../../docs/api/endpoints.md)
