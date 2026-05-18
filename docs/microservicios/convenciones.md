# Convenciones compartidas

## APIs

- Exponer endpoint de salud cuando el servicio sea desplegable.
- Documentar rutas públicas en el README local y en el catálogo global de endpoints.
- Mantener autenticación y errores documentados en `docs/api/`.

## Eventos

- Publicar sobre `travelhub.events.exchange`.
- Preferir routing keys con formato `evt.<dominio>.<resultado>`.
- Documentar eventos nuevos en [`contratos-eventos.md`](./contratos-eventos.md).

## Documentación local

Cada README local debe incluir:

- propósito;
- responsabilidad;
- dependencias;
- requisitos;
- configuración;
- ejecución local;
- pruebas;
- interfaces principales;
- documentación relacionada.

## Diagramas

- Formato oficial: Mermaid.
- Ubicación central: `docs/arquitectura/diagramas/`.
