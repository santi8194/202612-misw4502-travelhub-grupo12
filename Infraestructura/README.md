# Infraestructura y tipos de despliegue

Este directorio contiene la infraestructura activa del proyecto y las rutas de despliegue disponibles hoy.

## Mapa rapido

| Tipo de despliegue | Uso principal | Entrada recomendada |
| --- | --- | --- |
| Docker Compose local con SQLite | Desarrollo local aislado, sin depender de AWS | [`docker/README.md`](./docker/README.md) |
| Docker Compose local con RDS | Desarrollo local contra las bases reales de dev | [`docker/README.md`](./docker/README.md) |
| Docker Compose local con ngrok | Pruebas locales de Wompi con webhook y retorno publico | [`scripts/run-local-ngrok.ps1`](./scripts/run-local-ngrok.ps1) |
| Minikube local | Pruebas del backend sobre Kubernetes local | [`scripts/run-minikube-stack.ps1`](./scripts/run-minikube-stack.ps1) |
| Minikube usando RDS de AWS | Kubernetes local con credenciales de RDS sincronizadas desde Secrets Manager | [`scripts/sync-minikube-rds-secrets.ps1`](./scripts/sync-minikube-rds-secrets.ps1) |
| AWS dev | Infraestructura y despliegue remoto por Terraform + workflows de GitHub Actions | [`terraform/`](./terraform/) y [`.github/workflows`](../.github/workflows) |

## 1. Docker Compose local

Los archivos activos son:

- [`docker/docker-compose.yml`](./docker/docker-compose.yml): contrato base reutilizado por CD.
- [`docker/docker-compose.local.yml`](./docker/docker-compose.local.yml): overlay local con builds desde fuente, frontends, RabbitMQ, Redis y ngrok.
- [`docker/docker-compose.local.orl.yml`](./docker/docker-compose.local.orl.yml): variante heredada no usada por scripts ni workflows activos.
- `docker/.env.local.sqlite.dev`: plantilla local ignorada con SQLite, no versionada.
- `docker/.env.local.rds.dev`: plantilla local ignorada con credenciales reales de RDS/dev.

Usa esta ruta cuando quieras levantar todo el stack en Docker, incluyendo `user-web`, `partner-web` y el gateway local en `http://localhost:5001`.

La guia operativa completa vive en [`docker/README.md`](./docker/README.md).

## 2. Docker Compose local con ngrok

Esta variante existe para probar integraciones que necesitan una URL publica, especialmente:

- webhook de Wompi;
- retorno del widget de Wompi hacia la vista de procesamiento de reserva.

Cada integrante debe configurar su propio token en su archivo local:

```env
NGROK_AUTHTOKEN=...
```

Luego puede ejecutar desde la raiz del repo:

```powershell
.\Infraestructura\scripts\run-local-ngrok.ps1
```

El script levanta el stack, obtiene la URL publica de ngrok y recompila `user-web` con esa URL para el retorno del widget.

## 3. Minikube local

Para desplegar el backend en Kubernetes local:

```powershell
.\Infraestructura\scripts\run-minikube-stack.ps1
```

Ese script:

- inicia Minikube;
- construye las imagenes locales del backend;
- aplica secretos, Postgres y manifiestos de `k8s/minikube`;
- deja el ingress accesible mediante port-forward local.

Despues del despliegue:

```powershell
kubectl -n ingress-nginx port-forward service/ingress-nginx-controller 8080:80
```

La URL local esperada es:

```text
http://127.0.0.1:8080
```

## 4. Minikube usando RDS de AWS

Si necesitas que Minikube use credenciales reales de RDS dev para `authservice`, `booking`, `catalog` y `search`, ejecuta:

```powershell
.\Infraestructura\scripts\sync-minikube-rds-secrets.ps1
```

Ese script lee Secrets Manager, actualiza los secrets de Kubernetes y reinicia los deployments respaldados por base de datos.

## 5. AWS dev

La infraestructura remota se define con Terraform en [`terraform/`](./terraform/):

- `container_registry`
- `database`
- `ec2`
- `eks`
- `frontends`
- `ingress`

Los workflows activos de GitHub Actions gestionan:

- CD de backend hacia EC2/EKS;
- despliegue de frontends a S3 + CloudFront;
- validaciones de Terraform.

Los manifiestos de backend para AWS viven en [`k8s/aws/`](./k8s/aws/).

Antes de desplegar a AWS, valida estos puntos:

- `pms-integration` no debe depender del `mock-pms` local en AWS. Configura un `MOCK_PMS_URL` real alcanzable desde EKS o deshabilita el polling remoto con `ENABLE_POLLING=false` hasta tener PMS real.
- Usa solo los manifiestos activos con nombres equivalentes a las carpetas de backend, por ejemplo `pms-integration-*` y `partner-management-*`. Los archivos antiguos `pmsintegration-*` y `partnermanagement-*` no forman parte del flujo actual de CD.
- Verifica que existan los secretos requeridos en Secrets Manager para cada servicio y que el secreto de `payment` incluya las claves de Wompi y RabbitMQ que exige el workflow.
- Mantén los archivos `.env.local.*` fuera del control de versiones cuando contengan credenciales reales. El `.gitignore` ya los excluye; no los fuerces al repositorio.
- Si el equipo quiere que un clon nuevo sea operable sin intercambio manual, agrega plantillas `.env.local.*.example` sanitizadas y versionadas antes de apoyarte en ellas en la documentacion.

## Notas de consistencia

- El README de Docker es la fuente operativa para Compose; este archivo funciona como indice de alto nivel.
- Los scripts locales activos quedan nombrados por responsabilidad:
  - `run-local-ngrok.ps1`
  - `run-minikube-stack.ps1`
  - `sync-minikube-rds-secrets.ps1`
- `docker-compose.local.orl.yml` no tiene consumidores detectados en el repositorio y no debe asumirse como parte del camino soportado.
