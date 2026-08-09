![Python](https://img.shields.io/badge/Python-3.11-blue)

![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)

![Tests](https://img.shields.io/badge/tests-74%20passing-success)

![Version](https://img.shields.io/badge/version-v0.9.0-orange)

# AURA

AURA es un asistente inteligente de productividad que planifica, recomienda, aprende y explica sus decisiones mediante una interfaz conversacional.

Su arquitectura está basada en motores desacoplados, reglas explicables y aprendizaje adaptativo, priorizando mantenibilidad, extensibilidad y facilidad de prueba.
---

## Características

- Interfaz conversacional mediante Assistant Chat.
- Detección automática de intención.
- Planificación automática de tareas.
- Priorización basada en reglas.
- Gestión de deadlines.
- Preferencias horarias.
- Contextos de trabajo y personal.
- Recomendación de la siguiente tarea.
- Explicación de recomendaciones.
- Historial de recomendaciones.
- Registro de ejecuciones reales.
- Learning Engine.
- Perfil adaptativo persistente.
- Ajuste automático de estimaciones.
- Planificación adaptativa.
- Explicación de la planificación.
- Explicación del aprendizaje.
- Explicación del perfil adaptativo.

---

## Arquitectura

La arquitectura de AURA está compuesta por una capa conversacional que orquesta varios motores especializados.

Actualmente incluye:

- Assistant Layer
- Planner Engine
- Decision Engine
- Learning Engine
- Explanation Engine

Cada motor tiene una responsabilidad única y se comunica mediante modelos de dominio explícitos.

La lógica de negocio permanece desacoplada de FastAPI, SQLAlchemy y de cualquier proveedor externo.


---

# Motores

## Planner Engine

Genera automáticamente un plan diario considerando:

- prioridad;
- deadlines;
- horarios preferidos;
- bloques ocupados;
- descansos;
- contexto;
- duración estimada.

El resultado es un plan completamente explicable y determinista.

---

## Decision Engine

Determina cuál es la mejor tarea para realizar en un momento determinado.

Cada recomendación se construye mediante reglas independientes que generan:

- puntuación;
- razones;
- explicación en lenguaje natural.

---

## Learning Engine

Analiza las ejecuciones reales registradas por el usuario para detectar patrones de comportamiento.

Actualmente aprende:

- precisión de las estimaciones;
- comportamiento por categoría;
- productividad según energía;
- hábitos generales.

---

## Adaptive Profile 

Consolida el aprendizaje generado por el Learning Engine en un único perfil persistente.

Este perfil representa el conocimiento que AURA tiene sobre el usuario y es utilizado por:

- Planner Engine;
- Decision Engine.

De esta forma ambos motores utilizan exactamente la misma información aprendida.

---

# Tecnologías

El núcleo de AURA está construido con tecnologías modernas del ecosistema Python.

## Backend

- Python 3.11
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic

## Testing

- Pytest

## Arquitectura

- Repository Pattern
- Dependency Injection
- Service Layer
- Domain Models
- Rule-based Engines

## Integraciones

Actualmente todas las integraciones son opcionales.

Las próximas integraciones consideradas incluyen:

- Google Calendar
- WhatsApp
- GitHub
- Apple Health
- Garmin


---

# Instalación

Clonar el repositorio:

```bash
git clone https://github.com/TU_USUARIO/AURA.git

cd AURA
```

Crear un entorno virtual:

```bash
python -m venv .venv
```

Activarlo:

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```


---

# Ejecutar

Iniciar el servidor:

```bash
uvicorn app.main:app --reload
```

Documentación Swagger:

```
http://127.0.0.1:8000/docs
```


---

# Tests

Ejecutar toda la suite:

```bash
pytest -v
```

Estado actual:

- 74 tests automáticos.
- Tests unitarios.
- Tests de integración.
Cobertura de:

- Planner Engine
- Decision Engine
- Learning Engine
- Explanation Engine
- Assistant Layer
- Workflows
- Persistencia

---

# API

La API REST permite gestionar tareas, generar planificación, obtener recomendaciones y administrar el aprendizaje adaptativo.

Entre los principales endpoints se encuentran:

- Gestión de tareas.
- Planificación automática.
- Recomendaciones.
- Historial de recomendaciones.
- Registro de ejecuciones.
- Adaptive Profile.
- Assistant Chat.

Toda la documentación interactiva está disponible mediante Swagger.


---

## Estado del proyecto

Versión actual: **v0.9.0**
Objetivo actual: alcanzar la primera versión estable (v1.0.0) mediante la incorporación de memoria conversacional, integración con modelos de lenguaje e integraciones externas.
Estado del desarrollo:


✅ Planner Engine

✅ Decision Engine

✅ Learning Engine

✅ Explanation Engine

✅ Assistant Layer

🚧 Sprint 10

---

# Roadmap

Las próximas versiones estarán enfocadas en:

- mejorar las explicaciones del aprendizaje;
- enriquecer el Adaptive Profile;
- memoria conversacional;
- integración con LLM;
- contexto persistente;
- integraciones externas;
- optimización del aprendizaje adaptativo.
- ampliar las integraciones externas;
- continuar aumentando la cobertura de pruebas.

El roadmap completo se encuentra en `docs/roadmap.md`.


---

# Licencia

Este proyecto se encuentra actualmente en desarrollo.

La licencia será definida antes de la primera versión estable (v1.0.0).


---

# Filosofía del proyecto

AURA busca construir un asistente que ayude a tomar mejores decisiones, no simplemente un gestor de tareas.

Cada recomendación debe ser:

- explicable;
- transparente;
- reproducible;
- basada en el comportamiento real del usuario.

El objetivo no es reemplazar las decisiones del usuario, sino ofrecer recomendaciones fundamentadas que evolucionen con el tiempo.


                    AURA

            Assistant Layer
                    │
        Intent Detection Service
                    │
      ┌─────────────┼─────────────┐
      ▼             ▼             ▼
 Planner      Recommendation   Learning
                    │
                    ▼
             Explanation Engine