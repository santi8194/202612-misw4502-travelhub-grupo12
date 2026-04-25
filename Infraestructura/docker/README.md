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
- `http://localhost:5001/payment/health`
- `http://localhost:5001/pms-integration/health`
- `http://localhost:5001/partner-management/health`
- `http://localhost:5001/notification/health`


La saga ya queda incluida en el stack por defecto:

- `rabbitmq-broker`
- `redis-db`
- `booking-saga-worker`
- `notification`

Para validar que quedaron arriba:

```powershell
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml ps
```

Para apagar el stack local:

```powershell
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml down
```

## Copiar bases de datos locales (SQLite)

Si estas ejecutando el entorno local con Docker Compose (overlay local), puedes copiar las bases SQLite de cada microservicio para abrirlas en DBeaver.

Ubicate en esta carpeta:

```bash
cd Infraestructura/docker
```

Copiar cada base de datos:

```bash
docker cp travelhub-authservice:/src/data/auth.db ./auth.db
docker cp travelhub-catalog:/app/data/catalog.db ./catalog.db
docker cp travelhub-search:/app/data/search.db ./search.db
docker cp travelhub-booking:/src/instance/booking.db ./booking.db
docker cp travelhub-payment:/app/data/payments.db ./payments.db
docker cp travelhub-pms-integration:/app/data/pms.db ./pms.db
docker cp travelhub-partner-management:/app/data/partner_management.db ./partner_management.db
docker cp travelhub-notification:/app/data/notification.db ./notification.db
```

Si quieres validar la saga en ejecucion, revisa estos logs:

```bash
docker logs -f travelhub-booking-saga-worker
docker logs -f travelhub-rabbitmq
docker logs -f travelhub-notification
```

Verifica que los archivos quedaron en tu maquina:

```bash
ls -lh ./*.db
```

