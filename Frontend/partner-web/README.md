# UserWeb

This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 18.2.21.

## Development server

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The application will automatically reload if you change any of the source files.

## Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory.

## Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

## Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via a platform of your choice. To use this command, you need to first add a package that implements end-to-end testing capabilities.

## Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI Overview and Command Reference](https://angular.dev/tools/cli) page.

## Deployment

The application is deployed using AWS S3 and CloudFront. 

The deployment is fully automated via GitHub Actions (`frontend-cd.yml`). When code is pushed or merged into the `develop` or `main` branches, the pipeline automatically:
1. Installs dependencies and builds the project via `npm run build`.
2. Syncs the compiled output located in `dist/partner-web/browser/` to the designated S3 bucket using `aws s3 sync`.
3. Triggers a cache invalidation on the corresponding CloudFront distribution to serve the latest version immediately.

The Terraform infrastructure for these resources is defined in `Infraestructura/terraform/stacks/frontends`.
