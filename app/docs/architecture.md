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
- mantener contexto conversacional básico;
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

El dominio contiene los modelos que representan los conceptos principales utilizados por los motores y servicios de AURA.

La lógica del dominio permanece desacoplada de FastAPI y de los detalles de infraestructura.

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
- ConversationContext

---

## Servicios de aplicación

Los servicios coordinan los casos de uso y encapsulan la lógica necesaria para utilizar los distintos motores del sistema.

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
- ConversationMemoryService
- AssistantChatService
- IntentDetectionService

También existen servicios especializados de explicación:

- AdaptiveProfileExplanationService
- RecommendationExplanationService
- PlanningExplanationService
- LearningExplanationService

---

## Persistencia

La persistencia está desacoplada mediante Repository Pattern.

Los servicios utilizan repositorios para acceder a la información persistida, evitando que la lógica de aplicación dependa directamente de consultas SQL.

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

Su objetivo es ofrecer una única interfaz para operaciones complejas, evitando que los endpoints o la Assistant Layer conozcan los detalles internos de los motores.

Actualmente existen:

- PlanningWorkflowService
- RecommendationWorkflowService

`PlanningWorkflowService` permite construir planes utilizando las tareas persistidas y el perfil adaptativo.

También permite obtener el plan y sus decisiones explicables dentro de una misma ejecución del Planner, evitando ejecutar innecesariamente el motor más de una vez.

`RecommendationWorkflowService` coordina la planificación, el estado humano, el perfil adaptativo, el Decision Engine y el historial necesario para producir recomendaciones.

---

## Memoria conversacional

AURA mantiene contexto temporal durante una conversación mediante `ConversationMemoryService`.

El estado conversacional se representa mediante `ConversationContext`.

Actualmente conserva:

- última intención detectada;
- última recomendación;
- último plan generado.

Flujo:

```text
ConversationMemoryService
        │
        ▼
ConversationContext
        │
        ├── last_intent
        ├── last_recommendation
        └── last_plan
```

Esta memoria permite reutilizar información de interacciones anteriores sin consultar o recalcular innecesariamente información.

Por ejemplo:

```text
Usuario: ¿Qué hago ahora?
        │
        ▼
Recommendation
        │
        ▼
last_recommendation

Usuario: ¿Por qué?
        │
        ▼
ConversationMemoryService
        │
        ▼
last_recommendation
```

Cuando la información necesaria no está disponible en memoria, los servicios persistentes pueden actuar como fallback.

Por ejemplo, las explicaciones de recomendaciones pueden utilizar `RecommendationHistoryService` cuando no existe una recomendación disponible en el contexto conversacional.

La memoria conversacional actual reside en memoria durante la ejecución de la aplicación. No representa todavía una sesión persistente ni una memoria multiusuario.

---

## Assistant Layer

La Assistant Layer proporciona una interfaz conversacional unificada sobre los distintos motores de AURA.

Su responsabilidad consiste en interpretar la intención del usuario, seleccionar el caso de uso adecuado y orquestar los Workflow Services y servicios de aplicación correspondientes.

Actualmente incluye:

- AssistantChatService
- IntentDetectionService
- ConversationMemoryService

Las principales intenciones soportadas son:

- planificación;
- recomendaciones;
- aprendizaje;
- explicaciones;
- seguimiento contextual (`follow_up`).

Esta capa desacopla la interacción con el usuario de la lógica de negocio, permitiendo que los motores evolucionen de forma independiente.

El endpoint principal de esta capa es:

```text
POST /assistant/chat
```

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

El Planner también puede producir el plan y sus decisiones en una única ejecución para evitar cálculos duplicados cuando ambos resultados son necesarios.

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

Todas las recomendaciones son explicables mediante las razones generadas por las reglas del motor.

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

El conocimiento aprendido es reutilizado por el Planner Engine y el Decision Engine.

---

## Explanation Engine

Responsable de transformar el conocimiento interno del sistema en explicaciones comprensibles.

Actualmente incluye:

- AdaptiveProfileExplanationService
- RecommendationExplanationService
- PlanningExplanationService
- LearningExplanationService

