# UserWeb

This project was generated using [Angular CLI](https://github.com/angular/angular-cli) version 20.3.22.

## Development server

To start a local development server, run:

```bash
ng serve
```

Once the server is running, open your browser and navigate to `http://localhost:4200/`. The application will automatically reload whenever you modify any of the source files.

## Code scaffolding

Angular CLI includes powerful code scaffolding tools. To generate a new component, run:

```bash
ng generate component component-name
```

For a complete list of available schematics (such as `components`, `directives`, or `pipes`), run:

```bash
ng generate --help
```

## Building

To build the project run:

```bash
ng build
```

This will compile your project and store the build artifacts in the `dist/` directory. By default, the production build optimizes your application for performance and speed.

## Running unit tests

To execute unit tests with the [Karma](https://karma-runner.github.io) test runner, use the following command:

```bash
ng test
```

## Running end-to-end tests

For end-to-end (e2e) testing, run:

```bash
ng e2e
```

Angular CLI does not come with an end-to-end testing framework by default. You can choose one that suits your needs.

## Additional Resources

For more information on using the Angular CLI, including detailed command references, visit the [Angular CLI Overview and Command Reference](https://angular.dev/tools/cli) page.

## Deployment

The application is deployed using AWS S3 and CloudFront. 

The deployment is fully automated via GitHub Actions (`frontend-cd.yml`). When code is pushed or merged into the `develop` or `main` branches, the pipeline automatically:
1. Installs dependencies and builds the project via `npm run build`.
2. Syncs the compiled output located in `dist/user-web/browser/` to the designated S3 bucket using `aws s3 sync`.
3. Triggers a cache invalidation on the corresponding CloudFront distribution to serve the latest version immediately.

The Terraform infrastructure for these resources is defined in `Infraestructura/terraform/stacks/frontends`.

---

## 🏛 Arquitectura y Reglas del Proyecto (TravelHub)

Este proyecto ha sido migrado y adaptado para correr en un entorno estricto de **Angular 20**, priorizando una arquitectura **Client-Side Only**, orientada a Signals reactivos y desarrollo Standalone (libre de NgModules).

Todos los desarrolladores deben revisar la normativa documentada de forma obligatoria antes de estructurar o codificar nuevos flujos, componentes y vistas en él:

1. **[Decisiones de Arquitectura](./front-rules/actualizacion-arquitectura.md)**: Explicación de los cimientos (Tailwind vs Material CSS, Estructura de componentes y dependencias HTTP).
2. **[Reglas de Desarrollo](./front-rules/actualizacion-rules.md)**: Convenciones estandarizadas para el día a día, control flow sin asteriscos, tipado inamovible (Prohibición estricta de `any`) e inyección moderna con `inject()`.
3. **[Políticas de Pruebas / Testing](./front-rules/actualizacion-testing-rules.md)**: Cómo sostener una estructura de aserción agnóstica a modas (Testing mediante `data-testid`), el uso de simuladores modernos contra la app y cuota mínima (`> 80% coverage`).
