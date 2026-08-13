# AURA — Product Vision

## 1. Visión

AURA es un asistente personal inteligente de planificación y ejecución.

Su objetivo no es únicamente almacenar tareas ni construir calendarios.

AURA busca reducir la carga mental asociada a decidir constantemente:

- qué hacer;
- cuándo hacerlo;
- qué es más importante;
- qué puede esperar;
- cómo reorganizar el día cuando algo cambia;
- y por qué una determinada decisión tiene sentido.

La experiencia ideal de AURA requiere el mínimo esfuerzo posible por parte del usuario.

El usuario expresa lo que necesita hacer de forma natural y AURA se encarga de interpretar, organizar, priorizar, recordar, adaptar y explicar.

---

# 2. Principio central

AURA debe responder continuamente a tres preguntas:

1. ¿Qué debería hacer ahora?
2. ¿Qué viene después?
3. ¿Sigue siendo realista mi plan?

El usuario no debería tener que administrar constantemente su sistema de productividad.

AURA administra el sistema para que el usuario pueda concentrarse en ejecutar.

---

# 3. Filosofía de producto

## 3.1 Decidir, no solamente almacenar

Una lista de tareas dice qué está pendiente.

AURA debe ayudar a decidir qué hacer con esas tareas.

El sistema debe considerar:

- prioridad;
- deadlines;
- disponibilidad;
- contexto;
- duración;
- energía;
- enfoque;
- estrés;
- compromisos existentes;
- preferencias;
- comportamiento histórico.

---

## 3.2 Mínimo esfuerzo

El usuario no debería tener que completar formularios complejos para crear una tarea.

Por ejemplo:

> "Mañana tengo que llamar al dentista."

debería ser suficiente para crear una tarea razonable.

AURA deberá inferir toda la información que pueda y preguntar únicamente cuando falte información realmente necesaria.

El principio es:

> El usuario no debería tener que organizar el sistema para que el sistema pueda organizar al usuario.

---

## 3.3 Planificación dinámica

Un plan no es una estructura rígida.

La realidad cambia durante el día:

- reuniones se alargan;
- tareas toman más tiempo;
- aparecen urgencias;
- cambia la energía;
- algunas tareas terminan antes;
- otras no se realizan.

AURA debe ser capaz de reorganizar el resto del día cuando estas condiciones cambien.

El objetivo no es mantener intacto el plan original.

El objetivo es mantener un plan realista.

---

## 3.4 Explicabilidad

Las decisiones importantes de AURA deben poder explicarse.

El usuario podrá preguntar:

> "¿Por qué?"

> "¿Por qué esto primero?"

> "¿Por qué moviste esta tarea?"

> "¿Por qué reservaste 90 minutos?"

> "¿Qué has aprendido de mí?"

AURA deberá responder utilizando las razones reales que produjeron la decisión.

El aprendizaje nunca debe convertir el sistema en una caja negra.

---

## 3.5 Control del usuario

AURA recomienda y reorganiza, pero el usuario conserva siempre el control.

Si el usuario dice:

> "Quiero hacer esta tarea primero."

AURA debe aceptar esa decisión y adaptar el resto del plan.

Las preferencias explícitas del usuario tienen prioridad sobre las inferencias del sistema.

---

# 4. Workspaces

AURA tendrá inicialmente dos espacios principales:

- Trabajo
- Personal

Cada workspace mantiene su propio contexto, tareas, proyectos y prioridades.

## Trabajo

Puede contener:

- tareas profesionales;
- proyectos;
- reuniones;
- deadlines;
- clientes;
- actividades de concentración.

## Personal

Puede contener:

- hogar;
- salud;
- familia;
- compras;
- ejercicio;
- trámites;
- rutinas;
- recordatorios personales.

---

# 5. Separación de contexto y disponibilidad global

Trabajo y Personal deben permanecer separados conceptualmente y visualmente.

Sin embargo, ambos pertenecen a una misma persona y comparten el mismo tiempo.

Por ello AURA debe mantener una disponibilidad temporal global.

Ejemplo:

Una reunión de Trabajo de 10:00 a 11:00 bloquea ese horario para actividades personales que requieren atención.

Una cita médica personal de 15:00 a 16:00 bloquea ese horario para reuniones laborales.

Esto permite mantener privacidad y organización entre contextos sin crear dos calendarios incompatibles.

