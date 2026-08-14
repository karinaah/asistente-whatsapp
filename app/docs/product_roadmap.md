# AURA — Product Roadmap

## 1. Visión del producto

AURA es un **asistente personal inteligente de planificación** cuyo objetivo es ayudar al usuario no solamente a registrar tareas, sino también a decidir:

* qué tiene que hacer;
* qué debería hacer ahora;
* cuándo conviene realizar cada actividad;
* cómo organizar su día;
* y cómo reorganizarlo cuando las circunstancias cambian.

La visión de AURA no es convertirse simplemente en otro gestor de tareas.

El objetivo de largo plazo es construir un asistente capaz de comprender el contexto del usuario, organizar su tiempo, aprender de su comportamiento y acompañar la ejecución de sus actividades de forma progresivamente más natural y autónoma.

AURA debería evolucionar hasta poder:

* comprender tareas expresadas mediante lenguaje natural;
* organizar actividades según tiempo, prioridad, contexto y restricciones;
* recomendar la mejor siguiente acción;
* explicar por qué realiza una recomendación;
* aprender del comportamiento real del usuario;
* ajustar progresivamente sus decisiones;
* coordinar actividades personales y laborales;
* recordar información relevante entre interacciones;
* reorganizar el día cuando cambien las circunstancias;
* comunicarse mediante web, WhatsApp y voz;
* integrarse con calendarios y otras fuentes de disponibilidad;
* y, eventualmente, automatizar determinadas decisiones de planificación.

El desarrollo debe ser incremental, manteniendo un **núcleo estable, explicable y testeado en cada versión**.

---

# 2. Estado actual

## v1.0.1 — AURA conversacional estable

**Estado: cerrada**

AURA v1.0.1 constituye el baseline estable actual del proyecto.

Esta versión consolida el trabajo realizado desde las primeras versiones del Planner hasta la incorporación de inteligencia adaptativa, conversación y memoria contextual.

AURA actualmente cuenta con un sistema funcional de:

```text
Gestión de tareas
        ↓
Planner Engine
        ↓
Decision Engine
        ↓
Explanation Engine
        ↓
Learning Engine
        ↓
Adaptive Profile
        ↓
Assistant Layer
        ↓
Conversation Memory
```

---

## 3. Capacidades actuales

### Gestión de tareas

AURA permite administrar las tareas utilizadas posteriormente por los motores de planificación y decisión.

El sistema puede trabajar con información como:

* nombre de la tarea;
* duración;
* prioridad;
* deadline;
* contexto;
* horario preferido;
* estado;
* categoría;
* y otras características necesarias para planificación y aprendizaje.

---

### Planner Engine

El Planner es capaz de construir planes diarios considerando:

* horario disponible;
* duración de las tareas;
* prioridad;
* deadlines;
* horarios preferidos;
* bloques ocupados;
* descansos;
* contexto;
* y disponibilidad existente.

El Planner diferencia entre:

```text
scheduled_tasks
unscheduled_tasks
```

y mantiene las tareas programadas en orden cronológico.

A partir de v1.0.1, además:

* preserva espacios libres anteriores cuando existe una tarea con horario preferido;
* reutiliza correctamente esos espacios;
* evita avanzar irreversiblemente por el día;
* utiliza los deadlines como límites reales de planificación;
* y no agenda tareas después de su fecha límite.

---

### Decision Engine

AURA puede evaluar el plan y recomendar qué actividad conviene realizar.

Las decisiones pueden considerar factores como:

* tarea actualmente activa;
* prioridad;
* deadline;
* deadline vencido;
* horario preferido;
* tiempo disponible;
* contexto;
* energía;
* foco;
* estrés;
* y perfil adaptativo.

Esto permite pasar de:

> “Estas son tus tareas.”

a:

> “Esto es lo que tiene más sentido que hagas ahora.”

---

### Explanation Engine

Las recomendaciones no son completamente opacas.

AURA puede generar razones asociadas a sus decisiones y transformarlas en explicaciones naturales.

Por ejemplo:

> “Te recomiendo esta tarea porque está programada para este momento, tiene prioridad alta y coincide con tu nivel actual de energía.”

La explicabilidad continuará siendo un principio central del producto en versiones futuras.

---

### Learning Engine

