# AURA Roadmap

## Estado actual

### Versión

v0.8.0 — Adaptive Intelligence

### Estado

Desarrollo activo.

### Capacidades principales

- Planner Engine.
- Decision Engine.
- Learning Engine.
- Adaptive Profile persistente.
- Planificación adaptativa.
- Recomendaciones adaptativas.
- API REST.
- Suite de pruebas automatizadas (57 tests).

---




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

# Sprint 6 ✅ Finalizado

## Objetivos

- Registrar ejecuciones reales de tareas.
- Comparar duración estimada y duración real.
- Persistir ejecuciones.
- Analizar precisión de estimaciones.
- Generar insights por categoría.
- Analizar productividad según estado humano.
- Detectar métricas básicas de hábitos.
- Crear arquitectura modular de aprendizaje.

## Resultado

AURA puede:

- Registrar cómo se ejecutó realmente una tarea.
- Comparar estimaciones con duración real.
- Detectar subestimaciones y sobreestimaciones.
- Agrupar patrones por categoría.
- Analizar diferencias según energía.
- Calcular métricas básicas de hábitos.
- Generar insights estructurados mediante LearningService.
- Construir la base del Learning Engine.

## Sprint 7 ✅ Finalizado

### Adaptive Intelligence

### Objetivos

- Adaptive Profile.
- Persistencia del perfil.
- Planner adaptativo.
- Decision Engine adaptativo.
- Integración del Learning Engine.
- Reutilización del aprendizaje.
- Persistencia del conocimiento del usuario.

### Resultado

AURA ahora es capaz de:

- aprender del comportamiento del usuario;
- consolidar ese aprendizaje en un Adaptive Profile;
- persistir dicho perfil;
- reutilizar el perfil para mejorar automáticamente la planificación;
- reutilizar el perfil para mejorar las recomendaciones.

## Sprint 8

### Conversational Intelligence

### Objetivo

Permitir que AURA explique su razonamiento y su aprendizaje.

### Funcionalidades

- Explicar recomendaciones.
- Explicar planificación.
- Explicar el Adaptive Profile.
- Mostrar evolución del aprendizaje.
- Comparar perfiles.
- Mostrar nivel de confianza.
- Mejorar las respuestas conversacionales.


---

# Visión hacia v1.0

Antes de la versión 1.0 el proyecto buscará completar:

- Integraciones externas.
- Evidencias automáticas de cumplimiento.
- Simulación de planificación.
- Inteligencia conversacional.
- Evolución del Adaptive Profile.