---

# 6. Tipos de actividades

No todas las tareas deben comportarse como bloques rígidos de calendario.

AURA distinguirá inicialmente entre diferentes tipos de actividad.

## 6.1 Bloques de tiempo

Actividades que necesitan tiempo protegido.

Ejemplos:

- preparar una propuesta;
- estudiar;
- escribir un informe;
- hacer ejercicio;
- desarrollar una funcionalidad.

Ejemplo:

> Preparar propuesta — 90 minutos.

AURA debe reservar un espacio real para realizarla.

---

## 6.2 Compromisos fijos

Eventos que ocurren en un horario específico y no pueden moverse libremente.

Ejemplos:

- reuniones;
- citas médicas;
- vuelos;
- clases;
- compromisos familiares.

Ejemplo:

> Reunión con cliente — 10:00 a 11:00.

Estos compromisos forman parte de la disponibilidad global.

---

## 6.3 Tareas flexibles

Actividades que deben realizarse pero que no necesariamente necesitan reservar formalmente un bloque del calendario.

Ejemplos:

- echar a lavar ropa;
- tomar vitaminas;
- llamar al banco;
- sacar la basura;
- enviar un documento;
- hacer una compra rápida.

Ejemplo:

> Echar a lavar ropa — aproximadamente 5 minutos — hoy.

AURA puede mantener la actividad pendiente y buscar una oportunidad adecuada para realizarla sin convertirla necesariamente en un bloque rígido.

---

## 6.4 Actividades con seguimiento

Algunas actividades generan una acción futura.

Ejemplo:

> Echar a lavar ropa.

Puede requerir cinco minutos de atención inicial.

Posteriormente:

> La lavadora debería haber terminado. Recuerda sacar o mover la ropa.

AURA deberá poder representar actividades que generan seguimientos posteriores.

---

# 7. Planificación entre Trabajo y Personal

AURA debe poder razonar sobre ambos workspaces sin mezclarlos innecesariamente.

Ejemplo:

Trabajo:

- preparar propuesta;
- reunión 10:00;
- responder correos.

Personal:

- echar a lavar ropa;
- comprar comida;
- hacer ejercicio.

AURA puede producir:

08:30 — Preparar propuesta

10:00 — Reunión

11:00 — Echar a lavar ropa

11:05 — Continuar propuesta

12:00 — Responder correos

Las actividades personales pequeñas pueden aprovechar oportunidades naturales sin destruir bloques importantes de concentración.

---

# 8. Protección del trabajo profundo

AURA no debe optimizar únicamente para llenar cada minuto disponible.

Interrumpir una actividad de concentración para insertar una tarea de cinco minutos puede ser contraproducente.

Por ello el Planner deberá considerar el costo de interrupción.

Una tarea personal flexible puede esperar aunque técnicamente exista un espacio disponible si interrumpir una actividad importante genera más costo que beneficio.

El objetivo no es maximizar ocupación.

El objetivo es mejorar la ejecución real.

---

# 9. Experiencia principal

La pantalla principal de AURA debe responder inmediatamente:

- qué estoy haciendo ahora;
- qué viene después;
- cómo está organizado mi día;
- qué sigue pendiente.

Una posible estructura:

AURA

AHORA

Preparar propuesta  
45 min restantes  
Prioridad alta

[Completar]

HOY

08:30 Preparar propuesta  
10:00 Reunión  
11:15 Responder correos  
13:00 Almuerzo  
15:00 Informe

PERSONAL

✓ Medicamentos  
○ Echar a lavar ropa  
○ Comprar comida

AURA

"Pregúntame cualquier cosa..."

---

# 10. Conversación

La conversación será una interfaz fundamental, pero no será toda la aplicación.

El usuario podrá decir:

> "¿Qué hago ahora?"

> "¿Y después?"

> "Estoy cansada."

> "Solo tengo veinte minutos."

> "Mueve esto para mañana."

> "No alcancé a terminar."

> "Agrega comprar leche."

> "Hoy tengo que lavar ropa."

> "Planifica mañana."

> "¿Qué estoy posponiendo?"

> "¿Qué has aprendido de mí?"

La interfaz visual proporciona visibilidad y control.

La conversación proporciona velocidad y flexibilidad.

---

# 11. Voz

