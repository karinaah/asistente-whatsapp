# AURA — Arquitectura

## Objetivos arquitectónicos

La arquitectura de AURA busca construir un asistente de productividad inteligente que sea:

- fácil de mantener;
- fácil de probar;
- explicable;
- extensible;
- desacoplado de proveedores externos.

Para lograrlo, el dominio se mantiene independiente de FastAPI, SQLAlchemy y cualquier integración específica.

---

# Principios de diseño

AURA sigue los siguientes principios arquitectónicos:

- Separación entre dominio, aplicación y persistencia.
- Repository Pattern.
- Service Layer.
- Dependency Injection.
- Modelos de dominio independientes.
- Motores especializados por responsabilidad.
- Reglas pequeñas y reutilizables.
- Aprendizaje adaptativo desacoplado del resto del sistema.

Cada componente debe tener una única responsabilidad y comunicarse mediante modelos de dominio bien definidos.

---

# Tecnologías

## Backend

- Python 3.11
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic

## Testing

- Pytest

---

# Capas de la aplicación

## Dominio

El dominio contiene los conceptos centrales de AURA.

Entre ellos:

- Task
- ScheduledTask
- PlanningRequest
- PlanningResponse
- TimeBlock
- Recommendation
- RecommendationReason
- DecisionContext
- HumanState
- TaskExecution
- AdaptiveProfile

El dominio no depende de FastAPI, SQLAlchemy ni de ninguna tecnología de infraestructura.

---

## Servicios de aplicación

Los servicios implementan los casos de uso del sistema.

Actualmente existen:

- TaskService
- PlannerService
- AdaptivePlanningService
- DecisionEngine
- LearningService
- AdaptiveProfileService
- TaskExecutionService
- HumanStateService
- RecommendationHistoryService

Los servicios coordinan la lógica del negocio sin acceder directamente a la base de datos.

---

## Persistencia

La persistencia se implementa mediante Repository Pattern.

Los servicios nunca ejecutan consultas SQL directamente.

Flujo general:

```text
Service
    │
    ▼
Repository
    │
    ▼
SQLAlchemy Model
    │
    ▼
SQLite
```

Repositorios actuales:

- TaskRepository
- TaskExecutionRepository
- HumanStateRepository
- RecommendationHistoryRepository
- AdaptiveProfileRepository

---

# Motores principales

AURA está organizado en motores independientes.

Cada motor tiene una responsabilidad claramente definida.

## Planner Engine

Responsable de construir automáticamente el plan diario.

Considera:

- prioridad;
- deadlines;
- horarios preferidos;
- bloques ocupados;
- descansos;
- contexto;
- duración estimada;
- Adaptive Profile.

El planner nunca modifica las tareas originales.

Cuando necesita ajustar una duración utiliza una copia temporal de la tarea.

---

## Decision Engine

Responsable de recomendar la mejor tarea para realizar en un momento determinado.

La recomendación se construye mediante reglas independientes.

Actualmente existen reglas para:

- prioridad;
- deadlines;
- contexto;
- tiempo disponible;
- energía;
- enfoque;
- estrés;
- tareas vencidas;
- preferencias horarias;
- aprendizaje adaptativo.

Cada regla aporta una puntuación y una explicación.

El resultado final es una recomendación completamente explicable.

---

## Learning Engine

Responsable de aprender del comportamiento real del usuario.

Analiza las ejecuciones registradas y detecta patrones.

Actualmente aprende:

- precisión de estimaciones;
- comportamiento por categoría;
- productividad según energía;
- hábitos generales.

El resultado del aprendizaje es un Adaptive Profile.

---

## Adaptive Profile Service

Representa el conocimiento consolidado que AURA tiene sobre el usuario.

Su responsabilidad es:

- reconstruir el perfil;
- persistirlo;
- recuperarlo;
- ponerlo a disposición del Planner y del Decision Engine.

Actualmente el perfil puede almacenar información como:

- multiplicadores de duración por categoría;
- preferencia por tareas cortas con baja energía;
- mejores condiciones conocidas de energía;
- mejores condiciones conocidas de enfoque;
- nivel de confianza del aprendizaje.

---

# Flujo de aprendizaje

El aprendizaje sigue el siguiente ciclo:

```text
Task Execution
        │
        ▼
Learning Engine
        │
        ▼
Adaptive Profile
        │
        ▼
SQLite
```

Cuando Planner o Decision Engine necesitan conocimiento adaptativo:

```text
SQLite
      │
      ▼
Adaptive Profile Service
      │
      ▼
Adaptive Profile
      ├──────────────┐
      ▼              ▼
Planner Engine   Decision Engine
```

De esta forma ambos motores utilizan exactamente el mismo conocimiento del usuario.

---

# API

FastAPI expone todos los casos de uso mediante una API REST.

Actualmente la API incluye endpoints para:

- tareas;
- planificación;
- recomendaciones;
- historial de recomendaciones;
- estado humano;
- ejecuciones;
- perfil adaptativo.

La documentación interactiva está disponible mediante Swagger.

---

# Testing

La arquitectura fue diseñada para facilitar las pruebas automatizadas.

Actualmente existen pruebas para:

- Planner Engine;
- Decision Engine;
- Learning Engine;
- Adaptive Profile Service;
- persistencia;
- reglas individuales;
- integración entre motores.

Versión actual:

**57 tests automatizados.**

---

# Visión

AURA no busca ser únicamente un gestor de tareas.

Su objetivo es convertirse en un asistente inteligente de productividad capaz de:

- planificar;
- recomendar;
- aprender;
- adaptarse;
- explicar sus decisiones.

Toda la arquitectura está diseñada para permitir que estas capacidades evolucionen de forma independiente sin comprometer la mantenibilidad del sistema.