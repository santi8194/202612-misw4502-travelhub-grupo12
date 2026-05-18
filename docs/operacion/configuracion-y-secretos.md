# Configuración y secretos

## Fuentes de configuración

- Archivos `.env` locales para desarrollo.
- Secrets Manager y secretos de GitHub Actions para despliegues remotos.
- Variables de entorno específicas por servicio documentadas en sus README locales.

## Regla de documentación

- La documentación central describe el modelo general.
- Los nombres concretos de variables y secretos se mantienen junto al componente que los usa.
- Los secretos reales no deben versionarse en el repositorio.

## Referencias

- Docker local: [`../../Infraestructura/docker/README.md`](../../Infraestructura/docker/README.md)
- Remote state Terraform: [`../../Infraestructura/terraform/REMOTE_STATE_DEV.md`](../../Infraestructura/terraform/REMOTE_STATE_DEV.md)
- Firmado Android: [`../../Frontend/mobile-app/docs/guia_firmado_android.md`](../../Frontend/mobile-app/docs/guia_firmado_android.md)
