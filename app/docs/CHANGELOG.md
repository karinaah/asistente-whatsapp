# Changelog

Todas las modificaciones importantes del proyecto serán documentadas en este archivo.

El formato está inspirado en **Keep a Changelog** y las versiones siguen **Semantic Versioning**.

---
## v1.3.0

### Added

- Soporte de flexibilidad de tareas mediante los modos `flexible`, `semi_flexible` y `fixed`.
- Replanificación dinámica desde una hora específica del día.
- Nuevo `ReplanningService` para reorganizar tareas pendientes durante el día.
- Soporte de tareas activas con tiempo restante sin modificar su estimación original.
- Nueva intención conversacional `replanning`.
- Nueva intención `active_task_delay` para manejar atrasos en tareas activas.
- Soporte conversacional para frases como:
  - `Reorganiza lo que me queda del día`.
  - `Me faltan 30 minutos`.
  - `Me atrasé`.
- Follow-up contextual para solicitar el tiempo restante cuando el usuario informa un atraso sin indicar duración.
- Creación de tareas urgentes desde Chat con replanificación automática.
- Inferencia de prioridad alta a partir de expresiones como `urgente`, `urgencia` y `prioridad alta`.
- Limpieza del título de reuniones urgentes creadas desde mensajes conversacionales.

### Changed

- La planificación del día actual comienza desde la hora actual en lugar de volver al inicio configurado del día.
- Las tareas futuras ya no se incluyen al planificar o replanificar el día actual.
- Las tareas `fixed` deben respetar exactamente su horario preferido.
- Las tareas `semi_flexible` deben mantenerse dentro de su franja horaria preferida.
- Las tareas `in_progress` tienen prioridad sobre tareas pendientes durante una replanificación.
- Una nueva tarea urgente puede reorganizar lo pendiente sin desplazar automáticamente una tarea ya en progreso.
- La memoria conversacional conserva temporalmente el contexto necesario para completar follow-ups de replanificación.

### Testing

- Se agregaron pruebas para:
  - flexibilidad y restricciones de planificación;
  - replanificación desde hora actual;
  - exclusión de tareas completadas y futuras;
  - tareas activas y tiempo restante;
  - detección de nuevas intenciones conversacionales;
  - follow-ups contextuales;
  - creación y replanificación de tareas urgentes.
- Suite automatizada completa: **129 tests passing**.

### Release

AURA v1.3.0 incorpora replanificación dinámica y adaptación del plan durante el transcurso del día. El asistente puede reaccionar a atrasos, cambios de prioridad y nuevas tareas urgentes, manteniendo las restricciones temporales y el contexto conversacional inmediato.


## v1.2.0

### Added

- Workspaces `trabajo` y `personal` para separar ámbitos de las tareas.
- Tipos de actividad mediante `ActivityType`, incluyendo `deep_work`, `meeting`, `administrative`, `exercise`, `errand`, `study`, `routine`, `rest` y `other`.
- Persistencia de `workspace` y `activity_type` en SQLite.
- Migración compatible con bases existentes de AURA v1.1.x.
- Inferencia automática de `workspace` a partir del lenguaje natural de la tarea.
- Inferencia automática de `activity_type`.
- Sincronización del workspace inferido con el contexto operativo de la tarea.
- Filtros web para visualizar todas las tareas, tareas de trabajo o tareas personales.
- Edición de `workspace` y `activity_type` desde la interfaz web.
- `ActivityTypeRule` para incorporar el tipo de actividad al Decision Engine.
- Nuevo código de recomendación `activity_type_match`.
- `TaskCreationWorkflowService` para centralizar extracción, análisis y persistencia de tareas creadas desde lenguaje natural.
- Nueva intención conversacional `task_creation`.
- Creación de tareas directamente desde Assistant Chat mediante lenguaje natural.

### Changed

