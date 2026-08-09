# Changelog

Todas las modificaciones importantes del proyecto serán documentadas en este archivo.

El formato está inspirado en **Keep a Changelog** y las versiones siguen **Semantic Versioning**.

---

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