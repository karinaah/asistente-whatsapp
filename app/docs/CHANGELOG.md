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

## v0.9.0

### Added

- Explanation Engine.
- PlanningExplanationService.
- RecommendationExplanationService.
- LearningExplanationService.
- AdaptiveProfileExplanationService.
- PlanningWorkflowService.
- Endpoint para explicar la planificación.
- Endpoint para explicar recomendaciones.
- Endpoint para explicar el aprendizaje.
- Endpoint para explicar el perfil adaptativo.

### Changed

- Refactorización del Planner para producir `PlanningDecision`.
- Refactorización del flujo de planificación mediante `PlanningWorkflowService`.
- Consolidación de un modelo unificado `Explanation`.

### Improved

- Arquitectura basada en modelos explicables.
- Reutilización entre Planner y API.
- Desacoplamiento entre motores y presentación.
- Documentación de arquitectura completamente reescrita.

### Tests

- 64 tests passing.