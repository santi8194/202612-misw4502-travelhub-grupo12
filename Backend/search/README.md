# 🔍 TravelHub Search Service

Microservicio de búsqueda de hospedajes para la plataforma TravelHub. Utiliza **FastAPI**, **PostgreSQL** (por defecto), **OpenSearch** (opcional) y sigue los principios de **Arquitectura Hexagonal**.

## 🏗️ Arquitectura y Diseño

El servicio está diseñado bajo una arquitectura hexagonal (puertos y adaptadores) para desacoplar la lógica de negocio de las tecnologías externas:

```text
app/
├── domain/         # Núcleo: Entidades, Objetos de Valor e interfaces de Estrategia.
├── application/    # Casos de uso (BuscarHospedaje), DTOs y Puertos (Interfaces).
├── infrastructure/ # Adaptadores: Repositorios (PostgresHospedaje, PostgresDestination, OpenSearch).
├── routers/        # Rutas de FastAPI (Endpoints).
├── dependencies.py # Inyección de dependencias y validación de parámetros.
├── main.py         # Punto de entrada y gestión del ciclo de vida (Lifespan).
└── config.py       # Configuración centralizada vía Pydantic Settings (.env).
```

### Patrones y Principios Clave
- **Patrón Strategy**: Implementado para el ordenamiento de resultados (`RankingStrategy`). Cada estrategia genera tanto cláusulas SQL como DSL de OpenSearch.
- **Multimotor**: Soporte nativo para PostgreSQL (usando `JSONB` para disponibilidad) y OpenSearch (usando objetos `nested`). Se selecciona mediante configuración.
- **Esquema de Datos**: Todas las tablas residen en el esquema `search` de PostgreSQL (`search.hospedajes` y `search.destinos`).
- **Autocompletado de Destinos**: Implementado en PostgreSQL usando índices de prefijo (`varchar_pattern_ops`) sobre la columna `ciudad_lower` para búsquedas eficientes y normalizadas.

### 🐘 PostgreSQL vs 🔵 OpenSearch
El servicio permite elegir el motor de búsqueda de hospedajes mediante la variable `REPOSITORY_TYPE`. El autocompletado de destinos **siempre** utiliza PostgreSQL.

| Atributo | PostgreSQL (Default) | OpenSearch (Opcional) |
| :--- | :--- | :--- |
| **Uso Ideal** | Operaciones transaccionales y búsqueda moderada. | Búsqueda de alto rendimiento y gran escala. |
| **Tecnología** | Esquema SQL con `JSONB` para disponibilidad. | Índice invertido con objetos `nested`. |
| **Consistencia** | Fuerte consistencia (ACID). | Consistencia eventual. |
| **Configuración** | `REPOSITORY_TYPE=postgres` | `REPOSITORY_TYPE=opensearch` |

---

## 🚀 Cómo Levantarlo

### Prerrequisitos
- Docker y Docker Compose
- Python 3.11+ (para desarrollo local)

### 1. Configurar Variables de Entorno
Copia la plantilla de ejemplo y ajusta los valores si es necesario:
```bash
cd Backend/search
cp .env.example .env
```

### 2. Opción A: Levantar con Docker (Recomendado)
El proyecto incluye un `Dockerfile` multi-stage optimizado y un `docker-compose.yml` que empaqueta la aplicación y su base de datos.

```bash
# Construir y levantar el servicio + base de datos
docker compose up -d --build
```
La API estará disponible en [http://localhost:8000](http://localhost:8000).

### 3. Opción B: Desarrollo Local
Si prefieres correr el código directamente:

```bash
# A. Levantar solo la base de datos
docker compose up -d postgres

# B. Configurar entorno Python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt  # Incluye herramientas de test

# C. Poblar Datos de Prueba (Seed)
# Esto crea el esquema 'search', las tablas, índices e inserta datos.
python3 scripts/seed_data.py

# D. Iniciar el Microservicio
uvicorn app.main:app --reload
```

---

## 📡 API Endpoints

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/health` | Estado del servicio y salud de la infraestructura. |
| `GET` | `/api/v1/search` | Búsqueda por ciudad, fechas y huéspedes. |
| `GET` | `/api/v1/search/destinations` | Sugerencias de destinos (vía Postgres). |

---

## 🧪 Pruebas
El servicio cuenta con una cobertura completa incluyendo tests unitarios e integrados:
```bash
# Requiere tener instalado requirements-dev.txt
pytest tests/ -v --tb=short
```
## Combinación. Correr dockercompose y poblar datos 
cd Backend/search

# 1. Crear el .env desde la plantilla
cp .env.example .env

# 2. Levantar postgres + compilar y arrancar search
docker compose up -d

# 3. Poblar Datos de Prueba (Seed)
python3 scripts/seed_data.py

# 4. Verificar
curl http://localhost:8000/health


---

## 🛠️ Configuración (.env)
Configurables mediante el archivo `.env`:

- `REPOSITORY_TYPE`: Motor para búsqueda de hospedajes (`postgres` o `opensearch`).
- `DB_HOST`: Host de PostgreSQL (ej: `localhost`, `postgres`).
- `DB_PORT`: Puerto de PostgreSQL (default: `5432`).
- `DB_NAME`: Nombre de la base de datos.
- `DB_USER`: Usuario de PostgreSQL.
- `DB_PASSWORD`: Contraseña de PostgreSQL.
- `OPENSEARCH_ENDPOINT`: URL del cluster OpenSearch.
- `OPENSEARCH_INDEX`: Nombre del índice de hospedajes.
- `OPENSEARCH_USER` / `OPENSEARCH_PASSWORD`: Credenciales de OpenSearch.
- `OPENSEARCH_VERIFY_CERTS`: `false` para entornos de desarrollo.
