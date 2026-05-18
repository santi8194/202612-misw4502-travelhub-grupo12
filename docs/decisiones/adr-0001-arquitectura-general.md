# ADR-0001: Arquitectura general distribuida

## Estado

Aceptado

## Contexto

TravelHub requiere separar capacidades de negocio, frontends y despliegue para evolucionar dominios de forma independiente.

## Decisión

Adoptar frontends separados y servicios backend por dominio, combinando HTTP para interacción directa y eventos para coordinación asíncrona.

## Consecuencias

- Mejora la separación de responsabilidades.
- Exige contratos de eventos y documentación transversal.
- Introduce mayor complejidad operativa que una aplicación monolítica.
