# AURA — Roadmap

## Estado actual

### Completado

- Motor inicial de planificación.
- Priorización de tareas.
- Manejo de deadlines.
- Preferencias horarias.
- Bloques ocupados.
- Descansos.
- Reducción de fragmentación.
- Timeline diario.
- Separación de ScoringEngine.
- ScoreBreakdown.
- Factories de tests.
- Tests unitarios e integración.
- Contextos de trabajo y vida personal.
- Filtrado de planificación por contexto.

## Fase 1 — MVP funcional

Objetivo: convertir el motor actual en una aplicación utilizable.

### Pendiente

- Completar soporte de contexto en modelo, repositorio, servicios y API.
- CRUD de tareas.
- Persistencia estable de tareas.
- Estados de tarea:
  - pendiente;
  - programada;
  - en progreso;
  - completada;
  - cancelada.
- Endpoint para generar un plan diario.
- Endpoint para marcar una tarea como completada.
- Validaciones y manejo de errores.
- Tests de API y persistencia.
- Documentación básica de instalación y uso.

## Fase 2 — Experiencia por espacios

Objetivo: separar claramente las distintas áreas de la vida del usuario.

- Diseñar entidad Workspace.
- Migrar gradualmente desde TaskContext.
- Crear workspaces configurables.
- Horarios por workspace.
- Descansos por workspace.
- Preferencias por workspace.
- Vista Todo, Trabajo y Personal.
- Cambio rápido entre espacios.


## Fase 3 — Asistente de decisión ✅

Objetivo: ayudar al usuario a decidir, no solo organizar.

### Completado

- Función "¿Qué hago ahora?"
- Recomendación de la siguiente tarea.
- Explicación de cada recomendación.
- Motor de reglas.
- Contexto del usuario.
- Recomendaciones basadas en energía.
- Recomendaciones basadas en enfoque.
- Penalización por estrés.
- Historial de recomendaciones.

### Pendiente

- Identificación de tareas posponibles.
- Alertas de sobrecarga.
- Replanificación sugerida.
- Confirmación del usuario antes de cambios importantes.

## Fase 4 — Aprendizaje personal

Objetivo: adaptar la planificación al comportamiento real.

### Base implementada

- Persistencia del estado humano.
- Historial de recomendaciones.

### Próximos objetivos

- Registrar duración estimada y duración real.
- Aprender precisión de estimaciones.
- Detectar horarios de mayor productividad.
- Aprender tolerancia a bloques largos.
- Detectar patrones de postergación.
- Ajustar recomendaciones según historial.

## Fase 5 — Integraciones

Objetivo: reducir trabajo manual sin hacer obligatorio ningún proveedor.

- Calendario.
- Importación de actividades físicas.
- Garmin, cuando exista una vía viable.
- Apple Health.
- Google Health Connect.
- Fitbit u otros proveedores.
- GitHub.
- Correo y herramientas de comunicación.

Todas las integraciones deberán ser opcionales y desacopladas del dominio central.

## Fase 6 — Evidencias de cumplimiento

Objetivo: detectar automáticamente cuándo una tarea fue realizada.

- Modelo ActivityRecord.
- CompletionMatcher.
- Coincidencia por tipo, horario y duración.
- Confirmación ante coincidencias ambiguas.
- Completar ejercicio desde actividad registrada.
- Posibles evidencias futuras:
  - eventos de calendario;
  - commits;
  - sesiones de estudio;
  - documentos entregados.

## Fase 7 — Simulación y protección del tiempo

Objetivo: ayudar a evaluar decisiones futuras.

- Simular nuevos compromisos.
- Mostrar horas añadidas.
- Detectar colisiones futuras.
- Mostrar tareas desplazadas.
- Estimar impacto en objetivos.
- Detectar sacrificios recurrentes.
- Recomendar aceptar, rechazar o renegociar.

## Fuera del MVP

Estas capacidades no deben retrasar la primera versión:

- integración directa con relojes;
- adaptación automática por sueño o estrés;
- replanificación autónoma;
- simulación avanzada;
- modelo predictivo;
- inteligencia conversacional completa.




# Roadmap

## Sprint 1 ✅ Finalizado

### Objetivos

- Extracción de tareas mediante IA.
- Modelado del dominio.
- Parser temporal.
- API inicial.

### Estado

Completado.

## Sprint 2 ✅ Finalizado

### Objetivos

- Diseño del Planner.
- Algoritmo de planificación.
- Timeline.
- Bloques ocupados.
- Descansos.
- Preferencias horarias.
- Sistema de scoring.

### Estado

Completado.

## Sprint 3 ✅ Finalizado

### Objetivos

- Persistencia con SQLite.
- Integración con SQLAlchemy.
- Repository Pattern.
- CRUD completo de tareas.
- Integración Planner + Base de datos.
- Separación entre dominio y persistencia.
- Filtrado de tareas planificables.
- Validación funcional del planner.

### Resultado

AURA puede:

- Crear tareas.
- Persistirlas.
- Editarlas.
- Completarlas.
- Consultarlas.
- Recuperarlas desde la base de datos.
- Generar un plan automáticamente usando únicamente tareas pendientes.


# Sprint 4 ✅ Finalizado

## Objetivos

- Motor de decisión.
- Endpoint `/decision/recommend`.
- Recommendation.
- RecommendationReason.
- Score por reglas.
- Explicación de recomendaciones.
- DecisionEngine desacoplado.
- Sistema extensible de reglas.

## Resultado

AURA puede:

- Recomendar la siguiente tarea.
- Explicar por qué fue recomendada.
- Considerar prioridad, deadlines, contexto y tiempo disponible.
- Construir recomendaciones mediante reglas independientes.


# Sprint 5 ✅ Finalizado

## Objetivos

- HumanState.
- Recomendaciones sensibles al estado del usuario.
- Persistencia del estado humano.
- Historial de recomendaciones.
- Resúmenes naturales.

## Resultado

AURA ahora puede:

- Considerar energía, enfoque y estrés al recomendar tareas.
- Recuperar automáticamente el último estado humano registrado.
- Generar explicaciones naturales de las recomendaciones.
- Guardar el historial completo de recomendaciones.
- Persistir el estado humano y reutilizarlo en futuras decisiones.

## Nuevas reglas

- EnergyRule
- FocusRule
- StressRule

## Nuevos componentes

- RecommendationSummaryService
- HumanStateService
- RecommendationHistoryService