AURA ya cuenta con una primera arquitectura de aprendizaje basada en el comportamiento observado.

Actualmente puede analizar:

* ejecución de tareas;
* diferencias entre duración estimada y real;
* comportamiento por categorías;
* patrones básicos de productividad;
* hábitos;
* y estados humanos asociados a la ejecución.

---

### Adaptive Profile

El aprendizaje puede consolidarse en un perfil adaptativo persistente.

Este perfil puede ser utilizado nuevamente por:

* Planner Engine;
* Decision Engine;
* y otros servicios adaptativos.

Por ejemplo, AURA puede ajustar la duración esperada de una tarea utilizando comportamiento histórico en lugar de depender exclusivamente de la estimación inicial.

---

### Assistant Layer

AURA cuenta con una capa conversacional que permite interactuar con los motores existentes mediante lenguaje natural.

Actualmente puede reconocer flujos asociados a:

* planificación;
* recomendación;
* aprendizaje;
* explicación;
* follow-ups;
* y consultas desconocidas.

El endpoint conversacional principal es:

```text
/assistant/chat
```

---

### Memoria conversacional

Desde v1.0.0 AURA mantiene contexto temporal de conversación.

Puede recordar:

* última intención;
* última recomendación;
* último plan generado.

Esto permite conversaciones como:

> “¿Qué debería hacer ahora?”

y posteriormente:

> “¿Por qué?”

o:

> “¿Y después?”

sin tener que reconstruir todo el contexto desde cero.

### Limitación actual

La memoria conversacional es **intencionalmente temporal**.

Actualmente vive durante el proceso de ejecución de la aplicación y se reinicia cuando el proceso se detiene.

La persistencia de memoria será abordada en una versión posterior.

---

# 4. Calidad del baseline

AURA v1.0.1 cierra con:

```text
85 tests automatizados pasando
```

Además, se validaron manualmente los principales flujos conversacionales:

* planificación diaria;
* recomendación de tareas;
* explicación de recomendaciones;
* follow-ups contextuales;
* memoria conversacional;
* Learning Engine.

Por lo tanto, **v1.0.1 debe considerarse una versión cerrada**.

Las siguientes versiones deben construirse sobre este baseline y no reconstruir funcionalidades que ya forman parte del núcleo estable.

---

# 5. Roadmap general

La evolución acordada del producto es:

```text
v1.0.1
AURA conversacional estable
        ↓
v1.1
AURA usable
        ↓
v1.2
Trabajo + Personal
        ↓
v1.3
Día dinámico
        ↓
v1.4
Persistencia personal
        ↓
v1.5
Google Calendar
        ↓
v1.6
Interfaces naturales
        ↓
v1.7
Automatización y aprendizaje avanzado
```

Cada versión debe resolver un problema concreto antes de avanzar a la siguiente.

---

# 6. v1.1 — AURA usable

## Objetivo

Transformar el backend inteligente actual en una aplicación que pueda utilizarse realmente durante el día.

La prioridad de esta versión **no es agregar más inteligencia**.

AURA ya puede planificar, recomendar, explicar, conversar y aprender.

Ahora necesitamos poder **usar esas capacidades cómodamente**.

---

## App web

Construir la primera interfaz web funcional de AURA.

La interfaz debe priorizar:

* simplicidad;
* claridad;
* funcionalidad;
* rapidez de uso.

No necesitamos todavía construir una aplicación visualmente compleja.

---

## Vista Hoy

Será la vista central de AURA.

Debe responder rápidamente:

> “¿Cómo está organizado mi día?”

Debería permitir visualizar:

* fecha actual;
* tareas planificadas;
* horarios;
* tarea actual;
* siguiente tarea;
* tareas completadas;
* tareas que no pudieron programarse.

---

## Gestión de tareas

El usuario debe poder administrar tareas sin utilizar Swagger.

Como mínimo:

* crear;
* visualizar;
* editar;
* completar;
* eliminar.

---

## Chat

La interfaz debe exponer las capacidades actuales de:

```text
/assistant/chat
```

permitiendo conversaciones como:

> “Organiza mi día.”

> “¿Qué debería hacer ahora?”

> “¿Y después?”

> “¿Por qué?”

> “¿Qué has aprendido de mí?”

---

## Completar tareas

Las tareas deben poder marcarse como completadas directamente desde la interfaz.

