# Documentación técnica de TravelHub

Esta carpeta contiene la documentación transversal y canónica del sistema. La documentación operativa de cada componente permanece junto a su código y se enlaza desde aquí cuando se requiere detalle.

## Lectura recomendada

| Necesidad | Documento |
| --- | --- |
| Entender el sistema completo | [`arquitectura/vision-general.md`](./arquitectura/vision-general.md) |
| Ver componentes y relaciones | [`arquitectura/contexto-y-componentes.md`](./arquitectura/contexto-y-componentes.md) |
| Seguir flujos de negocio | [`arquitectura/flujos-criticos.md`](./arquitectura/flujos-criticos.md) |
| Revisar entornos y despliegue | [`arquitectura/despliegue-y-entornos.md`](./arquitectura/despliegue-y-entornos.md) |
| Consultar servicios | [`microservicios/catalogo-servicios.md`](./microservicios/catalogo-servicios.md) |
| Consultar eventos | [`microservicios/contratos-eventos.md`](./microservicios/contratos-eventos.md) |
| Consultar APIs | [`api/endpoints.md`](./api/endpoints.md) |
| Operar el sistema | [`operacion/README.md`](./operacion/README.md) |
| Revisar decisiones | [`decisiones/README.md`](./decisiones/README.md) |

## Regla documental

- La documentación transversal vive en `docs/`.
- La documentación de ejecución de cada componente vive junto al componente.
- Los documentos centrales resumen y redirigen; no duplican guías locales extensas.
- Los diagramas técnicos versionados se mantienen en Mermaid.
