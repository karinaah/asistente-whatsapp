# AURA — Decision Engine

## Propósito

El Decision Engine ayuda a AURA a responder una pregunta principal:

> ¿Cuál es la mejor acción que el usuario puede realizar ahora?

El planner determina qué tareas caben en el tiempo disponible.

El Decision Engine evalúa esas tareas y recomienda una acción, junto con las razones que justifican la recomendación.

## Principios

1. Las recomendaciones deben ser explicables.
2. El usuario conserva siempre el control.
3. Las reglas deben poder evolucionar de forma independiente.
4. Las integraciones externas aportan información, pero no deben controlar automáticamente el calendario.
5. AURA debe funcionar aunque el usuario no tenga dispositivos o servicios conectados.
6. Los pesos de las reglas deben estar centralizados y ser configurables en el futuro.
7. Una recomendación debe representar la mejor decisión disponible, no solamente la tarea más urgente.

## Flujo general

```text
Tareas persistidas
        ↓
PlannerService
        ↓
PlanningResponse
        ↓
DecisionContext
        ↓
DecisionEngine
        ↓
Decision Rules
        ↓
Recommendation