# AURA — Arquitectura

## Objetivos arquitectónicos

La arquitectura de AURA debe permitir:

- probar el dominio sin depender de FastAPI;
- cambiar la base de datos sin reescribir el planner;
- agregar proveedores externos sin acoplarlos al núcleo;
- mantener decisiones de planificación explicables;
- evolucionar gradualmente sin grandes reescrituras.

## Tecnologías actuales

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pytest

## Patrones principales

- Repository Pattern
- Dependency Injection
- Separación entre dominio, servicios e infraestructura
- Servicios pequeños con responsabilidades claras

## Capas

### Dominio

Contiene los conceptos centrales de AURA:

- Task
- TaskContext
- TimeBlock
- AvailableSlot
- ScheduledTask
- PlanningRequest
- PlanningResponse
- ScoreBreakdown

El dominio no debe depender de FastAPI, SQLAlchemy ni proveedores externos.

### Servicios de aplicación

Coordinan los casos de uso:

- PlannerService
- TaskSorter
- ScoringEngine

Responsabilidades actuales:

#### PlannerService

- coordinar la creación del plan;
- encontrar espacios disponibles;
- seleccionar slots;
- crear la línea de tiempo;
- gestionar tareas no programadas.

#### TaskSorter

- definir el orden previo de planificación.

#### ScoringEngine

- evaluar slots;
- calcular fragmentación;
- evaluar preferencias;
- evaluar deadlines;
- producir ScoreBreakdown.

### Persistencia

Los repositorios abstraen el almacenamiento.

Los servicios no deben ejecutar consultas SQL directamente.

```text
Service
   ↓
Repository Interface
   ↓
SQLAlchemy Repository
   ↓
Database