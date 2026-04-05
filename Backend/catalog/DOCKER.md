# Guía de Ejecución con Docker - Catalog Service

## Requisitos Previos

- Docker instalado (`docker --version`)
- Docker Compose instalado (`docker-compose --version`)

---

## Ejecutar con Docker Directo

### Paso 1: Construir la imagen
```bash
cd Backend/catalog
docker build -t catalog-service:1.0 .
```

### Paso 2: Ejecutar el contenedor
```bash
docker run -d \
  --name catalog-service \
  -p 8005:8005 \
  -e ENABLE_EVENTS=false \
  catalog-service:1.0
```

### Paso 3: Verificar que está corriendo
```bash
docker ps | grep catalog-service
```

### Paso 4: Probar el servicio
```bash
curl http://localhost:8005/catalog/properties
```

Utilizar colección de postman

### Detener el contenedor
```bash
docker stop catalog-service
docker rm catalog-service
