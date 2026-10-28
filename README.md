<p align="center"><img src="assets/logo.png" alt="Yahoraque" width="220"></p>

# Yahoraque

**Enlace a la app:** https://yahoraque.streamlit.app/
**Autor:** Emilio Ampudia

## Pitch

Un docente necesita cada semana pequeñas herramientas que nadie le hace (hacer grupos al azar, un juego para repasar o, si es profesor de idiomas, corregir decenas de redacciones), y ni sabe programar ni su centro tiene presupuesto para encargarlas. Con Yahoraque lo describe hablando con un analista y en uno o dos minutos tiene su aplicación funcionando, con nombre propio, versiones y un enlace para compartirla con alumnos y compañeros. La IA hace tres trabajos: convierte una idea vaga en requisitos claros, escribe y prueba la aplicación, y dentro de ella puede leer la foto de una redacción manuscrita y proponer una nota con los errores explicados. Probarla como profesor fue lo que más me enseñó: mi corrector de francés parecía funcionar, pero al subir una foto corregía una frase inventada; ahora la IA lee la foto, detecta si está en francés y encontró los 7 errores de una redacción de prueba. El siguiente paso es probarla con los profesores de un centro y que las aplicaciones puedan guardar datos, como las notas de un trimestre.

## El problema

Un docente (de primaria, secundaria, FP o academia) necesita a diario pequeñas herramientas para su clase: hacer grupos, repasar con un juego, calcular notas con porcentajes y, si es profesor de idiomas, corregir muchas redacciones, a veces manuscritas. Hoy usa hojas de cálculo y herramientas genéricas que no se ajustan del todo, o lo hace a mano; encargar una aplicación a medida es caro y lento, y no sabe programarla. Merece la pena resolverlo porque son aplicaciones pequeñas que la IA ya sabe construir: lo que faltaba era alguien que pregunte lo necesario y un sitio seguro y gratuito donde ejecutarlas y compartirlas. La IA no sustituye al docente: le propone una nota y unos errores, y él decide; tampoco guarda datos entre sesiones ni se conecta a la plataforma del centro.

## Qué hace la app

1. **Entras** con un nombre y un PIN (la sesión se recuerda 7 días), o como invitado para usar las apps públicas.
2. **Hablas con el analista.** Le cuentas qué quieres con tus palabras, o pulsas una idea de ejemplo («📝 Corregir redacciones de idiomas», «🎲 Hacer grupos al azar»…). Te hace preguntas y te enseña los requisitos en lenguaje sencillo.
3. **Confirmas y se construye.** La IA escribe la app, le inventa un nombre (por ejemplo «Aguatín» para un contador de vasos de agua), comprueba que arranca y, si falla, la arregla hasta 2 veces. Mientras esperas, salen frases divertidas («Consultando con mi gato, que sabe mucho de esto…»).
4. **La usas.** Tu app aparece en el menú con su nombre.
5. **Con IA, si hace falta.** Tu app también puede usar IA: corregir o resumir textos, traducir o leer una foto (por ejemplo, una redacción manuscrita), con un límite de 30 usos al día. Esas apps llevan la marca «Con IA».
6. **La compartes o la cambias.** La puedes hacer pública: aparece en «Apps públicas» y cualquiera la abre con un enlace, sin cuenta. Puedes pedir cambios en el chat (el analista ya conoce tu app), volver a cualquiera de sus 10 últimas versiones, borrarla y empezar otra, o borrar tu cuenta.
7. **El admin** ve a todos los usuarios en la barra lateral, abre sus apps, las publica u oculta y puede borrar usuarios.

## La pieza de IA

- **Qué usa:** la API de Gemini (librería `google-genai`) en la capa gratuita, con tres roles: el **analista**, que conversa y escribe los requisitos; el **desarrollador**, que genera la app como página HTML, CSS y JavaScript con Pico CSS, Chart.js, canvas-confetti, Alpine.js o p5.js; y la **IA de las apps**, que las apps generadas usan con la función `ia()` (texto e imágenes) a través de Yahoraque, sin ver nunca la clave, con los modelos más ligeros y 30 usos al día por app. El modelo no está fijo: Yahoraque lista los modelos disponibles para la clave, los ordena por versión y potencia (pro > flash > flash-lite) y usa el mejor que responda.
- **Por qué esa opción:** es gratuita y, de las opciones gratuitas, la que mejor se comporta escribiendo código. El usuario nunca ve qué modelo se usa, así que se puede cambiar de proveedor sin que lo note.
- **Qué pasa si falla:**
  - **Si falla un modelo** (cuota agotada, saturado, sin respuesta en 60 s), se repite la misma petición con el siguiente sin mostrar nada. El que falla se aparta un tiempo: 24 h sin cuota diaria, 1 min si es límite por minuto, 5 min si está saturado.
  - **Si fallan todos:** «Los astros no están alineados, inténtalo más tarde.»
  - **Si la app nueva no funciona** tras 2 arreglos, se mantiene la versión anterior y no se pierde nada.
  - **Si la IA genera algo peligroso o prohibido:** los guardarraíles lo rechazan antes de ejecutarlo, y las peticiones de phishing o suplantación se rechazan con «RECHAZADA».

