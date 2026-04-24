# Docker local sin romper CD

El archivo `docker-compose.yml` sigue siendo el contrato base del despliegue automatico.
Usa imagenes publicadas y las mismas variables que genera el workflow para conectarse al RDS.

Para desarrollo local sin alterar ese flujo, usa siempre el override `docker-compose.local.yml`.

Modo SQLite local:

```powershell
cd D:\Code\MISW\202612-misw4502-travelhub-grupo12\Infraestructura\docker
Copy-Item .env.local.sqlite.example .env.local
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

Modo RDS:

```powershell
cd D:\Code\MISW\202612-misw4502-travelhub-grupo12\Infraestructura\docker
Copy-Item .env.local.rds.example .env.local
# Edita .env.local con los hosts, usuarios y passwords reales de cada base
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

La regla es simple:

- Si `DB_*` viene completo para un servicio, ese servicio usa Postgres/RDS.
- Si `DB_*` queda vacio, ese servicio arranca con SQLite local.

Los archivos SQLite locales quedan persistidos en volumenes Docker para:

- `authservice`
- `catalog`
- `booking`
- `search`

Endpoints esperados por `nginx`:

- `http://localhost:5001/auth/health`
- `http://localhost:5001/booking/health`
- `http://localhost:5001/catalog/health`
- `http://localhost:5001/search/health`

Si necesitas los auxiliares de saga y mensajeria:

```powershell
docker compose --profile saga --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

Para apagar el stack local:

```powershell
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml down
```