AURA debe diseñarse desde el principio para poder utilizar múltiples interfaces.

La lógica del asistente no debe depender de la aplicación visual.

En el futuro, una interfaz de voz como Alexa podría actuar como cliente de AURA.

Ejemplo:

Usuario:

> "Alexa, pregúntale a AURA cómo está mi día."

AURA:

> "Buenos días. Tienes una reunión a las diez y una propuesta que vence al mediodía. Te recomiendo comenzar con la propuesta. También tienes tres pendientes personales; dos son rápidos y los dejaré para después de tu reunión."

Otro ejemplo:

Usuario:

> "Dile a AURA que hoy tengo que lavar ropa."

AURA:

> "Listo. Lo dejaré como una tarea personal flexible para hoy y buscaré un momento que no interfiera con tu trabajo."

La voz debe permitir interacción rápida sin necesidad de abrir la aplicación.

---

# 12. Aplicación visual

La aplicación sirve principalmente para:

- visualizar el día;
- consultar tareas;
- ver qué está completado;
- modificar decisiones;
- revisar los workspaces;
- consultar aprendizaje;
- configurar preferencias;
- intervenir cuando el usuario lo desee.

La aplicación no debe exigir administración constante.

El objetivo es que AURA pueda funcionar incluso durante períodos en los que el usuario apenas abre la aplicación.

---

# 13. Aprendizaje

AURA aprende del comportamiento real del usuario.

Puede aprender:

- cuánto duran realmente ciertos tipos de tareas;
- qué horarios funcionan mejor;
- cuándo existe mayor concentración;
- qué tareas suelen posponerse;
- cómo afecta la energía a diferentes actividades;
- qué estimaciones suelen ser demasiado optimistas;
- qué rutinas se repiten.

Este conocimiento se almacena en el Adaptive Profile.

---

# 14. Aprendizaje silencioso y explicable

El aprendizaje debe mejorar las decisiones sin exigir configuración constante.

Por ejemplo:

El usuario estima:

> Preparar informe — 60 minutos.

AURA ha observado históricamente que tareas similares requieren aproximadamente 75 minutos.

El Planner puede reservar más tiempo.

Si el usuario pregunta:

> "¿Por qué reservaste 75 minutos?"

AURA puede responder:

> "Porque este tipo de tarea te ha tomado aproximadamente un 20 % más de lo estimado en ejecuciones anteriores."

---

# 15. Rutinas

AURA deberá permitir representar actividades recurrentes.

Ejemplos:

- medicamentos;
- ejercicio;
- sacar la basura;
- planificación semanal;
- revisar correo;
- preparar informes;
- tareas domésticas.

Las rutinas no deben obligar al usuario a recrear tareas constantemente.

---

# 16. Replanificación

Cuando cambia el día, AURA debe evaluar automáticamente el impacto.

Ejemplo:

Usuario:

> "La reunión se alargó una hora."

AURA puede responder:

> "Reorganicé el resto del día. Mantengo la propuesta porque vence hoy y moví la documentación para mañana."

Otro ejemplo:

Usuario:

> "No terminé la propuesta."

AURA deberá decidir si:

- continuar inmediatamente;
- mover otra tarea;
- reprogramar;
- reducir el plan;
- solicitar una decisión al usuario.

---

# 17. Inicio del día

Una experiencia objetivo sería:

Usuario:

> "Buenos días, AURA."

AURA:

> "Buenos días. Tienes seis tareas pendientes y dos compromisos hoy. La propuesta vence al mediodía, así que la puse primero. Tu primera reunión es a las diez. También tienes dos tareas personales rápidas que dejaré para momentos que no interrumpan tu trabajo."

El usuario puede aceptar el plan sin necesidad de abrir ninguna pantalla.

---

# 18. Durante el día

AURA puede intervenir cuando existe información útil.

Ejemplo:

> "Terminaste antes de lo previsto. Tienes 25 minutos antes de tu reunión. Puedes responder los correos pendientes."

O:

> "Tu siguiente tarea requiere bastante concentración. Si estás cansada, puedo reorganizarla."

Las intervenciones deben ser útiles y limitadas.

AURA no debe convertirse en una fuente adicional de interrupciones.

---

# 19. Cierre del día

AURA puede ofrecer un resumen breve.

Ejemplo:

