# Autenticación

## Servicio responsable

`authservice` centraliza autenticación, registro, refresco de token y consulta de usuario autenticado.

## Mecanismo

- Tokens JWT stateless.
- Rutas principales: `POST /login`, `POST /refresh`, `GET /me`.
- La documentación operativa vive en [`../../Backend/authservice/README.md`](../../Backend/authservice/README.md).

## Regla documental

Cuando una API requiera autenticación, el README local del servicio debe indicarlo de forma explícita y enlazar a este documento.
