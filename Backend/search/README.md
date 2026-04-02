# 🔍 TravelHub Search Service

Microservicio de búsqueda de hospedajes para la plataforma TravelHub. Utiliza **FastAPI**, **PostgreSQL** (por defecto), **OpenSearch** (opcional) y sigue los principios de **Arquitectura Hexagonal**.

## 🏗️ Arquitectura y Diseño

El servicio está diseñado bajo una arquitectura hexagonal (puertos y adaptadores) para desacoplar la lógica de negocio de las tecnologías externas:

```text
app/
├── domain/         # Núcleo: Entidades, Objetos de Valor e interfaces de Estrategia.
├── application/    # Casos de uso (BuscarHospedaje), DTOs y Puertos (Interfaces).
├── infrastructure/ # Adaptadores: Repositorios (Postgres, OpenSearch, Redis).
├── routers/        # Rutas de FastAPI (Endpoints).
├── dependencies.py # Inyección de dependencias y validación de parámetros.
├── main.py         # Punto de entrada y gestión del ciclo de vida (Lifespan).
└── config.py       # Configuración centralizada vía variables de entorno.
```

### Patrones y Principios Clave
- **Patrón Strategy**: Implementado para el ordenamiento de resultados (`RankingStrategy`). Cada estrategia genera tanto cláusulas SQL como DSL de OpenSearch.
- **Multimotor**: Soporte nativo para PostgreSQL (usando `JSONB` para disponibilidad) y OpenSearch (usando objetos `nested`). Se selecciona mediante configuración.
- **Delegación de Búsqueda**: El filtrado por fechas y cupos se realiza enteramente en el motor de base de datos (SQL en Postgres o DSL en OpenSearch), garantizando alto desempeño.

### 🐘 PostgreSQL vs 🔵 OpenSearch
El servicio permite elegir el motor según la necesidad:

| Atributo | PostgreSQL (Default) | OpenSearch (Opcional) |
| :--- | :--- | :--- |
| **Uso Ideal** | Operaciones transacciones y búsqueda moderada. | Búsqueda de alto rendimiento y gran escala. |
| **Tecnología** | Esquema SQL con `JSONB` para disponibilidad. | Índice invertido con objetos `nested`. |
| **Consistencia** | Fuerte consistencia (ACID). | Consistencia eventual. |
| **Configuración** | `REPOSITORY_TYPE=postgres` | `REPOSITORY_TYPE=opensearch` |

## 🚀 Cómo Levantarlo (Desarrollo Local)

### Prerrequisitos
- Docker y Docker Compose
- Python 3.11+

### 1. Levantar Infraestructura
El proyecto incluye un `docker-compose.yml` que lanza **Postgres** y **Redis**.
*Nota: Los servicios de OpenSearch están comentados por defecto en el archivo para ahorrar recursos.*

```bash
cd Backend/search
docker compose up -d
```

### 2. Configurar Entorno Python
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Poblar Datos de Prueba (Seed)
Este script crea la tabla de Postgres, el índice de OpenSearch (si está activo) e inserta 8 hospedajes de prueba:

```bash
python3 scripts/seed_data.py
```

### 4. Iniciar el Microservicio
```bash
uvicorn app.main:app --reload
```
La API estará disponible en [http://localhost:8000](http://localhost:8000).

## 📡 API Endpoints

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/health` | Estado del servicio. |
| `GET` | `/api/v1/search` | Búsqueda por ciudad, fechas y huéspedes. |
| `GET` | `/api/v1/search/destinations` | Autocompletado de destinos (vía Redis). |

## 🧪 Pruebas
El servicio cuenta con una cobertura completa incluyendo tests unitarios e integrados (60+ tests):
```bash
pytest tests/ -v
```

## 🛠️ Variables de Entorno
Configurables en `app/config.py` o mediante un archivo `.env`:

- `REPOSITORY_TYPE`: Motor activo (`postgres` o `opensearch`). Default: `postgres`.
- `POSTGRES_URL`: URL de conexión a Postgres.
- `REDIS_URL`: URL de conexión a Redis (siempre necesario para destinos).
- `OPENSEARCH_ENDPOINT`: URL del cluster OpenSearch.
- `OPENSEARCH_INDEX`: Nombre del índice.