- El Decision Engine considera ahora el tipo de actividad como señal adicional al recomendar tareas.
- `AssistantService` reutiliza `TaskCreationWorkflowService` para evitar duplicación del flujo de creación.
- Assistant Chat puede interpretar frases de acción como solicitudes de creación de tareas.
- Trabajo y vida personal utilizan una disponibilidad temporal global compartida.
- Los `busy_blocks` afectan a la planificación independientemente del workspace.
- El workspace organiza y filtra tareas sin crear agendas temporales independientes.
- El análisis automático de tareas incorpora categoría, información temporal, tipo de actividad y workspace.

### Testing

- Se agregaron tests para:
  - inferencia automática de `activity_type`;
  - inferencia automática de `workspace`;
  - sincronización `workspace → context`;
  - `ActivityTypeRule`;
  - disponibilidad global entre tareas personales y de trabajo;
  - creación de tareas desde Assistant Chat;
  - creación conversacional de tareas de trabajo y personales.
- Suite automatizada completa: **99 tests passing**.
- Validación manual del flujo end-to-end:
  - creación de una tarea de trabajo desde Chat;
  - inferencia `workspace = trabajo`;
  - inferencia `activity_type = deep_work`;
  - creación de una tarea personal desde Chat;
  - inferencia `workspace = personal`;
  - inferencia `activity_type = exercise`;
  - persistencia de ambas tareas;
  - visualización en la interfaz web;
  - filtrado correcto por workspace.

### Release

AURA v1.2.0 amplía el modelo de organización y decisión introducido en v1.1.0, permitiendo gestionar explícitamente tareas personales y laborales dentro de una misma planificación diaria.

El foco de esta versión fue incorporar workspaces y tipos de actividad como información estructural de las tareas, utilizar esas señales en el análisis y las recomendaciones, y permitir la creación de tareas mediante lenguaje natural desde Assistant Chat, manteniendo una disponibilidad temporal global y una arquitectura desacoplada y explicable.

---

## v1.1.0

### Added

- Primera interfaz web usable de AURA.
- Vista `Hoy` conectada al `PlanningWorkflowService`.
- Visualización de tareas programadas y no programadas.
- Navegación web entre `Hoy`, `Tareas` y `Chat`.
- Vista completa de gestión de tareas.
- Creación de tareas desde la web.
- Edición de tareas desde la web.
- Completado de tareas desde la web.
- Eliminación de tareas con confirmación.
- Vista web de Chat integrada con `AssistantChatService`.
- Soporte de memoria conversacional y follow-ups desde la interfaz web.
- Archivos estáticos y estilos CSS para la interfaz.
- Estados vacíos para planificación y listado de tareas.
- Nuevas pruebas automatizadas para las rutas web principales.

### Changed

- AURA puede utilizarse durante el flujo principal diario sin depender de Swagger.
- La Vista Hoy reutiliza el Planner y el perfil adaptativo existentes.
- Completar una tarea desde la web actualiza el estado persistido y permite regenerar el plan.
- Las tareas completadas se diferencian visualmente en la Vista Tareas.
- El flujo web reutiliza los servicios y workflows existentes sin duplicar lógica del Core.

### Testing

- Se agregaron tests para:
  - `/web`
  - `/web/tasks`
  - `/web/chat`
- Suite automatizada completa: **88 tests passing**.
- Validación manual completa del flujo:
  - crear tarea;
  - editar tarea;
  - verla reflejada en Hoy;
  - planificar mediante Chat;
  - realizar follow-up contextual;
  - completar tarea;
  - comprobar replanificación;
  - eliminar tarea.

### Release

AURA v1.1.0 transforma el núcleo conversacional estable de v1.0.1 en una aplicación web usable.

El foco de esta versión fue exponer las capacidades ya existentes de planificación, recomendación, aprendizaje y conversación mediante una interfaz simple, manteniendo el Core desacoplado y sin incorporar todavía las capacidades planificadas para versiones posteriores como workspaces, persistencia multiusuario, Google Calendar o WhatsApp.

---

## v1.0.1

### Fixed

