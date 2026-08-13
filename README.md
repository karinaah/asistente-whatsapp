![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green)
![Tests](https://img.shields.io/badge/tests-83%20passing-success)
![Version](https://img.shields.io/badge/version-v1.0.0-orange)

# AURA

AURA es un asistente inteligente de productividad que planifica, recomienda, aprende, se adapta y explica sus decisiones mediante una interfaz conversacional.

Su arquitectura está basada en motores desacoplados, reglas explicables, aprendizaje adaptativo y memoria conversacional, priorizando mantenibilidad, extensibilidad y facilidad de prueba.

AURA v1.0.0 funciona sin depender de servicios externos de inteligencia artificial ni APIs de pago.

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
- Memoria conversacional temporal.
- Seguimiento contextual de conversaciones.
- Reutilización del último plan y recomendación durante la conversación.
- Soporte para consultas contextuales como `¿Y después?`.

---

# Arquitectura

La arquitectura de AURA está compuesta por una capa conversacional que orquesta varios motores especializados.

Sus principales componentes son:

- Assistant Layer
- Conversation Memory
- Planner Engine
- Decision Engine
- Learning Engine
- Explanation Engine
- Adaptive Profile
- Workflow Services
- Repository Layer

Cada componente tiene responsabilidades definidas y se comunica mediante modelos explícitos.

La lógica de negocio permanece desacoplada de FastAPI, SQLAlchemy y de proveedores externos.

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

La arquitectura completa se encuentra documentada en `docs/architecture.md`.

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
- duración estimada;
- conocimiento del Adaptive Profile.

El resultado es un plan explicable y determinista.

El Planner también puede producir el plan y sus decisiones explicables dentro de una misma ejecución, evitando cálculos duplicados.

---

## Decision Engine

Determina cuál es la mejor tarea para realizar en un momento determinado.

Cada recomendación se construye mediante reglas independientes que generan:

- puntuación;
- razones;
- explicación.

Actualmente puede considerar factores como:

- prioridad;
- deadlines;
- contexto;
- tiempo disponible;
- energía;
- enfoque;
- estrés;
- preferencias horarias;
- aprendizaje adaptativo.

---

## Learning Engine

Analiza las ejecuciones reales registradas para detectar patrones de comportamiento.

Actualmente aprende sobre:

- precisión de las estimaciones;
- comportamiento por categoría;
- productividad según energía;
- hábitos generales.

El conocimiento obtenido puede consolidarse en el Adaptive Profile y reutilizarse en decisiones futuras.

---

## Explanation Engine

Transforma las decisiones internas de AURA en explicaciones comprensibles.

Actualmente incluye explicaciones para:

- recomendaciones;
- planificación;
- aprendizaje;
- Adaptive Profile.

La explicación permanece separada de la lógica que toma la decisión.

---

# Adaptive Profile

El Adaptive Profile consolida el conocimiento generado por el Learning Engine en un perfil persistente.

Representa información aprendida sobre el comportamiento del usuario y es reutilizado por:

- Planner Engine;
- Decision Engine.

Esto permite que planificación y recomendación utilicen una fuente compartida de conocimiento adaptativo.

---

# Assistant Layer

La Assistant Layer proporciona una interfaz conversacional unificada sobre los motores existentes.

Actualmente puede reconocer intenciones relacionadas con:

- planificación;
- recomendaciones;
- aprendizaje;
- explicaciones;
- seguimiento contextual.

El principal punto de entrada es:

```text
POST /assistant/chat
```

Ejemplo de interacción:

```text
Usuario: Planifica mi día
AURA: genera el plan

Usuario: ¿Qué hago ahora?
AURA: genera una recomendación

Usuario: ¿Por qué?
AURA: explica la recomendación

Usuario: ¿Y después?
AURA: utiliza el contexto del plan y la recomendación
```

---

# Memoria conversacional

AURA v1.0.0 incorpora memoria conversacional temporal mediante `ConversationMemoryService`.

Actualmente puede conservar:

- última intención detectada;
- última recomendación;
- último plan generado.

Esto permite reutilizar contexto entre mensajes consecutivos.

La memoria actual reside durante la ejecución de la aplicación. Todavía no representa memoria persistente por usuario ni sesiones conversacionales independientes.

Cuando determinada información no se encuentra disponible en memoria, algunos flujos pueden recurrir a información persistida como fallback.

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

## Arquitectura

- Repository Pattern
- Dependency Injection
- Service Layer
- Domain Models
- Rule-based Engines
- Explainable Models
- Workflow Services

---

# Integraciones

El núcleo actual de AURA no requiere integraciones externas ni servicios de IA de pago.

Las integraciones futuras serán opcionales y podrán incluir:

- Google Calendar;
- WhatsApp;
- GitHub;
- Apple Health;
- Garmin;
- modelos de lenguaje.

El objetivo arquitectónico es que las integraciones externas complementen el sistema sin convertirse en una dependencia del núcleo.

---

# Instalación

Clonar el repositorio:

```bash
git clone https://github.com/karinaah/asistente-whatsapp.git
cd AURA
```

Crear un entorno virtual:

```bash
python -m venv .venv
```

Activarlo en Windows:

```bash
.venv\Scripts\activate
```

Activarlo en Linux o macOS:

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

La documentación interactiva de Swagger estará disponible en:

```text
http://127.0.0.1:8000/docs
```

---

# Tests

Ejecutar toda la suite:

```bash
pytest -v
```

Estado de v1.0.0:

- 83 tests automatizados.
- Tests unitarios.
- Tests de integración.
- Tests de persistencia.
- Tests de reglas.
- Tests de motores.
- Tests de Workflow Services.
- Tests de memoria conversacional.
- Tests de flujos conversacionales.
- Cobertura de Planner, Decision, Learning, Explanation, Adaptive Profile y Assistant.

---

# API

La API REST permite utilizar las principales capacidades de AURA.

Incluye casos de uso para:

- gestión de tareas;
- planificación automática;
- recomendaciones;
- historial de recomendaciones;
- estado humano;
- registro de ejecuciones;
- aprendizaje;
- Adaptive Profile;
- explicaciones;
- Assistant Chat.

La Assistant Layer expone el flujo conversacional principalmente mediante:

```text
POST /assistant/chat
```

Toda la documentación interactiva de los endpoints está disponible mediante Swagger.

---

# Estado del proyecto

Versión actual: **v1.0.0**

Estado:

- ✅ Planner Engine
- ✅ Decision Engine
- ✅ Learning Engine
- ✅ Explanation Engine
- ✅ Adaptive Profile
- ✅ Workflow Services
- ✅ Assistant Layer
- ✅ Conversational Memory
- ✅ Contextual Follow-ups
- ✅ Persistencia
- ✅ Suite automatizada de tests

AURA v1.0.0 representa la primera versión estable del núcleo del asistente.

---

# Roadmap

Después de v1.0.0, las posibles líneas de evolución incluyen:

- memoria conversacional por sesión y usuario;
- contexto conversacional persistente;
- referencias contextuales más avanzadas;
- explicaciones conversacionales más naturales;
- mejoras del aprendizaje adaptativo;
- nuevas reglas de planificación y recomendación;
- integración opcional con modelos de lenguaje;
- Google Calendar;
- WhatsApp;
- otras integraciones externas;
- ampliación continua de la cobertura de pruebas.

El roadmap completo se encuentra en `docs/roadmap.md`.

---

# Limitaciones actuales

AURA v1.0.0 establece el núcleo funcional del proyecto, pero todavía existen capacidades previstas para versiones posteriores.

Entre ellas:

- la memoria conversacional no es persistente;
- todavía no existe aislamiento de memoria por usuario o sesión;
- el reconocimiento de intención está basado en reglas;
- las conversaciones contextuales soportadas son todavía limitadas;
- las integraciones externas no forman parte del núcleo v1.0.0;
- no se utiliza un modelo de lenguaje para generar o interpretar conversaciones.

Estas limitaciones permiten mantener la primera versión determinista, explicable y completamente funcional sin servicios externos.

---

# Filosofía del proyecto

AURA busca construir un asistente que ayude a tomar mejores decisiones, no simplemente un gestor de tareas.

Cada decisión debe ser:

- explicable;
- transparente;
- reproducible;
- basada en información disponible y, cuando corresponda, en el comportamiento aprendido del usuario.

El objetivo no es reemplazar las decisiones del usuario, sino ofrecer recomendaciones fundamentadas que evolucionen con el tiempo.

AURA está diseñado para que nuevas capacidades puedan incorporarse progresivamente sin comprometer la claridad ni la independencia de su núcleo.