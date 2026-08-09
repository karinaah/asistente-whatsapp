# AURA — Arquitectura

## Filosofía

AURA está diseñado como un asistente inteligente de productividad compuesto por motores independientes.

Cada motor tiene una única responsabilidad y produce modelos de dominio explícitos que pueden ser reutilizados por otros componentes del sistema.

La arquitectura prioriza:

- mantenibilidad;
- explicabilidad;
- extensibilidad;
- facilidad de prueba;
- desacoplamiento entre dominio e infraestructura.

---

# Objetivos arquitectónicos

La arquitectura de AURA debe permitir:

- probar el dominio sin depender de FastAPI;
- cambiar la persistencia sin modificar la lógica del negocio;
- incorporar proveedores externos sin afectar el núcleo;
- mantener decisiones completamente explicables;
- aprender automáticamente del comportamiento del usuario;
- evolucionar mediante componentes independientes.

---

# Principios de diseño

AURA utiliza una combinación de principios y patrones arquitectónicos.

## Principios

- Responsabilidad única.
- Bajo acoplamiento.
- Alta cohesión.
- Explicabilidad por diseño.
- Dominio independiente de la infraestructura.
- Arquitectura incremental.

## Patrones

- Repository Pattern
- Service Layer
- Dependency Injection
- Domain Models
- Rule-based Engines
- Explainable Models
- Workflow Services

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

# Arquitectura por capas

## Dominio

El dominio contiene exclusivamente conceptos del negocio.

No depende de FastAPI, SQLAlchemy ni de ninguna otra tecnología.

Principales modelos:

- Task
- ScheduledTask
- PlanningRequest
- PlanningResponse
- PlanningDecision
- PlanningReason
- Recommendation
- RecommendationReason
- HumanState
- TaskExecution
- LearningInsight
- AdaptiveProfile
- Explanation

---

## Servicios de aplicación

Los servicios coordinan los casos de uso.

Actualmente existen:

- TaskService
- PlannerService
- AdaptivePlanningService
- DecisionEngine
- LearningService
- AdaptiveProfileService
- HumanStateService
- RecommendationHistoryService
- TaskExecutionService

---

## Persistencia

La persistencia está completamente desacoplada mediante Repository Pattern.

Los servicios nunca ejecutan consultas SQL directamente.

Flujo:

```text
Service
    │
    ▼
Repository
    │
    ▼
SQLAlchemy
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

## Workflow Services

Los workflows encapsulan casos de uso completos reutilizando múltiples servicios de aplicación.

Su objetivo es ofrecer una única interfaz para operaciones complejas, evitando que los endpoints o el Assistant conozcan los detalles internos de los motores.

Actualmente:

- PlanningWorkflowService
- RecommendationWorkflowService


---

## Assistant Layer

La Assistant Layer proporciona una interfaz conversacional unificada sobre los distintos motores de AURA.

Su responsabilidad consiste en interpretar la intención del usuario, seleccionar el caso de uso adecuado y orquestar los distintos Workflow Services y motores del sistema.

Actualmente incluye:

- AssistantChatService
- IntentDetectionService

Las principales intenciones soportadas son:

- planificación;
- recomendaciones;
- aprendizaje;
- explicaciones.

Esta capa desacopla la interacción con el usuario de la lógica de negocio, permitiendo que los motores evolucionen de forma independiente.
---


# Motores

AURA se compone de cuatro motores principales.

## Planner Engine

Responsable de construir automáticamente un plan diario.

Considera:

- prioridad;
- deadlines;
- preferencias horarias;
- bloques ocupados;
- descansos;
- contexto;
- duración estimada;
- Adaptive Profile.

Produce:

- PlanningResponse
- PlanningDecision

Las decisiones de planificación permiten explicar posteriormente por qué cada tarea fue ubicada en un determinado horario.

---

## Decision Engine

Responsable de recomendar la mejor tarea para ejecutar.

Utiliza un conjunto de reglas independientes.

Actualmente considera:

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

Produce:

- Recommendation
- RecommendationReason

Todas las recomendaciones son completamente explicables.

---

## Learning Engine

Responsable de aprender automáticamente del comportamiento del usuario.

Analiza:

- duración estimada;
- duración real;
- comportamiento por categoría;
- productividad según energía;
- hábitos generales.

Produce:

- LearningInsight
- AdaptiveProfile

El conocimiento aprendido es reutilizado por el Planner y el Decision Engine.

---

## Explanation Engine

Responsable de transformar el conocimiento interno del sistema en explicaciones naturales.

Actualmente incluye:

- AdaptiveProfileExplanationService
- RecommendationExplanationService
- PlanningExplanationService
- LearningExplanationService

Todos producen el modelo unificado:

- Explanation

De esta manera la lógica del negocio permanece separada de la presentación.

---

# Servicios compartidos

## AdaptiveProfileService

Gestiona el conocimiento consolidado del usuario.

Responsabilidades:

- reconstruir el perfil;
- persistirlo;
- recuperarlo;
- entregarlo a los motores que lo requieren.

Actualmente almacena:

- multiplicadores de duración;
- preferencias aprendidas;
- mejores condiciones conocidas;
- nivel de confianza del aprendizaje.

---

# Flujos principales

## Flujo de aprendizaje

```text
TaskExecution
        │
        ▼
