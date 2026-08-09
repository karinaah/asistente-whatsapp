# AURA

AURA es un asistente inteligente de productividad que planifica tareas, recomienda qué hacer en cada momento y aprende del comportamiento del usuario para mejorar automáticamente sus futuras decisiones.

Su arquitectura está basada en motores desacoplados, reglas explicables y aprendizaje adaptativo, priorizando transparencia, mantenibilidad y facilidad de prueba.

## Tecnologías

- Python 3.11
- FastAPI
- OpenAI
- WhatsApp Cloud API
- Google Calendar API

# AURA

## ¿Qué es AURA?

## Características

## Arquitectura

## Motores

## Instalación

## Ejecutar

## Tests

## API

## Roadmap

## Licencia

## Características

- Planificación automática de tareas.
- Priorización basada en reglas.
- Gestión de deadlines.
- Preferencias horarias.
- Contextos (Trabajo / Personal).
- Recomendación de la siguiente tarea.
- Explicación de cada recomendación.
- Historial de recomendaciones.
- Registro de ejecuciones reales.
- Aprendizaje adaptativo.
- Perfil adaptativo persistente.
- Ajuste automático de estimaciones.
- Recomendaciones adaptativas.


## Arquitectura

AURA está organizado en cuatro motores independientes:

- Planner Engine
- Decision Engine
- Learning Engine
- Adaptive Profile Service

Cada componente tiene una responsabilidad única y se comunica mediante modelos de dominio bien definidos.