Estos servicios utilizan el modelo unificado:

- Explanation

De esta manera, la lógica del negocio permanece separada de la presentación de las decisiones al usuario.

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

## ConversationMemoryService

Gestiona el contexto temporal utilizado por la Assistant Layer.

Responsabilidades actuales:

- conservar la última intención;
- conservar la última recomendación;
- conservar el último plan;
- recuperar el contexto conversacional;
- limpiar la memoria cuando sea necesario.

La implementación actual utiliza memoria local y no requiere servicios externos ni APIs de pago.

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

### Planificación

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

### Recomendación

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

### Aprendizaje

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

### Perfil adaptativo

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

## Flujo conversacional

La Assistant Layer funciona como punto de entrada unificado para la interacción conversacional.

```text
Usuario
      │
      ▼
AssistantChatService
      │
      ├──────────────► ConversationMemoryService
      │                       │
      │                       ▼
      │               ConversationContext
      │
      ▼
IntentDetectionService
      │
      ├────────────┬────────────┬────────────┬────────────┐
      ▼            ▼            ▼            ▼            ▼
 Planning    Recommendation   Learning   Explanation   Follow-up
 Workflow       Workflow
      │            │
      └────────────┴──────────────────────────┐
                                             ▼
                                  AssistantChatResponse
```

La memoria permite que una interacción pueda utilizar información generada anteriormente.

Ejemplo:

```text
Usuario
"Planifica mi día"
        │
        ▼
last_plan

Usuario
"¿Qué hago ahora?"
        │
        ▼
last_recommendation

Usuario
"¿Por qué?"
        │
        ▼
last_recommendation

Usuario
"¿Y después?"
        │
        ▼
last_plan + last_recommendation
```

Esto permite mantener conversaciones contextuales básicas sin depender de un modelo de lenguaje externo.

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
- explicaciones;
- asistente conversacional;
- seguimiento contextual de conversaciones.

El endpoint:

```text
POST /assistant/chat
```

constituye la principal interfaz conversacional del sistema y reutiliza los motores existentes mediante la Assistant Layer.

La documentación interactiva de la API se genera automáticamente mediante Swagger.

---

# Testing

La arquitectura fue diseñada para facilitar pruebas unitarias y de integración.

Actualmente existen pruebas para:

- Planner Engine;
- Decision Engine;
- Learning Engine;
- Adaptive Profile;
- servicios de explicación;
- persistencia;
- reglas individuales;
- integración entre motores;
- Workflow Services;
- AssistantChatService;
- IntentDetectionService;
- memoria conversacional;
- flujos conversacionales contextuales.

**83 tests automatizados.**

Los tests permiten validar los motores de forma independiente y comprobar los principales flujos de integración sin depender de la interfaz HTTP.

---

# Estado arquitectónico de v1.0.0

La primera versión estable de AURA integra las siguientes capacidades:

```text
                    AURA
                      │
              Assistant Layer
                      │
          ┌───────────┴───────────┐
          │                       │
Conversation Memory          Workflows
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
           Planner            Decision            Learning
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  │
                           Explanation
                                  │
                                  ▼
                           Adaptive Profile
```

La arquitectura mantiene separados:

- interacción;
- orquestación;
- dominio;
- persistencia;
- aprendizaje;
- explicación;
- memoria conversacional.

Esto permite evolucionar cada capacidad sin acoplarla innecesariamente a las demás.

---

# Visión

AURA no busca ser únicamente un gestor de tareas.

Su objetivo es convertirse en un asistente inteligente capaz de:

- planificar;
- recomendar;
- aprender;
- adaptarse;
- explicar cada decisión que toma;
- mantener contexto durante una conversación.

La interacción con el usuario se realiza mediante una capa conversacional que reutiliza los motores existentes, permitiendo ofrecer una experiencia unificada sin acoplar la interfaz a la lógica del negocio.

La versión v1.0.0 establece una base funcional y explicable sobre la cual pueden incorporarse posteriormente capacidades como memoria por sesión, interfaces adicionales, integraciones externas y modelos de lenguaje opcionales.

El núcleo de AURA permanece funcional sin depender de servicios externos de inteligencia artificial.