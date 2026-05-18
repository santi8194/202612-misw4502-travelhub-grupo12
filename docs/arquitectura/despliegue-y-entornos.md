# Despliegue y entornos

## Entornos soportados

| Entorno | Uso |
| --- | --- |
| Docker local con SQLite | Desarrollo aislado |
| Docker local con RDS | Desarrollo local contra datos remotos de dev |
| Docker local con ngrok | Pruebas de callbacks públicos de Wompi |
| Minikube local | Validación del backend sobre Kubernetes |
| AWS dev/prod | Despliegue remoto con Terraform y GitHub Actions |

## Vista de despliegue

La topología de despliegue se resume en [`diagramas/despliegue.mmd`](./diagramas/despliegue.mmd).

## Fuentes de detalle

- Mapa operativo: [`../../Infraestructura/README.md`](../../Infraestructura/README.md)
- Docker local: [`../../Infraestructura/docker/README.md`](../../Infraestructura/docker/README.md)
- Remote state Terraform: [`../../Infraestructura/terraform/REMOTE_STATE_DEV.md`](../../Infraestructura/terraform/REMOTE_STATE_DEV.md)
- Operación central: [`../operacion/README.md`](../operacion/README.md)
