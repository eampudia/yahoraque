<p align="center"><img src="assets/logo.png" alt="Yahoraque" width="220"></p>

# Yahoraque

**Enlace a la app:** https://yahoraque.streamlit.app/
**Autor:** Emilio Ampudia

## Pitch

Mucha gente necesita una aplicación pequeña (una calculadora para su negocio, un juego para clase, un control de gastos) y no sabe programar ni puede pagar un desarrollo. Yahoraque te deja describirla hablando con un analista y la construye, la publica y te da un enlace para compartirla. La IA hace dos trabajos: de analista, que convierte una idea vaga en requisitos claros, y de programador, que escribe la app en HTML y JavaScript, la prueba y la corrige sola. Probarla con navegadores reales destapó fallos que en local no se veían: la sesión se perdía al recargar en Streamlit Cloud, los enlaces públicos pedían iniciar sesión, y una app maliciosa podía hacerse pasar por admin con un simple `key="user"`. Un ejemplo: pedí una calculadora de propinas y en 20 segundos tenía «Propinator» funcionando; lo siguiente sería poder volver a versiones anteriores y que las apps guarden datos.

## El problema

Cualquier persona sin conocimientos de programación que quiera una aplicación web sencilla: autónomos, docentes, asociaciones, gente con una afición. Hoy usa herramientas genéricas que no hacen exactamente lo que necesita, o encarga un desarrollo que es caro y lento para algo pequeño. Merece la pena resolverlo porque la mayoría de estas apps son simples, y la IA ya escribe bien ese tipo de código: lo que falta es alguien que pregunte lo necesario y un sitio seguro donde ejecutarla.

## Qué hace la app

1. **Entras** con un nombre y un PIN (la sesión se recuerda 7 días), o como invitado para usar las apps públicas.
2. **Hablas con el analista.** Le cuentas qué quieres con tus palabras. Te hace preguntas y te enseña los requisitos en lenguaje sencillo.
3. **Confirmas y se construye.** La IA escribe la app, le inventa un nombre (por ejemplo «Aguatín» para un contador de vasos de agua), comprueba que arranca y, si falla, la arregla hasta 2 veces. Mientras esperas, salen frases divertidas («Consultando con mi gato, que sabe mucho de esto…»).
4. **La usas.** Tu app aparece en el menú con su nombre.
5. **La compartes o la cambias.** La puedes hacer pública: aparece en «Apps públicas» y cualquiera la abre con un enlace, sin cuenta. Puedes pedir cambios en el chat (el analista ya conoce tu app) o borrarla y empezar otra.
6. **El admin** ve a todos los usuarios en la barra lateral, abre sus apps, las publica u oculta y puede borrar usuarios.

## La pieza de IA

- **Qué usa:** la API de Gemini (librería `google-genai`) en la capa gratuita, con dos roles: el **analista**, que conversa y escribe los requisitos, y el **desarrollador**, que genera la app como página HTML, CSS y JavaScript con Pico CSS, Chart.js, canvas-confetti, Alpine.js o p5.js. El modelo no está fijo: Yahoraque lista los modelos disponibles para la clave, los ordena por versión y potencia (pro > flash > flash-lite) y usa el mejor que responda.
- **Por qué esa opción:** es gratuita y, de las opciones gratuitas, la que mejor se comporta escribiendo código. El usuario nunca ve qué modelo se usa, así que se puede cambiar de proveedor sin que lo note.
- **Qué pasa si falla:**
  - **Si falla un modelo** (cuota agotada, saturado, sin respuesta en 60 s), se repite la misma petición con el siguiente sin mostrar nada. El que falla se aparta un tiempo: 24 h sin cuota diaria, 1 min si es límite por minuto, 5 min si está saturado.
  - **Si fallan todos:** «Los astros no están alineados, inténtalo más tarde.»
  - **Si la app nueva no funciona** tras 2 arreglos, se mantiene la versión anterior y no se pierde nada.
  - **Si la IA genera algo peligroso o prohibido:** los guardarraíles lo rechazan antes de ejecutarlo, y las peticiones de phishing o suplantación se rechazan con «RECHAZADA».

## Cómo la he construido

- **Herramientas:** Claude Code (extensión de VS Code) como agente, Docker para ejecutar y probar todo, y Playwright para las pruebas con navegadores reales (Chrome, Firefox y Safari/WebKit). [Añade otras si las usaste, por ejemplo la herramienta con la que hiciste el logo.]
- **Fichero de contexto del agente:** [CLAUDE.md](CLAUDE.md). Le obliga a trabajar solo en Docker, a fijar versiones, a no subir secretos, a no hacer commit sin mi permiso y a convertir mis ideas en reglas comprobables en [especificacion.md](especificacion.md).
- **Prompts clave** (copiados tal cual):
  1. «continua con el modo desarrollador»
  2. «cuando entro con el usuario administrador, tengo que poder ver en la barra de la izquierda los usuarios que se han registrado y tengo que poder borrarlos y ver sus aplicaciones»
  3. «cuando te pida modificaciones de la aplicacion, usa la información de la aplicacion que ya tenemos creada. Porque no la incluyes en el contexto.»
  4. «Me gustaria que las aplicaciones que crea, se creasen en javascript (pero el codigo de python) siempre que fuera posible.»
  5. «crees que podria utilizar alguna libreria grafica de python para mejorar la creacion de aplicaciones?»
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

**Apps públicas, vistas por el admin.** Cada app tiene el nombre que le inventó la IA y la frase «Para qué sirve» de sus requisitos. En la barra lateral, debajo del menú, el admin ve a los usuarios registrados. El primero sale con su hash porque se registró antes de que se guardaran los nombres.

![Apps públicas vistas por el admin](assets/APP%20Publicas.png)

**Javijator, abierta por un invitado.** Una app pública generada por la IA en HTML y JavaScript, con el estilo de Yahoraque (títulos en Fredoka, colores del logo). Quien la abre no tiene cuenta: entra como invitado.

![Javijator abierta por un invitado](assets/APP%20javijator.png)

**Cambiar una app desde el chat.** Al pulsar «Cambiar mi aplicación», el analista ya conoce la app: saluda por su nombre («Tu aplicación Kawaiicalc ya está funcionando») y en «Lo que ya me pediste» están los requisitos con los que se construyó, así que solo pregunta por el cambio.

![Chat para cambiar Kawaiicalc](assets/Edita%20APP.png)
