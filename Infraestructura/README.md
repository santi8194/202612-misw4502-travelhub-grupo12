# Infraestructura

## Propósito

Conjunto de artefactos para desarrollo local, despliegue en Kubernetes y aprovisionamiento remoto.

## Alcance

- Docker Compose local
- Minikube
- Kubernetes sobre AWS
- Terraform
- Scripts operativos

## Prerrequisitos

- Docker y Docker Compose
- `kubectl`
- Terraform
- Credenciales AWS cuando aplique

## Rutas de despliegue soportadas

| Ruta | Uso |
| --- | --- |
| Docker local con SQLite | Desarrollo aislado |
| Docker local con RDS | Desarrollo local contra dev remoto |
| Docker local con ngrok | Pruebas de Wompi |
| Minikube local | Validación del backend en Kubernetes |
| AWS dev/prod | Despliegue remoto |

## Configuración

- Docker local: `docker/`
- Kubernetes: `k8s/`
- Terraform: `terraform/`
- Scripts: `scripts/`

## Comandos operativos

Consultar las guías específicas:

- [`docker/README.md`](./docker/README.md)
- [`terraform/REMOTE_STATE_DEV.md`](./terraform/REMOTE_STATE_DEV.md)

## Dependencias

- Docker
- Kubernetes
- AWS
- GitHub Actions

## Documentación relacionada

- [`../docs/operacion/README.md`](../docs/operacion/README.md)
- [`../docs/arquitectura/despliegue-y-entornos.md`](../docs/arquitectura/despliegue-y-entornos.md)