- Fixed Planner behavior that could lose available time slots before tasks with a preferred start time.
- Planner now reuses earlier available slots instead of advancing through the day irreversibly.
- Planner now respects task deadlines as scheduling limits.
- Tasks are no longer scheduled after their deadline.
- Improved conversational planning responses to include task names and scheduled times.
- Planning responses are now presented in chronological order.
- Assistant now reports tasks that could not be scheduled.
- Improved singular and plural wording for unscheduled tasks.

### Testing

- Added regression test for preserving earlier available planning slots.
- Added regression test for preventing tasks from being scheduled after their deadline.
- Full automated suite: **85 tests passing**.

### Validation

Manually validated the main conversational flows:

- daily planning;
- task recommendation;
- recommendation explanation;
- contextual follow-ups;
- conversational memory;
- Learning Engine.

Conversational memory remains intentionally temporary and is reset when the application process restarts.

### Release

AURA v1.0.1 is a maintenance release focused on scheduling correctness and improvements discovered during real-world functional testing of v1.0.0.

---

## v1.0.0

### Added

- Conversational memory through `ConversationMemoryService`.
- `ConversationContext` for maintaining temporary assistant state.
- Memory of the last detected intent.
- Memory of the last recommendation.
- Memory of the last generated plan.
- Contextual follow-up support.
- Support for conversational queries such as `¿Y después?`.
- Memory-first explanation flow with persistent history as fallback.
- Planning workflow capable of producing plans and planning decisions in a single execution.

### Changed

- `AssistantChatService` now maintains conversational context between interactions.
- Planning results are stored in conversational memory.
- Recommendations are stored in conversational memory.
- Follow-up requests can reuse previous planning and recommendation context.
- Recommendation explanations prioritize conversational memory before querying persistent history.
- `PlannerService` exposes plan and decision results without executing the planner twice.

### Testing

- Added tests for `ConversationMemoryService`.
- Added conversational memory integration tests.
- Added follow-up intent detection tests.
- Added contextual conversation tests.
- Added plan and recommendation memory tests.
- Full automated suite: **83 tests passing**.

### Release

AURA v1.0.0 introduces the first stable conversational version of the assistant.

The system can now plan, recommend, learn, adapt, explain its decisions, and maintain basic conversational context without depending on paid external AI services.

---

## v0.9.0

### Added

- `AssistantChatService`.
- `IntentDetectionService`.
- `RecommendationWorkflowService`.
- Conversational endpoint (`/assistant/chat`).
- Conversational planning.
- Conversational recommendations.
- Conversational learning.
- Conversational explanations.

### Changed

- Planning logic moved to `PlanningWorkflowService`.
- Recommendation logic moved to `RecommendationWorkflowService`.
- Assistant architecture reorganized.
- Improved workflow reuse.

### Testing

- Added unit tests for `AssistantChatService`.
- Improved test isolation using mocks.

### Architecture

- Introduced Assistant Layer.
- Added conversational orchestration.

---

## v0.8.0 — Adaptive Intelligence

Fecha: Agosto 2026

### Added

- Learning Engine.
- Adaptive Profile.
- Adaptive Profile Service.
- Adaptive Planning.
- Adaptive Decision Engine.
- Recommendation History.
- Task Execution.
- Adaptive Profile API.
- Persistencia del perfil adaptativo.

### Changed

- Planner Engine ahora utiliza Adaptive Profile para ajustar automáticamente la duración estimada de las tareas.
- Decision Engine incorpora reglas adaptativas basadas en el comportamiento histórico del usuario.
- La arquitectura se reorganizó para desacoplar aprendizaje, planificación y toma de decisiones.

### Improved

- Explicabilidad de recomendaciones.
- Organización de servicios.
- Arquitectura desacoplada.
- Cobertura de pruebas.

### Testing

- 57 pruebas automatizadas.
- Cobertura de Planner Engine.
- Cobertura de Decision Engine.
- Cobertura de Learning Engine.
- Cobertura de Adaptive Profile.