Esta acción será especialmente importante para las siguientes versiones porque alimentará:

* historial de ejecución;
* aprendizaje;
* replanificación;
* seguimiento;
* rutinas;
* notificaciones.

---

## Criterio de cierre v1.1

AURA v1.1 estará terminada cuando sea posible utilizar el flujo principal del producto durante un día normal **sin depender de Swagger como interfaz de uso**.

---

# 7. v1.2 — Trabajo + Personal

## Objetivo

Permitir que AURA comprenda diferentes áreas de la vida manteniendo una única representación del tiempo disponible.

---

## Workspaces

Introducir inicialmente:

```text
Personal
Trabajo
```

Cada tarea podrá pertenecer a un workspace.

Ejemplos:

```text
Preparar presentación → Trabajo
Revisar informe → Trabajo

Comprar supermercado → Personal
Hacer yoga → Personal
```

---

## Tipos de actividad

El workspace y el tipo de actividad deben representar conceptos distintos.

Ejemplos de tipos de actividad:

```text
deep_work
meeting
administrative
exercise
errand
study
routine
rest
```

Esto permitirá que AURA comprenda no solamente **a qué área pertenece una tarea**, sino también **qué tipo de esfuerzo o actividad representa**.

---

## Disponibilidad global

Aunque existan workspaces diferentes, el tiempo disponible debe ser único.

Por ejemplo:

```text
09:00–10:00 Trabajo
10:00–11:00 Trabajo
11:00–12:00 Cita personal
12:00–13:00 Trabajo
```

La cita personal ocupa tiempo real y, por lo tanto, afecta la disponibilidad laboral.

AURA debe comprender esto automáticamente.

---

## Criterio de cierre v1.2

AURA puede organizar actividades laborales y personales dentro de una única línea temporal, manteniendo la separación conceptual entre ambos contextos.

---

# 8. v1.3 — Día dinámico

## Objetivo

Pasar de un plan generado una vez al día a un plan capaz de adaptarse a lo que realmente ocurre.

AURA debe evolucionar desde:

> “Este es tu plan.”

hacia:

> “Este es el mejor plan considerando cómo ha avanzado tu día.”

---

## Tareas flexibles

No todas las actividades tienen el mismo nivel de rigidez.

Se deberá diseñar una distinción similar a:

```text
fixed
preferred
flexible
```

Una reunión fija no debería comportarse igual que una tarea que puede realizarse en cualquier momento de la tarde.

---

## Replanificación

AURA deberá poder recalcular el día cuando:

* una tarea termine antes;
* una tarea tome más tiempo;
* una tarea no se realice;
* aparezca una nueva tarea;
* cambie la disponibilidad;
* cambie una prioridad;
* ocurra un compromiso inesperado.

---

## Seguimientos

AURA podrá comenzar a hacer seguimiento de acciones pendientes.

Ejemplo:

> “Esta tarea quedó pendiente ayer. Hoy vuelve a existir espacio para realizarla.”

---

## Estabilidad del plan

Un plan dinámico no significa reorganizar constantemente todo el día.

AURA debe preferir:

> **el mínimo cambio necesario que produzca una mejora útil.**

Las decisiones existentes deberían conservarse cuando no exista una razón suficientemente importante para modificarlas.

---

## Criterio de cierre v1.3

AURA puede adaptar el plan a la ejecución real del día sin generar una experiencia impredecible o excesivamente cambiante.

---

# 9. v1.4 — Persistencia personal

## Objetivo

Transformar AURA desde un asistente que funciona durante una sesión hacia un asistente que mantiene continuidad personal en el tiempo.

---

## Usuarios

Incorporar identidad persistente de usuario.

Esto permitirá posteriormente:

* autenticación;
* múltiples usuarios;
* aislamiento de información;
* despliegue fuera del entorno local.

---

## Sesiones

Las conversaciones deberán tener una identidad persistente.

AURA podrá reconocer cuándo diferentes mensajes forman parte de una misma conversación.

---

## Memoria persistente

La memoria actual dejará de depender exclusivamente del proceso de ejecución.

Se deberán distinguir distintos tipos de memoria, por ejemplo:

```text
contexto conversacional
preferencias
preferencias de planificación
información histórica relevante
```

La memoria debe ser **estructurada e intencional**.

