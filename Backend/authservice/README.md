# Auth Service

Microservicio de autenticación para la plataforma hotelera. Genera tokens JWT stateless integrándose de forma mockeada con el servicio de Usuarios.

## Requisitos

- Python 3.9+

Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Pruebas y Cobertura

Desde la carpeta `Backend/AuthService`, ejecuta:

```bash
python -m pytest --maxfail=1 --disable-warnings --cov=. --cov-report=term-missing --cov-fail-under=80
```

Este comando estandariza la validacion de pruebas y fuerza una cobertura minima del 80%.

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

## Usuarios Mockeados por Defecto

En `app/services/user_service.py` se incluyeron los siguientes usuarios de prueba:

- **Admin/Partner**: `admin@hotel.com` / `admin123`
- **Usuario Normal**: `user@hotel.com` / `user123`

## Protección contra Fuerza Bruta

El servicio incorpora un mecanismo sencillo en memoria para bloqueo de cuentas tras varios intentos fallidos.
- **Límite**: 5 intentos fallidos
- **Bloqueo**: 15 minutos (configurable en `.env` o `config.py`)
