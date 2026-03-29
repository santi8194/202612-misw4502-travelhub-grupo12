# 🔍 TravelHub Search Service

Microservicio de búsqueda de hospedajes para la plataforma TravelHub. Utiliza **FastAPI**, **OpenSearch** y sigue los principios de **Arquitectura Hexagonal**.

## 🏗️ Arquitectura y Diseño

El servicio está diseñado bajo una arquitectura hexagonal (puertos y adaptadores) para desacoplar la lógica de negocio de las tecnologías externas:

```text
app/
├── domain/         # Núcleo: Entidades, Objetos de Valor e interfaces de Estrategia.
│                   # (Sin dependencias externas).
├── application/    # Casos de uso (BuscarHospedaje) y Puertos (Interfaces).
│                   # Define QUÉ hace el sistema.
└── infrastructure/ # Adaptadores: Implementación del Repositorio con OpenSearch.
                    # Define CÓMO se comunica con el exterior.
```

### Patrones Clave
- **Patrón Strategy**: Implementado para el ordenamiento de resultados (`RankingStrategy`). Permite cambiar la lógica de ranking (ej. Precio Primero) sin modificar el caso de uso.
- **Query Builder Delegado**: La lógica de filtrado por fechas y cupos se delega 100% a OpenSearch mediante una consulta DSL compleja con objetos `nested`, garantizando alto desempeño.

## 🚀 Cómo Levantarlo (Desarrollo Local)

### Prerrequisitos
- Docker y Docker Compose
- Python 3.11+

### 1. Levantar OpenSearch
El proyecto incluye un `docker-compose.yml` que lanza OpenSearch y Dashboards:
```bash
cd Backend/search
docker compose up -d
```
*Nota: Esperar unos 30 segundos a que el cluster esté listo (estado "green").*

### 2. Configurar Entorno Python
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Poblar Datos de Prueba (Seed)
Este paso crea el índice con el mapping `nested` correcto e inserta 8 hospedajes colombianos realistas:
```bash
python3 scripts/seed_data.py
```

### 4. Iniciar el Microservicio
```bash
uvicorn app.main:app --reload
```
La API estará disponible en [http://localhost:8000](http://localhost:8000).

## 📚 Documentación Interactiva (Swagger)

Puedes explorar y probar los endpoints interactivamente a través de las siguientes URLs una vez que el servicio esté corriendo:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## 📡 API Endpoints

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/health` | Estado del servicio. |
| `GET` | `/api/v1/search` | Búsqueda con filtros de ciudad, país, fechas y huéspedes. |
| `GET` | `/api/v1/search/destinations` | Autocompletado de destinos (sugerencias por prefijo). |

**Ejemplo de búsqueda:**
`GET /api/v1/search?ciudad=Cartagena&pais=Colombia&fecha_inicio=2026-03-28&fecha_fin=2026-03-30&huespedes=2`

**Ejemplo de autocompletado:**
`GET /api/v1/search/destinations?q=car`

## 🧪 Pruebas
El servicio cuenta con una cobertura exhaustiva (>90% en domain/application):
```bash
pytest tests/ -v
```

## 🛠️ Variables de Entorno
Configurables en `app/config.py` o mediante un archivo `.env`:
- `OPENSEARCH_ENDPOINT`: URL del cluster (default: `https://localhost:9200`)
- `OPENSEARCH_INDEX`: Nombre del índice (default: `hospedajes`)
- `OPENSEARCH_USER` / `OPENSEARCH_PASSWORD`: Credenciales.
