# Docker local sin romper CD

El archivo `docker-compose.yml` sigue siendo el contrato base del despliegue automático.
Usa imágenes publicadas y las mismas variables que genera el workflow para conectarse al RDS.

Para desarrollo local sin alterar ese flujo:

```powershell
cd D:\Code\MISW\202612-misw4502-travelhub-grupo12\Infraestructura\docker
Copy-Item .env.local.example .env.local
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml config
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

Endpoints esperados por `nginx`:

- `http://localhost:5001/auth/health`
- `http://localhost:5001/booking/health`
- `http://localhost:5001/catalog/health`
- `http://localhost:5001/search/health`

Si necesitas los auxiliares de saga y mensajería:

```powershell
docker compose --profile saga --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

Para apagar el stack local:

```powershell
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml down
```
