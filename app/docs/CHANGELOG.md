# Changelog

Todas las modificaciones importantes del proyecto serán documentadas en este archivo.

El formato está inspirado en **Keep a Changelog** y las versiones siguen **Semantic Versioning**.

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

# v0.8.0 — Adaptive Intelligence

Fecha: Agosto 2026

## Added

- Learning Engine.
- Adaptive Profile.
- Adaptive Profile Service.
- Adaptive Planning.
- Adaptive Decision Engine.
- Recommendation History.
- Task Execution.
- Adaptive Profile API.
- Persistencia del perfil adaptativo.

## Changed

- Planner Engine ahora utiliza Adaptive Profile para ajustar automáticamente la duración estimada de las tareas.
- Decision Engine incorpora reglas adaptativas basadas en el comportamiento histórico del usuario.
- La arquitectura se reorganizó para desacoplar aprendizaje, planificación y toma de decisiones.

## Improved

- Explicabilidad de recomendaciones.
- Organización de servicios.
- Arquitectura desacoplada.
- Cobertura de pruebas.

## Testing

- 57 pruebas automatizadas.
- Cobertura de Planner Engine.
- Cobertura de Decision Engine.
- Cobertura de Learning Engine.
- Cobertura de Adaptive Profile.



# Changelog

# v0.9.0

## Added

- AssistantChatService
- IntentDetectionService
- RecommendationWorkflowService
- Conversational endpoint (`/assistant/chat`)
- Conversational planning
- Conversational recommendations
- Conversational learning
- Conversational explanations

## Changed

- Planning logic moved to PlanningWorkflowService
- Recommendation logic moved to RecommendationWorkflowService
- Assistant architecture reorganized
- Improved workflow reuse

## Testing

- Added unit tests for AssistantChatService
- Improved test isolation using mocks

## Architecture

- Introduced Assistant Layer
- Added conversational orchestration