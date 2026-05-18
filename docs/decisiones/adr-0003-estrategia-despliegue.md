# ADR-0003: Estrategia de despliegue híbrida

## Estado

Aceptado

## Contexto

El proyecto necesita desarrollo local reproducible y despliegue remoto sobre AWS.

## Decisión

Usar Docker Compose para desarrollo local, Minikube para validación en Kubernetes y Terraform con GitHub Actions para AWS.

## Consecuencias

- Permite probar por niveles de fidelidad.
- Mantiene una ruta local accesible y una ruta remota automatizada.
- Requiere documentación clara de entornos y configuración.