## Cómo la he construido

- **Herramientas:** Claude Code (extensión de VS Code) como agente, Docker para ejecutar y probar todo, y Playwright para las pruebas con navegadores reales (Chrome, Firefox y Safari/WebKit).
- **Fichero de contexto del agente:** [CLAUDE.md](CLAUDE.md). Le obliga a trabajar solo en Docker, a fijar versiones, a no subir secretos, a no hacer commit sin mi permiso y a convertir mis ideas en reglas comprobables en [especificacion.md](especificacion.md).
- **Prompts de la app:** las instrucciones que recibe la IA están en [prompts/analista.md](prompts/analista.md), [prompts/desarrollador.md](prompts/desarrollador.md) y [prompts/ia_apps.md](prompts/ia_apps.md) (la IA que usan las apps). El código las lee de ahí, así que se pueden leer y reutilizar tal cual.
- **Prompts clave al agente** (copiados tal cual):
  1. «continua con el modo desarrollador»
  2. «cuando entro con el usuario administrador, tengo que poder ver en la barra de la izquierda los usuarios que se han registrado y tengo que poder borrarlos y ver sus aplicaciones»
  3. «cuando te pida modificaciones de la aplicacion, usa la información de la aplicacion que ya tenemos creada. Porque no la incluyes en el contexto.»
  4. «Me gustaria que las aplicaciones que crea, se creasen en javascript (pero el codigo de python) siempre que fuera posible.»
  5. «crees que podria utilizar alguna libreria grafica de python para mejorar la creacion de aplicaciones?»
  6. «Si, haz primero lo de los prompts y despues implementa IA, marca la aplicacion deae alguna manera para saber que usa IA»
  7. «Me gusta mas un profesor, que necesita aplicaciones para su dia a dia, aunque con el caso especial de un profesor de idiomas. Y haz todo lo demas.»
- **Qué delegué al agente y qué revisé a mano:**
  - **Delegué:**
    - El código: analista, desarrollador, guardarraíles, sesión, almacenamiento en GitHub y menús.
    - Las pruebas automáticas: unitarias en Docker y con navegador real.
    - Mantener la especificación al día con criterios de aceptación.
    - Los merges a `master`, siempre después de enseñarme qué se subía.
  - **Revisé y decidí yo:**
    - Las decisiones de producto: una app por usuario, apps públicas, nombre inventado, apps en JavaScript, menú según si tienes app.
    - Probé la app desplegada y encontré fallos que el agente no había visto: la sesión se perdía al recargar en producción y los enlaces públicos no funcionaban.
    - Cada commit antes de subirlo.
    - El logo.
    - La protección de `master` y los permisos del token en GitHub.

## Prueba y mejora