El objetivo no es almacenar indefinidamente todas las conversaciones sin criterio.

---

## Rutinas

Introducir actividades recurrentes.

Ejemplos:

```text
Tomar creatina
Hacer ejercicio
Planificar mañana
Revisión semanal
```

Una rutina no debería requerir crear manualmente la misma tarea cada día.

---

## Notificaciones

AURA podrá comenzar a comunicarse proactivamente.

Ejemplos:

> “Tu próxima actividad comienza en 15 minutos.”

> “Esta tarea sigue pendiente.”

> “Tu planificación cambió porque la actividad anterior tomó más tiempo.”

---

## Criterio de cierre v1.4

AURA mantiene información personal relevante entre reinicios y puede gestionar comportamientos recurrentes y notificaciones.

---

# 10. v1.5 — Google Calendar

## Objetivo

Incorporar los compromisos reales del usuario como restricciones automáticas del Planner.

---

## Primera etapa: lectura

Inicialmente Google Calendar debe actuar como fuente de disponibilidad.

```text
Google Calendar
        ↓
Eventos
        ↓
Busy Blocks
        ↓
Planner
```

AURA podrá conocer reuniones, citas y compromisos sin que el usuario tenga que registrarlos nuevamente.

---

## Segunda etapa: escritura

Posteriormente podrá evaluarse:

* crear eventos;
* modificar eventos creados por AURA;
* sincronizar determinadas tareas.

Debe mantenerse una distinción clara entre:

**compromisos fijos del calendario**

y

**tareas flexibles administradas por AURA**.

Google Calendar aporta restricciones.

AURA continúa tomando las decisiones de planificación.

---

## Criterio de cierre v1.5

Los compromisos reales del calendario participan automáticamente en las decisiones del Planner.

---

# 11. v1.6 — Interfaces naturales

## Objetivo

Permitir interactuar con AURA sin depender necesariamente de abrir la aplicación web.

La lógica de planificación debe continuar siendo única.

Las nuevas interfaces solamente deben actuar como puntos de entrada al mismo núcleo.

---

## WhatsApp

**Primera interfaz externa priorizada.**

Ejemplo:

> “Mañana tengo que revisar una tesis y preparar una presentación.”

Arquitectura conceptual:

```text
WhatsApp
    ↓
Adaptador de interfaz
    ↓
Assistant Layer
    ↓
Workflows existentes
    ↓
AURA Core
```

No debe duplicarse lógica de planificación dentro de la integración de WhatsApp.

---

## Audio

Una vez estabilizada la interacción escrita:

```text
Audio
   ↓
Speech-to-Text
   ↓
Assistant Layer
   ↓
AURA
```

Esto permitirá registrar tareas y consultar al asistente sin escribir.

---

## Alexa / asistentes de voz

Posteriormente podrán evaluarse interfaces adicionales.

Por ejemplo:

> “Pregúntale a AURA qué debería hacer ahora.”

La prioridad será primero WhatsApp y posteriormente voz/Alexa.

---

## Criterio de cierre v1.6

AURA puede utilizarse mediante al menos una interfaz natural externa reutilizando el mismo núcleo de planificación, decisión y aprendizaje.

---

# 12. v1.7 — Automatización y aprendizaje avanzado

## Objetivo

Evolucionar desde un Planner adaptativo hacia un sistema progresivamente más proactivo y personalizado.

Esta versión deberá aprovechar la información histórica acumulada durante el uso real de las versiones anteriores.

---

## Aprendizaje avanzado

Posibles áreas:

* horarios de mayor productividad;
* duración real según tipo de tarea;
* patrones de postergación;
* patrones de energía;
* patrones de foco;
* rendimiento según contexto;
* cumplimiento de rutinas;
* aceptación o rechazo de recomendaciones.

Ejemplo:

```text
Estimación inicial:
60 minutos

Historial:
Tareas similares requieren aproximadamente 82 minutos

Nueva estimación de AURA:
80 minutos
```

El `Adaptive Profile` actual constituye la base para esta evolución.

---

## Automatización

AURA podrá comenzar a realizar determinadas acciones sin necesitar una instrucción explícita para cada una.

Por ejemplo:

* reprogramar automáticamente tareas flexibles;
* detectar rutinas a partir del comportamiento repetido;
* identificar días con carga poco realista;
* proteger bloques productivos;
* anticipar conflictos;
* sugerir ajustes antes de que aparezcan problemas;
* recuperar automáticamente tareas pendientes.

---

## Principio de automatización

AURA debe automatizar con mayor libertad aquellas decisiones que sean:

* reversibles;
* explicables;
* de bajo impacto.

Las decisiones con consecuencias externas importantes deben mantener mayor control del usuario.

---

## Criterio de cierre v1.7

AURA utiliza comportamiento histórico suficiente para mejorar significativamente sus decisiones y automatizar determinadas acciones manteniendo explicabilidad y control.

---

# 13. Más allá de v1.7

Existen capacidades interesantes que todavía no necesitan una versión asignada.

Entre ellas:

* interacción por voz más avanzada;
* planificación semanal;
* planificación de objetivos de largo plazo;
* predicción de carga;
* detección avanzada de rutinas;
* nuevas plataformas de mensajería;
* contexto de ubicación;
* nuevas integraciones;
* interacción multidispositivo;
* agentes de planificación más autónomos.

Estas capacidades deberán priorizarse según el aprendizaje obtenido mediante el uso real de AURA.

---

# 14. Principios de desarrollo

## 1. El núcleo es independiente de la interfaz

Web, WhatsApp, voz o futuras interfaces deben utilizar los mismos motores.

La inteligencia no debe duplicarse.

---

## 2. No agregar IA cuando no sea necesaria

Si una regla determinística resuelve correctamente un problema, no necesitamos reemplazarla simplemente por utilizar IA.

Los modelos externos o generativos deben incorporarse cuando aporten valor concreto.

---

## 3. Explicabilidad

Las decisiones importantes deben poder justificarse.

---

## 4. Aprender del comportamiento real

Lo que el usuario realmente hace debe tener progresivamente más peso que las suposiciones iniciales del sistema.

---

## 5. Una sola línea temporal

Trabajo, vida personal, ejercicio, reuniones, citas y rutinas consumen el mismo recurso:

**tiempo.**

Los workspaces organizan conceptualmente las actividades, pero no deben crear disponibilidades artificialmente separadas.

---

## 6. Dinámico, pero estable

AURA debe adaptarse cuando las circunstancias cambien sin reorganizar innecesariamente todo el día.

---

## 7. Autonomía progresiva

La evolución esperada es:

```text
AURA recomienda
      ↓
AURA ayuda a ejecutar
      ↓
AURA anticipa
      ↓
AURA automatiza decisiones reversibles
```

La autonomía debe aumentar junto con la información disponible y la confianza en las decisiones.

---

## 8. Versiones estables

Las nuevas funcionalidades no deben comprometer capacidades existentes.

Cada versión debe mantener cobertura mediante pruebas automatizadas y agregar tests de regresión cuando se detecten errores reales.

---

# 15. Punto actual de desarrollo

```text
VERSIÓN ESTABLE
AURA v1.0.1

TESTS
85 passing

ESTADO
Versión cerrada

SIGUIENTE VERSIÓN
AURA v1.1 — AURA usable

OBJETIVO INMEDIATO
Transformar el backend inteligente existente
en una aplicación que pueda utilizarse realmente
durante el día.
```

Por lo tanto, el próximo trabajo **no consiste en seguir agregando inteligencia al backend**.

El núcleo actual ya permite:

```text
Planificar
Recomendar
Explicar
Aprender
Adaptarse
Conversar
Recordar contexto temporal
```

El siguiente paso es construir la experiencia necesaria para **usar realmente AURA**.

---

# 16. Próximo milestone

## AURA v1.1 — AURA usable

El desarrollo continúa desde:

```text
v1.0.1
    ↓
Backend estable
    ↓
85 tests passing
    ↓
INICIO v1.1
    ↓
App web
    ↓
Vista Hoy
    ↓
Gestión de tareas
    ↓
Chat
    ↓
Completar tareas
    ↓
Uso real de AURA
```

A partir de este punto, cualquier nueva funcionalidad debe evaluarse preguntando:

> **¿Pertenece realmente a v1.1 o corresponde a una versión posterior del roadmap?**

Esto permitirá evitar que el alcance de cada versión crezca innecesariamente y mantener una evolución controlada del producto.
