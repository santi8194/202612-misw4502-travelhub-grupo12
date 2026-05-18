# Docker local sin romper CD

El archivo `docker-compose.yml` sigue siendo el contrato base del despliegue automatico.
Usa imagenes publicadas y las mismas variables que genera el workflow para conectarse al RDS.

Para desarrollo local sin alterar ese flujo, usa siempre el override `docker-compose.local.yml`.

Modo SQLite local:

```powershell
cd D:\Code\MISW\202612-misw4502-travelhub-grupo12\Infraestructura\docker
# Si ya tienes la plantilla local ignorada:
Copy-Item .env.local.sqlite.dev .env.local
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

Modo RDS:

```powershell
cd D:\Code\MISW\202612-misw4502-travelhub-grupo12\Infraestructura\docker
# Si ya tienes la plantilla local ignorada:
Copy-Item .env.local.rds.dev .env.local
# Edita .env.local con los hosts, usuarios y passwords reales de cada base
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml up -d --build
```

Las plantillas `.env.local.sqlite.dev` y `.env.local.rds.dev` son archivos locales ignorados por Git. En un clon nuevo no aparecen hasta que el equipo los provea por un canal seguro o se creen plantillas `.example` sanitizadas y versionadas.

El overlay local actual incluye `ngrok` siempre. Si `NGROK_AUTHTOKEN` queda vacio, el resto del stack puede iniciar, pero el contenedor de `ngrok` no quedara operativo. Para un entorno local realmente limpio, configura el token o separa `ngrok` a un overlay/perfil opcional en una mejora posterior.

La regla es simple:

- Si `DB_*` viene completo para un servicio, ese servicio usa Postgres/RDS.
- Si `DB_*` queda vacio, ese servicio arranca con SQLite local.

Los archivos SQLite locales quedan persistidos en volumenes Docker para:

- `authservice`
- `catalog`
- `booking`
- `search`
- `payment`
- `pms-integration`
- `partner-management`
- `notification`

Antes de levantar el stack, puedes validar que la combinacion de archivos renderiza correctamente:

```powershell
docker compose --env-file .env.local -f docker-compose.yml -f docker-compose.local.yml config
```

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

## Docker Compose local con ngrok

Cada integrante debe configurar su propio token de ngrok en su archivo local no versionado:

```env
NGROK_AUTHTOKEN=tu_token_personal_de_ngrok
```

Para levantar el stack local con RDS, ngrok y el `user-web` recompilado con la URL publica del tunel:

```powershell
cd D:\Code\MISW\202612-misw4502-travelhub-grupo12
.\Infraestructura\scripts\run-local-ngrok.ps1
```

El script:

- valida que existan las variables Wompi y `NGROK_AUTHTOKEN`;
- levanta Docker Compose local, incluyendo el servicio `ngrok`;
- obtiene la URL publica HTTPS desde el inspector local de ngrok;
- reconstruye `user-web` con esa URL para el retorno del widget de Wompi;
- imprime la URL exacta de webhook que se debe registrar en Wompi Sandbox.

El servicio `ngrok` vive dentro de Docker Compose, por lo que no es necesario instalar el binario de ngrok en cada maquina del equipo. Cada persona solo necesita su token propio en el archivo `.env.local.rds.dev` o en el archivo local que use para el entorno RDS.

La configuracion del inspector local de ngrok se define en `ngrok.yml`, que expone la interfaz del agente en `0.0.0.0:4040` dentro del contenedor para poder consultarla desde `http://localhost:4040`.

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

## Variante heredada

El archivo `docker-compose.local.orl.yml` queda hoy como una variante local heredada con Postgres centralizado y un subconjunto del stack.

- No lo usa ningun script, workflow ni README activo del repositorio.
- No es la entrada recomendada para desarrollo local.
- Si se conserva, debe tratarse como una variante manual aislada hasta que el equipo decida si la documenta formalmente o la elimina.

## Documentación relacionada

- [`../../docs/operacion/README.md`](../../docs/operacion/README.md)
- [`../../docs/arquitectura/despliegue-y-entornos.md`](../../docs/arquitectura/despliegue-y-entornos.md)