Learning Engine
        │
        ▼
AdaptiveProfile
        │
        ▼
SQLite
```

---

## Flujo adaptativo

```text
SQLite
      │
      ▼
AdaptiveProfileService
      │
      ▼
AdaptiveProfile
      ├───────────────┐
      ▼               ▼
Planner Engine   Decision Engine
```

---

## Flujo de explicaciones

```text
Planner Engine
        │
        ▼
PlanningDecision
        │
        ▼
PlanningExplanationService
        │
        ▼
Explanation
```

```text
Decision Engine
        │
        ▼
Recommendation
        │
        ▼
RecommendationExplanationService
        │
        ▼
Explanation
```

```text
Learning Engine
        │
        ▼
LearningInsight
        │
        ▼
LearningExplanationService
        │
        ▼
Explanation
```

```text
AdaptiveProfile
        │
        ▼
AdaptiveProfileExplanationService
        │
        ▼
Explanation
```

---

# API

FastAPI expone los casos de uso mediante una API REST.

Actualmente existen endpoints para:

- tareas;
- planificación;
- recomendaciones;
- historial de recomendaciones;
- estado humano;
- ejecuciones;
- aprendizaje;
- perfil adaptativo;
- explicaciones.
- asistente conversacional.

El endpoint `/assistant/chat` constituye la principal interfaz conversacional del sistema y reutiliza los motores existentes mediante la Assistant Layer.

---

# Testing

La arquitectura fue diseñada para facilitar pruebas unitarias e integración.

Actualmente existen pruebas para:

- Planner Engine;
- Decision Engine;
- Learning Engine;
- Adaptive Profile;
- servicios de explicación;
- persistencia;
- reglas individuales;
- integración entre motores.

**74 tests automatizados.**

---

# Visión

AURA no busca ser únicamente un gestor de tareas.

Su objetivo es convertirse en un asistente inteligente capaz de:

- planificar;
- recomendar;
- aprender;
- adaptarse;
- explicar cada decisión que toma.

La interacción con el usuario se realiza mediante una capa conversacional que reutiliza estos motores, permitiendo ofrecer una experiencia unificada sin acoplar la interfaz a la lógica del negocio.

## Flujo conversacional

```text
Usuario
      │
      ▼
AssistantChatService
      │
      ▼
IntentDetectionService
      │
      ├───────────────┬───────────────┬───────────────┐
      ▼               ▼               ▼               ▼
Planning        Recommendation    Learning     Explanation
Workflow         Workflow
      │               │
      └───────────────┴───────────────┐
                                      ▼
                              AssistantResponse

# 7. Servicios de aplicación

Yo agregaría:

```markdown
- AssistantChatService
- IntentDetectionService                              