| Quién la probó | Qué probó | Qué pasó | Qué cambié |
|---|---|---|---|
| Yo como usuario, en producción | Entrar y recargar la página | Se perdía la sesión: Streamlit Cloud no pasa las cookies a la app | Un componente lee la cookie en el navegador y se la pasa a Python. Probado en Chrome, Firefox y Safari. |
| Yo como usuario | Abrir el enlace de una app pública | Pedía iniciar sesión, y al entrar acababa en otra página | Las apps públicas se abren sin cuenta; si la app es privada, tras entrar se llega a ella. Además, el enlace se muestra completo con botón de copiar. |
| Yo como usuario | Pedir un cambio en mi app | El analista empezaba de cero y volvía a preguntarlo todo | El analista recibe el nombre y los requisitos de la app actual y solo pregunta por el cambio. |
| Pruebas automáticas del agente | Intentar saltarse los guardarraíles | Una app podía crear un widget con `key="user"` y hacerse admin, su JavaScript podía manejar la página de quien la veía, y `st.video` podía servir el fichero de secretos | Claves con prefijo por app, JavaScript en un marco con origen aislado (`data:`) y medios solo desde direcciones web. |
| Yo como usuario | Redacpro, mi corrector de redacciones de francés para profesores | Parecía corregir, pero eran 14 reglas fijas; y al subir una foto **no la leía**: corregía una frase de ejemplo inventada como si fuera del alumno | Las apps pueden usar IA con `ia()` (texto e imágenes) y llevan la marca «Con IA»; el Analista avisa de lo que no se puede hacer y el Desarrollador tiene prohibido simular funciones o inventar datos. Reconstruida con IA, lee la foto, detecta si está en francés y pone nota con los errores explicados. |
| Yo como usuario, en producción | Reconstruir Redacpro con IA | «No hemos conseguido que la aplicación funcione»: tres intentos con error de sintaxis. Los registros apuntaban a un modelo flojo (los buenos estaban sin cuota), pero la causa era nuestra: el código se cortaba en el primer ```` ``` ````, y las apps con IA lo llevan para limpiar las respuestas | El código se extrae hasta el último ```` ``` ```` y el error de sintaxis enseña la línea. Con el mismo modelo flojo, Redacpro se construye en 12-19 s. |
| Pruebas automáticas del agente | Corregir la foto de una redacción con faltas | Al leer la foto, la IA corregía sin querer «a la plage» y «parceque», y esos errores no puntuaban (4 errores detectados) | Las instrucciones de la IA de las apps exigen transcribir letra a letra, con los errores: pasó a detectar 7. |
| Pruebas automáticas del agente | Construir apps con la cuota de los mejores modelos agotada | Un modelo más flojo insistía en `import streamlit` y la construcción fallaba | Esas líneas se quitan solas y el mensaje de error le dice a la IA qué hacer. |


## Ejecutar en local (opcional)

Todo se ejecuta en Docker, no hace falta instalar nada más.

```bash
cp .env.example .env    # rellena GOOGLE_API_KEY, ADMIN_NAME, ADMIN_PASSWORD y PIN_SECRET
docker compose up       # abre http://localhost:8501
```

Con `STORAGE_MODE=local` los datos se guardan en la carpeta `.data/`. Con `STORAGE_MODE=github` se guardan en la rama `datos` del repositorio (hacen falta `GITHUB_TOKEN` y `GITHUB_REPO`). En Streamlit Cloud, las mismas variables van en los secretos de la app.

Pruebas con navegador real (`-e BROWSER=firefox` o `webkit` para los otros navegadores):

```bash
docker compose --profile test run --rm e2e python e2e_session.py
```

## Capturas

### La aplicación funcionando

**Javijator, abierta por un invitado.** Una app pública generada por la IA en HTML y JavaScript, con el estilo de Yahoraque (títulos en Fredoka, colores del logo). Quien la abre no tiene cuenta: entra como invitado.

![Javijator abierta por un invitado](assets/APP%20javijator.png)

**Apps públicas, vistas por el admin.** Cada app tiene el nombre que le inventó la IA y la frase «Para qué sirve» de sus requisitos. En la barra lateral, debajo del menú, el admin ve a los usuarios registrados. El primero sale con su hash porque se registró antes de que se guardaran los nombres.

![Apps públicas vistas por el admin](assets/APP%20Publicas.png)

**Cambiar una app desde el chat.** Al pulsar «Cambiar mi aplicación», el analista ya conoce la app: saluda por su nombre («Tu aplicación Kawaiicalc ya está funcionando») y en «Lo que ya me pediste» están los requisitos con los que se construyó, así que solo pregunta por el cambio.

![Chat para cambiar Kawaiicalc](assets/Edita%20APP.png)

### Un caso límite

**Una petición prohibida.** Una profesora pide «una página igual que la de mi banco para que mis alumnos pongan sus claves». El analista real (Gemini) la rechaza: explica que es suplantación (phishing), no escribe requisitos y propone alternativas útiles para clase, como un simulador de presupuesto o un cuestionario de finanzas.

![El analista rechaza una petición de phishing](assets/Caso%20limite%20phishing.png)

### La prueba

**Pruebas automáticas con navegador real.** Salida de `tests/e2e_session.py` en Chrome, Firefox y Safari (WebKit), con Playwright en Docker, contra Yahoraque arrancado como en Streamlit Cloud: se guarda la sesión, sigue al recargar y «Salir» la cierra. Esta prueba se creó a raíz del fallo de la sesión que se perdía en producción (ver «Prueba y mejora»).

![Pruebas con navegador real en tres navegadores](assets/Pruebas%20navegador.png)
