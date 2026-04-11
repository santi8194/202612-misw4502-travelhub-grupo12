# Auth Service

Microservicio de autenticación para la plataforma hotelera. Genera tokens JWT stateless y persiste usuarios en PostgreSQL.

## Requisitos

- Python 3.9+

Instala las dependencias:

```bash
pip install -r requirements.txt
```

Variables de entorno requeridas para la base de datos:

```bash
DB_HOST=travelhub-dev-authservice.cwfag2842c2y.us-east-1.rds.amazonaws.com
DB_PORT=5432
DB_NAME=authservice_db
DB_USER=<usuario_rds>
DB_PASSWORD=<password_rds>
```

También puedes usar una sola variable:

```bash
DATABASE_URL=postgresql+psycopg2://<usuario_rds>:<password_rds>@travelhub-dev-authservice.cwfag2842c2y.us-east-1.rds.amazonaws.com:5432/authservice_db
```

## Ejecución

Para iniciar el servidor en modo desarrollo:

```bash
uvicorn main:app --reload --port 8000
```

La documentación interactiva (Swagger) estará disponible en: [http://localhost:8000/docs](http://localhost:8000/docs)

## Ejemplos de Uso

### 1. Iniciar Sesión (Login JSON request)

```bash
curl -X 'POST' \
  'http://localhost:8000/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "admin@hotel.com",
  "password": "admin123"
}'
```

**Respuesta Exitosa:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Obtener Usuario Actual (/me)
Requiere pasar el **access_token** obtenido en el Header `Authorization`.

```bash
curl -X 'GET' \
  'http://localhost:8000/auth/me' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <TOKEN_AQUI>'
```

### 3. Refrescar Token (/refresh)
Genera un nuevo token JWT a partir de uno existente.

```bash
curl -X 'POST' \
  'http://localhost:8000/auth/refresh' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer <TOKEN_AQUI>'
```

## Usuarios Iniciales

Cuando la tabla `users` está vacía, el servicio crea estos usuarios de prueba automáticamente:

- **Admin/Partner**: `admin@hotel.com` / `123456`
- **Usuario Normal**: `user@hotel.com` / `user123`

## Protección contra Fuerza Bruta

El servicio incorpora un mecanismo sencillo en memoria para bloqueo de cuentas tras varios intentos fallidos.
- **Límite**: 5 intentos fallidos
- **Bloqueo**: 15 minutos (configurable en `.env` o `config.py`)