> "Completaste cuatro de cinco tareas importantes. El informe quedó pendiente y lo moví provisionalmente a mañana. Hoy las tareas de trabajo tomaron un poco más de lo previsto."

El cierre permite alimentar el Learning Engine sin exigir un proceso manual complejo.

---

# 20. Automatización progresiva

AURA debe ganar autonomía gradualmente.

Inicialmente:

- recomienda;
- propone;
- pregunta.

Con suficiente confianza y preferencias explícitas podrá:

- reorganizar tareas flexibles;
- ajustar estimaciones;
- mover tareas no críticas;
- seleccionar oportunidades para tareas rápidas.

Las acciones de mayor impacto deberán seguir requiriendo confirmación cuando corresponda.

---

# 21. Integraciones

Las integraciones son mecanismos de entrada y salida, no el núcleo de inteligencia.

Integraciones previstas:

- Google Calendar;
- Alexa;
- WhatsApp u otros sistemas de mensajería;
- notificaciones móviles;
- servicios de salud o actividad;
- herramientas profesionales.

El dominio de AURA debe continuar funcionando independientemente de estos proveedores.

---

# 22. Principio de baja fricción

Cada nueva funcionalidad debe responder una pregunta:

> ¿Esto reduce o aumenta la carga mental del usuario?

Si una funcionalidad requiere más administración de la que elimina, debe reconsiderarse.

---

# 23. Qué AURA no quiere ser

AURA no pretende ser:

- una simple lista de tareas;
- un calendario tradicional;
- un chatbot genérico;
- un sistema que llena cada minuto del día;
- un sistema rígido que castiga los cambios;
- una caja negra que toma decisiones inexplicables;
- una aplicación que exige mantenimiento constante.

---

# 24. Un día con AURA

## 08:00 — Inicio

AURA presenta el plan del día.

Prioriza una propuesta laboral que vence al mediodía.

Detecta una reunión a las 10:00.

Mantiene "echar a lavar ropa" como tarea personal flexible.

## 09:50

AURA evita interrumpir el trabajo profundo únicamente para completar la tarea doméstica.

## 10:00

Comienza la reunión.

## 11:00

Finaliza la reunión.

AURA detecta una oportunidad natural:

> "Antes de continuar, tienes pendiente echar a lavar ropa. Te toma aproximadamente cinco minutos."

## 11:05

El usuario inicia la lavadora.

AURA programa un seguimiento aproximado para cuando termine el ciclo.

## 11:10

El usuario continúa trabajando.

## 12:00

La propuesta queda completada.

AURA actualiza el plan.

## 14:00

El usuario dice:

> "Estoy cansada y tengo treinta minutos."

AURA recomienda una tarea de baja demanda cognitiva que cabe en ese período.

## 16:00

Una reunión inesperada ocupa una hora.

AURA recalcula el resto del día.

## 17:30

Una tarea ya no cabe razonablemente.

AURA propone moverla al día siguiente.

## Final del día

AURA presenta un resumen corto y actualiza el aprendizaje a partir de las ejecuciones reales.

---

# 25. Experiencia objetivo

AURA debe sentirse menos como administrar una herramienta y más como tener un asistente que mantiene continuamente una representación realista del día.

La experiencia ideal es:

Decir lo que necesitas hacer.

Dejar que AURA organice.

Consultar qué hacer ahora.

Ejecutar.

Informar cambios cuando ocurren.

Dejar que AURA vuelva a organizar.

---

# 26. Principios de producto

Toda evolución de AURA deberá respetar estos principios:

1. Decidir, no solamente almacenar tareas.
2. Adaptarse cuando cambia el día.
3. Explicar las decisiones importantes.
4. Aprender del comportamiento real.
5. Mantener al usuario en control.
6. Minimizar configuración y administración.
7. Proteger la concentración.
8. Separar contextos sin fragmentar el tiempo.
9. Utilizar automatización progresiva.
10. Reducir la carga mental.

---

# 27. North Star

La métrica conceptual de AURA no será cuántas tareas almacena el usuario.

Será cuánto reduce la necesidad del usuario de pensar continuamente:

> "¿Qué debería hacer ahora?"

AURA tiene éxito cuando el usuario puede confiar en que su sistema refleja razonablemente su realidad y le ayuda a actuar sin tener que reorganizarlo constantemente.