# Plan de Lanzamiento del Proyecto

Este documento describe el proceso de lanzamiento para los diversos componentes del proyecto Travel Hub. El proceso de lanzamiento está estandarizado para los componentes Mobile, Web y Backend, utilizando etiquetas (tags) de Git y GitHub Releases.

## 1. Estrategia de Versiones

Utilizamos Versionamiento Semántico (SemVer) con un sufijo de componente para identificar qué parte del proyecto se está lanzando.

| Componente            | Patrón de Etiqueta | Rama Objetivo |
| :-------------------- | :----------------- | :------------ |
| **Aplicación Móvil**  | `vX.Y.Z-mobile`    | `mobile-main` |
| **Frontends Web**     | `vX.Y.Z-web`       | `web-main`    |
| **Servicios Backend** | `vX.Y.Z-backend`   | `main`        |

_Ejemplos: `v1.0.0-mobile`, `v0.2.1-web`, `v1.1.0-backend`_

## 2. Disparadores de Lanzamiento

Los lanzamientos se disparan **manualmente** al crear y subir una etiqueta de Git que coincida con los patrones anteriores.

```bash
# Ejemplo: Lanzamiento del componente Web
git checkout web-main
git pull origin web-main
git tag v1.0.0-web
git push origin v1.0.0-web
```

## 3. Artefactos de Lanzamiento

Cada componente genera artefactos específicos que se adjuntan a la "Release" en GitHub.

### 3.1 Aplicación Móvil

- **Artefacto**: APK de Android firmado (`app-release.apk`).
- **Notas**: Notas de lanzamiento generadas automáticamente.

### 3.2 Frontends Web

- **Artefactos**: Archivos Zip para cada aplicación frontend:
  - `partner-web-build.zip`
  - `user-web-build.zip`
- **Notas**: Notas de lanzamiento generadas automáticamente.

### 3.3 Servicios Backend

- **Artefacto**: Referencias de imágenes Docker.
- **Notas**: La descripción del lanzamiento contendrá una lista de las imágenes Docker específicas y sus etiquetas (basadas en el SHA de Git) subidas al Elastic Container Registry (ECR) para cada microservicio.

## 4. Integración CI/CD

### 4.1 Móvil (`android_ci.yml`)

Cuando se sube una etiqueta `v*-mobile`:

1.  Construye la aplicación Flutter en modo release.
2.  Firma el APK utilizando los secretos del almacén de llaves (keystore).
3.  Crea una Release en GitHub y sube el APK.

### 4.2 Web (`frontend-cd.yml`)

Cuando se sube una etiqueta `v*-web`:

1.  Identifica qué aplicaciones web necesitan construcción.
2.  Construye las aplicaciones usando `npm run build`.
3.  Comprime (zip) los directorios `dist/` resultantes.
4.  Crea una Release en GitHub y sube los archivos `.zip`.

### 4.3 Backend (`backend-cd-base.yml` / `backend-cd-prod.yml`)

Cuando se sube una etiqueta `v*-backend`:

1.  Identifica todos los microservicios activos en el directorio `Backend/`.
2.  Construye las imágenes Docker para cada servicio.
3.  Sube las imágenes a ECR con la etiqueta de versión y la etiqueta `latest`.
4.  Crea una Release en GitHub con notas que documentan los URIs de ECR para cada servicio.
