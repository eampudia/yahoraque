# Especificación · Yahoraque


## 1. Problema y usuario

- **Quién tiene el problema:** un **docente** (primaria, secundaria, FP o academia) sin conocimientos de programación que necesita pequeñas aplicaciones para su día a día en clase: hacer grupos al azar, un juego de preguntas para repasar, calcular la nota media con porcentajes…
  - **Caso especial, el profesor de idiomas:** corrige muchas redacciones (en el ejemplo de referencia, en francés) y quiere una herramienta que lea el texto, aunque sea una foto de una redacción manuscrita, detecte si está en el idioma pedido y le proponga una nota con los errores explicados según el nivel del alumno.
- **Cómo lo resuelve hoy:** con hojas de cálculo, herramientas genéricas (formularios, plataformas de concursos) que no se ajustan del todo a lo que necesita, o a mano; corregir redacciones se lleva buena parte de su tiempo fuera de clase. Encargar una aplicación a medida es caro y lento, y su centro no tiene presupuesto ni programador.
- **Qué le molesta de cómo lo hace hoy:** las herramientas genéricas no hacen exactamente lo que necesita y no sabe programar para adaptarlas.
- **Qué parte resuelve la IA:**
  1. **Analista:** convierte su idea, contada con sus palabras, en requisitos claros.
  2. **Desarrollador:** escribe la aplicación, la prueba y la corrige sola.
  3. **IA dentro de la app:** cuando la app lo necesita, corrige, resume, traduce o lee el texto de una foto (por ejemplo, la redacción manuscrita).
- **Qué queda fuera:**
  - Guardar datos entre sesiones (por ejemplo, las notas de todo un trimestre) y conectarse a la plataforma del centro (Moodle, Classroom…).
  - Datos personales reales de los alumnos: se recomienda no poner nombres reales, porque los textos se envían a la IA de la capa gratuita (sección 11).
  - La decisión final: la IA **propone** una nota y unos errores, y el docente la revisa. Puede equivocarse, sobre todo con letra difícil de leer.
- Yahoraque está pensada para docentes, pero cualquiera puede registrarse y crear su app.

## 2. Qué hace el producto

1. Ayuda al usuario a saber qué necesita.
2. Desarrolla el código necesario.
3. Lo despliega de forma que sea accesible para el usuario.

## 3. Entradas y salidas

- El usuario describe su problema y el sistema le devuelve unos requerimientos en lenguaje humano, no técnico.
- Cuando el usuario los confirma, el sistema construye la aplicación y le inventa un nombre.
- El usuario puede volver al chat en cualquier momento para pedir cambios.
- La aplicación es privada (solo la ven su dueño y el admin) hasta que el dueño la hace pública; entonces la puede usar cualquiera, también los invitados sin cuenta.
- El dueño puede borrar su aplicación y empezar otra.
- Las aplicaciones pueden usar IA (por ejemplo, para corregir un texto o leer una foto), con un límite de usos al día; las que la usan llevan la marca «Con IA».

## 4. La pieza de IA

- **Opción elegida:** modelos Gemini de Google, capa gratuita, usados con la API de Google (Gemini API) y su librería oficial para Python.
- **Por qué:** Permite desarrollar la aplicación de forma gratuita y es la opción gratuita que mejor se comporta.
- **El usuario no sabe qué modelo se usa.** La interfaz nunca menciona Gemini, para poder cambiar de proveedor sin afectar al usuario.

### Elección del modelo
1. **Listar:** el sistema pide a la API de Google la lista de modelos disponibles para la clave y se queda solo con los que pueden generar texto. La lista se guarda en memoria y se refresca cada cierto tiempo (por ejemplo, cada hora), no en cada mensaje.
2. **Ordenar de más a menos potente:** la API no indica qué modelo es más potente, así que el orden se calcula a partir del nombre:
   - Primero la versión más alta (por ejemplo, 2.5 antes que 2.0).
   - Dentro de la misma versión: `pro` antes que `flash`, y `flash` antes que `flash-lite`.
   - Se descartan los modelos que no sirven para conversar o generar código (embeddings, imagen, audio, etc.).
3. **Probar en orden:** cada petición se envía al primer modelo de la lista. Si falla (cuota agotada, modelo no disponible, error temporal), se reintenta **la misma petición** con el siguiente, sin mostrar nada al usuario.
4. **Recordar los que fallan:** un modelo que falla se aparta durante un tiempo, para no perder tiempo probándolo en cada mensaje:
   - Sin cuota diaria, o no disponible para la clave: 24 horas.
   - Límite por minuto: 1 minuto.
   - Saturado, error del servidor o sin respuesta en 60 segundos: 5 minutos.
   - Error en la petición (probablemente un fallo nuestro): no se aparta.
5. **Si fallan todos:** se muestra "Los astros no están alineados, inténtalo más tarde."
6. **Registro interno:** qué modelo respondió y cuáles fallaron se anota en los logs, nunca en la pantalla del usuario.
- **Instrucciones para el modelo (system prompt):** el texto exacto está en [prompts/analista.md](prompts/analista.md) y [prompts/desarrollador.md](prompts/desarrollador.md), y el código los lee de ahí (`prompts.py`), así que lo que se ve en esos ficheros es lo que recibe la IA. Las partes que cambian van como `{MARCADORES}` (las marcas de los requisitos, los módulos y funciones permitidos, el kit de librerías…), explicados al principio de cada fichero. Resumen:
  - **Modo Analista:** se comporta como un analista tratando con un cliente. Hace las preguntas necesarias y, cuando ve que puede diseñar algo, muestra los requerimientos en lenguaje no técnico y pregunta si se empieza a construir.
    - **Si el usuario ya tiene app:** el analista recibe su nombre y sus requisitos guardados. Saluda con «¡Hola! Tu aplicación <nombre> ya está funcionando. Cuéntame qué te gustaría cambiar o añadir.», trata lo que pida como cambios sobre esa app (salvo que diga claramente que quiere otra distinta), no vuelve a preguntar lo que ya está en los requisitos y, al terminar, escribe los requisitos **completos** actualizados: lo que se mantiene más lo que cambia, con el mismo título.
    - El Desarrollador recibe esos requisitos completos junto con el código actual de la app (ver «Modo Desarrollador»).
  - **Modo Desarrollador:** se comporta como un programador senior de JavaScript, HTML, CSS y Python, y construye la app como una página HTML/JavaScript siempre que sea posible (sección 7, «Ejecución de las apps»). Recibe los requisitos confirmados (y el código actual de la app, si ya tenía una) y devuelve, en la misma respuesta, una línea `NOMBRE: <palabra>` con el nombre inventado de la app y el código completo en un único bloque, cumpliendo las reglas de los guardarraíles (sección 7), que se le explican en sus instrucciones. Si la app es de las prohibidas, responde «RECHAZADA» y no se construye nada.
  - En ambos modos rechaza peticiones de phishing, suplantación o acciones moralmente no deseables (ver sección 7).

### IA dentro de las apps
- **Qué pueden hacer:** las apps generadas pueden usar IA para entender, corregir, resumir, traducir, clasificar o explicar textos, y para leer el texto de una foto (también manuscrito, si se lee bien). No pueden crear imágenes, audio ni vídeo, ni leer PDF u otros documentos.
- **Cómo:** con la función `ia(pregunta, imagen=None)`, que reciben ya puesta (`app_ai.py`). Devuelve el texto de la respuesta. `imagen` es lo que devuelve `st.file_uploader` (PNG, JPG o WEBP, hasta 5 MB).
- **La clave nunca llega a la app:** la llamada la hace Yahoraque en el servidor y la app solo recibe la respuesta.
- **Instrucciones fijas** en cada llamada: [prompts/ia_apps.md](prompts/ia_apps.md). Hacer lo que pide la petición con el formato pedido (solo JSON si lo pide), no inventar, transcribir las imágenes letra a letra con sus errores y rechazar contenido prohibido.
- **Solo al pulsar un botón:** la página de JavaScript no puede llamar a `ia()`, así que una app con IA recoge los datos con widgets de Streamlit y la llama dentro de `if st.button(...)`. Si una app la llama al cargar, la prueba de arranque falla con «ia() solo se puede usar al pulsar un botón, no al cargar la app.» y la IA la reescribe.
- **Protección de la cuota gratuita**, que es la misma que construye las apps:
  - Las apps usan primero los modelos más ligeros (`flash-lite`, luego `flash`, luego `pro`). En la capa gratuita cada modelo tiene su propia cuota, así que no gastan la de los que usan el Analista y el Desarrollador.
  - **30 usos al día por app**, entre todas las personas que la usen (`app_ai.DAILY_LIMIT`). El contador está en memoria: se reinicia si se reinicia el servidor.
  - Pregunta de hasta 10.000 caracteres y respuesta de hasta 2.048 tokens.
  - Repetir exactamente la misma pregunta en la misma sesión reutiliza la respuesta y no gasta un uso.
- **Avisos** (salen en la app y la detienen en ese punto; el resto de Yahoraque sigue funcionando):
  - Límite: «Esta aplicación ya ha usado la IA 30 veces hoy, que es el máximo. Vuelve a intentarlo mañana.»
  - Sin IA: «La IA no está disponible ahora mismo. Inténtalo más tarde.»
  - Imagen: «La imagen tiene que ser PNG, JPG o WEBP.», «La imagen es demasiado grande: como mucho 5 MB.», «La imagen tiene que venir de un botón para subir archivos.»
  - Texto: «El texto es demasiado largo para la IA: como mucho 10.000 caracteres.»
- **Marca «Con IA»:** al guardar o restaurar una app se mira si su código llama a `ia()` y se apunta en `app.json` (`uses_ai`). Esas apps llevan una etiqueta morada «Con IA» (icono de destellos) en «Apps públicas», en la página de la app (la del dueño y la del enlace) y en «Usuarios» del admin. Al pasar el ratón: «Esta aplicación usa inteligencia artificial, hasta 30 veces al día.»
- **Requisitos:** el Analista añade la línea «Usa IA: No» o «Usa IA: Sí: <para qué>», avisa al cliente del límite diario y de lo que la IA no puede hacer, y el Desarrollador solo usa `ia()` si dice «Sí».
- **Honestidad:** ni el Analista ni el Desarrollador pueden simular funciones. El Analista avisa de lo que no se puede hacer o solo se hace de forma aproximada. El Desarrollador no puede fingir que lee una foto o corrige sin IA, ni rellenar con datos o textos de ejemplo sin decirlo, ni inventar valores (por ejemplo, una nota) si la respuesta de la IA no se puede leer.

## 5. Usuarios y permisos

| Acción | Invitado | Usuario registrado (nombre + PIN) | Admin |
|---|---|---|---|
| Ver el listado de apps públicas | Sí | Sí | Sí |
| Usar una app pública | Sí | Sí | Sí |
| Crear o modificar una app | No | Sí, solo la suya | Sí |
| Hacer pública o privada una app | No | Sí, solo la suya | Sí, cualquiera |
| Ver una app privada | No | Solo la suya | Sí |
| Borrar una app | No | Sí, solo la suya | Solo junto con su usuario |
| Borrar una cuenta | No | Sí, solo la suya | Sí, cualquiera |

- Cada usuario registrado tiene **una sola aplicación**. Para tener otra distinta, borra la suya y crea una nueva (o pide cambios en el chat).
- Hay un único admin (el propietario de Yahoraque). Puede borrar cualquier usuario junto con su aplicación.

### Acceso
- No hay login con Google. El usuario escribe **su nombre y un PIN**.
- **Primera vez:** en la pestaña «Soy nuevo» elige un nombre libre y un PIN de 4 a 8 números (lo escribe dos veces). Se separa de «Entrar» para que una errata en el nombre no cree un usuario nuevo sin querer.
- **Siguientes veces:** en la pestaña «Entrar» escribe su nombre y su PIN. Si no coinciden, no entra.
- **La sesión se recuerda 7 días** en ese navegador, también al recargar la página o cerrarlo:
  - Al entrar (con nombre y PIN, como admin o como invitado), el navegador guarda la cookie `yahoraque_sesion`. Contiene un token con el identificador, el nombre, el rol, la fecha de registro y la fecha de caducidad, firmado con HMAC (clave derivada de `PIN_SECRET`; para el admin, también de `ADMIN_PASSWORD`). Sin el secreto no se puede falsificar ni cambiar, por ejemplo, el rol.
  - Al abrir Yahoraque con una cookie válida se entra directamente, sin pedir el PIN.
  - **Quién lee la cookie:** Streamlit Cloud no pasa las cookies del navegador a la app (`st.context.cookies` llega vacío), así que un componente propio (`session_cookie.py`) la lee en el navegador y envía su valor a Python; también la escribe al entrar y la borra al salir. En local el servidor sí la ve y se usa directamente.
  - Puede verse un instante la pantalla de acceso al recargar, mientras el navegador envía la cookie.
  - La cookie deja de valer si: han pasado 7 días desde que se entró; el usuario se ha borrado; el usuario se ha borrado y otra persona se ha registrado con el mismo nombre (no coincide la fecha de registro); en el caso del admin, ha cambiado `ADMIN_PASSWORD` o `ADMIN_NAME`.
  - «Salir» borra la cookie y vuelve a la pantalla de acceso.
  - Los 7 días cuentan desde que se entró con el PIN; usar Yahoraque no los alarga.
- Los nombres no distinguen mayúsculas ni espacios al principio o al final: "Ana" y " ana " son el mismo usuario.
- El PIN nunca se guarda en claro. Se guarda su hash, combinado con un secreto (`PIN_SECRET`), para que no se pueda adivinar a partir del repositorio público.
- **PIN olvidado:** no hay recuperación. El admin puede borrar el usuario para que vuelva a registrarse.
- **Admin:** entra con el nombre `ADMIN_NAME` y la contraseña `ADMIN_PASSWORD`, ambos en los secretos.
- El nombre se guarda tal cual lo escribió el usuario (sin espacios al principio o al final) en su `user.json`, para que el admin pueda reconocerlo. Los usuarios registrados antes de este cambio aparecen con su hash en lugar del nombre.
- Se recomienda al usuario usar un alias en lugar de su nombre real.
- **"Privada" significa que solo se puede usar desde Yahoraque por su dueño**, no que el código sea secreto. El repositorio de GitHub es público (ver sección 11).

### Borrar mi cuenta
- En la barra lateral, debajo de «Salir», los usuarios registrados (no el invitado ni el admin) tienen «Borrar mi cuenta». Abre un desplegable: «Se borrarán tu cuenta, tu aplicación y todas sus versiones. No se puede deshacer.» y el botón «Sí, borrar mi cuenta».
- Al confirmar se borra su carpeta entera, se cierra la sesión (como «Salir», también la cookie) y se muestra «Tu cuenta se ha borrado.» en la pantalla de acceso. Con ese nombre se puede volver a registrar cualquiera.
- Si falla: «No hemos podido borrar tu cuenta. Inténtalo de nuevo en un rato.»

### Gestión de usuarios (solo admin)
- **Listado:** cuando entra el admin, la barra de la izquierda muestra, debajo del menú, todos los usuarios registrados ordenados por nombre (sin distinguir mayúsculas). El admin no aparece en la lista. Los invitados y los usuarios no ven esta lista.
- **Detalle:** al pulsar un usuario se abre la página «Usuarios» con su nombre, la fecha de registro, el nombre de su aplicación, el interruptor «Pública», la aplicación funcionando y sus requisitos (desplegables). Si no tiene: «Todavía no tiene aplicación».
- **Publicar u ocultar:** con el interruptor «Pública» el admin puede hacer pública o privada la app de cualquier usuario, igual que su dueño desde la página de su app. El cambio se guarda al momento, aparece o desaparece de «Apps públicas», y el dueño lo ve en su interruptor. Si no se puede guardar, el interruptor vuelve a su posición anterior y se muestra «No hemos podido cambiarlo. Inténtalo de nuevo en un rato.»
- **Borrado:** en esa página, «Borrar usuario» pide confirmación («Sí, borrar» / «Cancelar»). Al confirmar se elimina la carpeta del usuario entera (cuenta, requisitos y app) y desaparece de la lista. Con ese nombre se puede volver a registrar cualquiera.
- Si falla la lectura o el borrado, se muestra un mensaje sencillo y el error real va a los logs.
- La lista se guarda en memoria hasta 5 minutos para no hacer una llamada a GitHub por usuario en cada clic. Se refresca al momento cuando alguien se registra o se borra un usuario.

## 6. Flujo del usuario

1. El usuario entra con su nombre y PIN, o como invitado.
2. **Invitado:** ve el listado de apps públicas y puede abrirlas. No puede hacer nada más.
3. **Usuario registrado:** el menú de la izquierda depende de si ya tiene app:
   - **Sin app:** «Inicio» (página de inicio) abre directamente el chat del Analista, con el título «Crea tu aplicación». Después, «Apps públicas».
   - **Con app:** la primera entrada es **el nombre de la app** (página de inicio) y abre la app para usarla, con sus opciones (pública, compartir, borrar). Después, «Apps públicas». El chat para cambiarla **no está en el menú**: se abre con el enlace «Cambiar mi aplicación» de la página de la app, con el título «Cambiar <nombre>».
   - El admin ve lo mismo para su propia app, más «Usuarios».
   - Al terminar de construir la app, el usuario sigue en el chat con el mensaje «¡Tu aplicación <nombre> está lista!» y el menú ya muestra el nombre. Al borrarla, vuelve al chat y el menú vuelve a «Inicio».
4. Para crear o modificar su app, entra en **modo Analista**: describe lo que quiere y el sistema le hace preguntas hasta tener los requerimientos.
   - **Ideas de ejemplo:** si todavía no tiene app y el chat está vacío, aparecen cuatro botones con ideas del día a día de un docente: «📝 Corregir redacciones de idiomas», «🎲 Hacer grupos al azar», «❓ Un juego de preguntas para repasar» y «🧮 Calcular la nota media». Al pulsar uno, su texto se envía como primer mensaje al analista.
5. El sistema le muestra los requerimientos en lenguaje sencillo (las etiquetas en negrita, cada una en su línea) y le pregunta si quiere empezar, avisando de que «Construirla tarda 1 o 2 minutos.»
6. Al confirmar, el sistema construye la app y guarda una nueva versión.
7. El usuario elige si su app es pública o privada (ver «Nombre, visibilidad y borrado de la app»).
8. El usuario puede volver a una versión anterior de su app (ver «Versiones de la app»).

### Nombre, visibilidad y borrado de la app
- **Nombre:**
  - Al construir la app por primera vez, la IA le inventa un nombre: **una sola palabra inventada**, inspirada en los requisitos, fácil de pronunciar (por ejemplo, «Aguatín» para un contador de vasos de agua).
  - Solo letras (se aceptan tildes y ñ), como mucho 20, con la primera en mayúscula. Si la IA devuelve otra cosa, se quitan los caracteres que no son letras; si no queda nada, se usa «Miapp».
  - Al cambiar la app desde el chat, **el nombre se mantiene**.
  - No tiene que ser único: dos apps pueden llamarse igual, porque su dirección usa el hash del dueño.
  - El nombre es la entrada del menú y el título de la página de la app del dueño, y aparece en «Apps públicas», en su página y en el mensaje «¡Tu aplicación <nombre> está lista!».
- **Visibilidad:**
  - Una app nueva es **privada**. Cambiar la app desde el chat no cambia su visibilidad.
  - En la página de su app, el dueño tiene el interruptor «Pública» («Aparece en «Apps públicas» y la puede usar cualquiera, también sin cuenta»).
  - **Apps públicas:** página del menú para todos. Para los invitados es la página de inicio. Muestra las apps públicas ordenadas por nombre, con su nombre, la frase «Para qué sirve» de sus requisitos y un enlace «Abrir». Si no hay: «Todavía no hay aplicaciones públicas.»
  - **Página de cada app:** `/app?app=<hash del dueño>`.
  - **Enlace para compartir:** cuando la app es pública, el dueño ve en la página de su app la dirección completa (por ejemplo `https://yahoraque.streamlit.app/app?app=<hash>`) en un recuadro con botón de copiar. Se construye con el dominio por el que se entra, sin la ruta interna del marco de Streamlit Cloud (`/~/+/`).
  - **Abrir un enlace compartido:**
    - **Sin sesión y app pública:** se abre la app directamente como invitado, sin pantalla de acceso. Ese invitado no se recuerda: si después entra por la portada, ve la pantalla de acceso.
    - **Con sesión guardada:** entra con su usuario, no como invitado (también en Streamlit Cloud, donde la sesión llega del navegador un instante después).
    - **Sin sesión y app privada o inexistente:** se ve la pantalla de acceso; al entrar, se le lleva a la página de esa app (la ve si es su dueño o el admin).
  - Si la app no existe, o es privada y quien la abre no es su dueño ni el admin, se muestra «Esta aplicación no existe o no es pública.», el mismo mensaje en los dos casos, para no revelar qué apps existen.
  - El listado se guarda en memoria hasta 5 minutos y se refresca al momento cuando una app cambia, se publica, se oculta o se borra.
- **Borrado:**
  - En la página de su app, «Borrar mi aplicación» pide confirmación («Se borrará <nombre> y lo que pediste. Tu cuenta sigue. No se puede deshacer.» / «Sí, borrar» / «Cancelar»).
  - Al confirmar se borran el código, los datos de la app, los requisitos y todas sus versiones; la cuenta se mantiene y el usuario puede crear una app nueva, que recibirá un nombre nuevo.

### Mensajes divertidos mientras se espera a la IA
- En las dos esperas de la IA, en lugar de un texto fijo («Pensando…») se muestra una frase divertida junto al indicador de espera. Es solo un mensaje de espera: no se enseña lo que va razonando el modelo.
- **Cuándo:**
  - **Modo Analista:** desde que el usuario envía su mensaje hasta que llega la respuesta o aparece un error.
  - **Modo Desarrollador (construcción de la app):** desde que el usuario confirma los requisitos hasta que la app está lista o falla, incluidos los hasta 2 intentos de arreglo (sección 7, «Apps rotas»). La rotación sigue sin cortes de un intento a otro.
  - Al terminar la espera, la frase desaparece.
- **Misma lista** en los dos modos.
- **Rotación:** la primera frase sale al momento. Si la espera sigue, cambia cada 3 segundos.
- **Orden:** al azar, sin repetir ninguna hasta haber usado todas. Si la espera es tan larga que se acaban, se vuelve a barajar la lista y se empieza otra vuelta.
- **Tono:** humor blanco, apto para todos, en español, sin palabras técnicas. Ninguna frase menciona la IA, modelos o proveedores (ver sección 4), ni se parece al mensaje de error «Los astros no están alineados…», para no confundir una espera con un fallo.
- **Lista de frases (40):**
  1. Afilando los lápices…
  2. Despertando a las neuronas del turno de noche…
  3. Consultando con mi gato, que sabe mucho de esto…
  4. Preparándome un café bien cargado para pensar mejor…
  5. Ordenando tus ideas por colores…
  6. Buscando la pregunta perfecta debajo del sofá…
  7. Haciendo garabatos en una servilleta…
  8. Calentando motores… brum, brum…
  9. Pidiéndole consejo a mi abuela…
  10. Contando hasta diez para no precipitarme…
  11. Dándole vueltas, como a un buen cocido…
  12. Poniéndome las gafas de pensar…
  13. Sacudiendo la bola de cristal…
  14. Desenredando la madeja de ideas…
  15. Uniendo los puntos para ver el dibujo…
  16. Mirando por la ventana con cara de genio…
  17. Explicándoselo todo a mi pato de goma…
  18. Rascándome la cabeza con elegancia…
  19. Apuntándolo todo en mi libreta mágica…
  20. Probando ideas en la pizarra…
  21. Encendiendo la bombilla… un momento, que parpadea…
  22. Mezclando los ingredientes de tu receta…
  23. Consultándolo con la almohada, pero en versión rápida…
  24. Montando el puzle pieza a pieza…
  25. Hinchando el globo de las ideas…
  26. Pasando la aspiradora a las ideas malas…
  27. Echando cuentas con los dedos…
  28. Regando el huerto de las ideas…
  29. Sacándole brillo a tu idea…
  30. Buscando las llaves de la inspiración…
  31. Ensayando mi mejor respuesta delante del espejo…
  32. Dibujando planos con mucho cariño…
  33. Atando cabos sueltos…
  34. Pensando tan fuerte que casi se oye…
  35. Inflando las ruedas de la creatividad…
  36. Leyendo el manual de instrucciones del universo…
  37. Haciendo estiramientos mentales…
  38. Persiguiendo una idea que se me ha escapado…
  39. Afinando la guitarra antes de tocar tu canción…
  40. Haciendo malabares con tus ideas…

## 7. Funcionamiento técnico

### Ejecución de las apps
- Las apps de los usuarios se ejecutan **dentro de Yahoraque**.
- **Dónde se ven:** el dueño, en la entrada del menú con el nombre de la app; el admin, en «Usuarios» al elegir al usuario; todos (si es pública), en su página `/app?app=<hash del dueño>`. Siempre dentro de un marco, debajo del título con su nombre.
- **Apps en JavaScript siempre que sea posible:**
  - El fichero de la app es Python (`app.py`), pero su único trabajo es mostrar una página completa de HTML, CSS y JavaScript con una sola llamada `st.components.v1.html(HTML, height=...)`. Toda la lógica y la interacción (botones, cálculos, juegos, gráficos) van en JavaScript, así que responde al momento, sin recargar la página en el servidor.
  - Los widgets de Streamlit (`st.button`, `st.text_input`…) solo se usan si algo no se puede hacer en el navegador.
  - La página se muestra aislada (ver «Guardarraíles»): no puede usar `localStorage`, `sessionStorage`, `indexedDB` ni cookies (dan error), así que los datos viven en variables de JavaScript mientras está abierta.
  - **Estilo Yahoraque:** al mostrar cada app, Yahoraque añade al principio de su `<head>` Pico CSS 2.0.6 y un tema propio con los colores del logo (`--yq-blue` #2f7bf5, `--yq-green` #1cc39a, `--yq-yellow` #fdb924, `--yq-purple` #9a5cf6 como color principal, `--yq-navy` #13183f), letra Fredoka en títulos y botones y Nunito en el texto, y modo claro. La IA usa HTML semántico, que Pico ya pinta, escribe solo el CSS que falte y no redefine esos colores. Los estilos propios de la app van después, así que pueden ajustar el tema. (`app_theme.py`)
  - **Kit de librerías:** la app solo puede cargar estas, con la dirección y versión exactas: Chart.js 4.4.1 (gráficas), canvas-confetti 1.9.3 (celebraciones), Alpine.js 3.14.1 (interactividad) y p5.js 1.9.4 (juegos y dibujo). Si el código carga otra (`<script src>` o `<link href>` externos), la construcción lo trata como un error y la IA lo corrige. No llama a otras webs ni APIs.
  - Si la IA escribe `import streamlit…` (sobra, porque `st` ya está dado), esas líneas se quitan solas antes de revisar el código; `components.html(...)` funciona como `st.components.v1.html(...)`.
  - La IA elige la altura del marco (por defecto, 600 píxeles) para que se vea toda la app sin cortes; el marco no crece solo.
  - Números, fechas y dinero en el formato del idioma de los requisitos (en español: 1.234,56 € y 25/10/2026).
- **Las apps no recuerdan nada:** no guardan datos entre sesiones. Se avisa al usuario de esto durante el modo Analista.

### Guardarraíles
- **Seguridad:** el código generado no puede leer los secretos (clave de la IA, token de GitHub), ni el código de Yahoraque o de otras apps, ni cambiar quién es el usuario conectado. Se implementa en dos capas:
  1. **Revisión antes de ejecutar:** se rechaza el código que:
     - importa módulos fuera de esta lista: `calendar`, `collections`, `datetime`, `decimal`, `fractions`, `functools`, `itertools`, `json`, `math`, `random`, `re`, `statistics`, `textwrap` (tampoco `streamlit`, que ya viene dado como `st`);
     - usa `eval`, `exec`, `compile`, `open`, `getattr`, `setattr`, `delattr`, `globals`, `locals`, `vars`, `dir`, `type`, `object`, `super`, `input`, `help`, `breakpoint` o `memoryview`;
     - usa nombres o atributos que empiecen por guion bajo, `.format`/`.format_map`, o atributos de frames y código (`gi_`, `f_`, `co_`, `tb_`, `cr_`, `ag_`);
     - usa funciones de `st` fuera de la lista permitida (por ejemplo `st.secrets`, `st.sidebar`, `st.set_page_config`, `st.navigation`).
  2. **Ejecución limitada:**
     - Solo hay funciones básicas de Python (`len`, `range`, `sorted`…).
     - Los módulos permitidos llegan sin sus partes privadas ni otros módulos dentro.
     - `st` solo tiene las funciones permitidas, también en columnas, pestañas, formularios y demás contenedores.
     - Las claves de los widgets y `st.session_state` llevan el prefijo `app_<hash>_`, así que una app no puede leer ni cambiar el estado de Yahoraque (por ejemplo, el usuario conectado) ni el de otras apps.
     - `st.image`, `st.audio` y `st.video` solo aceptan direcciones web o datos, nunca rutas de ficheros del servidor.
     - `st.html` no puede usar `unsafe_allow_javascript`, que ejecutaría JavaScript en la página de Yahoraque (podría robar la cookie de sesión).
     - El HTML/JavaScript propio (`st.components.v1.html`) se muestra en un marco con origen propio (URL `data:`): su JavaScript no puede leer ni manejar la página de Yahoraque de quien la está viendo.
- Si una app que ya estaba guardada falla al ejecutarse, se muestra «La aplicación ha tenido un problema. Prueba a recargar la página.» y el error real va a los logs.
- **Contenido:** no se generan apps de phishing, de suplantación de marcas o personas, ni con fines moralmente no deseables.

### Almacenamiento y versiones
- Los datos de los usuarios se guardan en el **mismo repositorio de GitHub que Yahoraque**, pero en una rama aparte. El acceso se hace con un token guardado en los secretos.
- **Rama `master`:** es la que despliega Streamlit Cloud. Contiene solo el código de Yahoraque, nunca datos de usuarios.
- **Rama `datos`** (nombre configurable con `DATA_BRANCH`): contiene solo los datos de los usuarios. Yahoraque la lee y escribe a través de la API de GitHub; Streamlit no la despliega, así que guardar en ella no reinicia la plataforma.
  - Si la rama no existe, se crea sola, a partir de la rama principal del repositorio, la primera vez que se guarda algo.
  - El código de las apps de los usuarios se lee de esta rama en el momento de ejecutarlas, no de los ficheros desplegados.
- Cada usuario tiene **una carpeta `users/<hash del nombre>/`** en la rama `datos`. Dentro se guardan su cuenta (`user.json`: nombre, hash del PIN y fecha de registro), sus requisitos (`requisitos.md`), el código de su app (`app.py`) y los datos de la app (`app.json`: nombre, si es pública y la frase «Para qué sirve»).
- En desarrollo (`STORAGE_MODE=local`) la misma estructura se guarda en la carpeta `.data/` del disco, que está fuera de git.
- Cada guardado es un commit en la rama `datos`. Las versiones de cada app, en cambio, se guardan como ficheros propios (`users/<hash>/versiones/<fecha>.json`), para que funcionen igual en local y para listarlas con una sola llamada (ver «Versiones de la app»).
- Si dos guardados coinciden y chocan, se reintenta.
- Al borrar una cuenta o app se elimina su carpeta, pero **no se reescribe el historial de git**: las versiones antiguas siguen existiendo.
- **Reset total de la plataforma:** se borra la rama `datos`. Desaparecen todos los usuarios y sus apps; el código de Yahoraque no cambia.
### Versiones de la app
- **Qué es una versión:** cada construcción que funciona guarda una versión con su código y sus requisitos, en `users/<hash>/versiones/<id>.json` (`id` = fecha y hora UTC con microsegundos, que ordena las versiones). `app.json` guarda cuál es la actual (`version`).
- **Cuántas:** se guardan las **10 últimas**; al guardar la 11.ª se borra la más antigua.
- **Apps de antes de las versiones:** la primera vez que se reconstruyen, su versión anterior se guarda como «Versión 1», así no se pierde.
- **Dónde se ven:** en la página de la app del dueño, en el desplegable «Versiones (N)», de la más nueva a la más antigua. Cada una muestra «Versión N», la fecha y hora en la zona horaria del navegador (por ejemplo, 28/10/2026 20:25), «· la que tienes ahora» si es la actual, el botón «Lo que pediste» (sus requisitos) y, si no es la actual, el botón «Restaurar».
- **Restaurar:** la versión elegida pasa a ser la app actual (código, requisitos y frase «Para qué sirve»). No se borra ni se crea ninguna versión, así que se puede volver a la más nueva. El nombre y la visibilidad (pública o privada) no cambian. Se muestra «Has vuelto a la versión N.» y el chat del Analista parte de los requisitos restaurados.
- Solo el dueño puede restaurar. Si falla: «No hemos podido restaurarla. Inténtalo de nuevo en un rato.»

### Apps rotas
- Antes de dejar visible una nueva versión, se comprueba que pasa la revisión de los guardarraíles y que arranca sin errores.
- **La prueba de arranque** se hace en un proceso aparte, sin ningún secreto en su entorno, fuera de la carpeta del proyecto y con un límite de 30 segundos. Así una app rota o con un bucle infinito no bloquea Yahoraque. Solo se comprueba la primera carga de la app, no lo que pasa al pulsar sus botones.
- Si falla, la IA recibe el error y reescribe la app completa, **hasta 2 veces**.
- La app y sus requisitos solo se guardan si la nueva versión funciona. Si sigue fallando, se mantiene la última versión que funcionaba, los requisitos siguen pendientes en el chat y se muestra: «No hemos conseguido que la aplicación funcione. Si tenías una, sigue la anterior. Pulsa «¡Sí, adelante!» para intentarlo otra vez o cambia algo.»
- Si la IA rechaza la app por su contenido: «No podemos construir esta aplicación porque no cumple las normas de Yahoraque.»
- Si se agotan todos los modelos: «Los astros no están alineados, inténtalo más tarde.»
- Si todo va bien: «¡Tu aplicación <nombre> está lista!» con un enlace «Ver mi aplicación».

### Uso de la IA
- La elección del modelo y el cambio automático cuando falla se describen en la sección 4 («Elección del modelo»).
- Una app se genera en una sola petición, para que todo su código salga del mismo modelo. Si esa petición falla, se repite entera con el siguiente modelo.
- **Límite de construcciones:** cada usuario puede construir su app como mucho **10 veces al día** (cada pulsación de «¡Sí, adelante!» cuenta, salga bien o mal); el admin no tiene límite. Al llegar al tope: «Hoy ya has construido tu aplicación 10 veces, que es el máximo del día. Vuelve a intentarlo mañana.» El contador está en memoria y se reinicia si se reinicia el servidor. Los mensajes al analista no tienen límite.

## 8. Restricciones

- Coste cero: capa gratuita de la API de IA, de Streamlit Cloud y de GitHub.
- Las claves y la configuración sensible van en los secretos, nunca en el código:

  | Secreto | Para qué sirve |
  |---|---|
  | `GOOGLE_API_KEY` | Clave de la capa gratuita de la IA |
  | `GITHUB_TOKEN` | Token para guardar las apps en el repositorio |
  | `GITHUB_REPO` | Repositorio donde se guardan las apps |
  | `ADMIN_NAME` | Nombre con el que entra el admin |
  | `ADMIN_PASSWORD` | Contraseña del admin |
  | `PIN_SECRET` | Cadena aleatoria que se combina con los PIN antes de guardar su hash |
  | `STORAGE_MODE` | `local` (guarda en disco, para desarrollo) o `github` (producción) |
  | `DATA_BRANCH` | Rama donde se guardan los datos de los usuarios (por defecto, `datos`) |

  En local se leen de `.env`. En producción, de los secretos de Streamlit.
- Sin datos personales reales. Las carpetas usan el hash del nombre y se recomienda usar un alias.
- Lenguaje sencillo en toda la interfaz, para alguien sin conocimientos técnicos.

## 9. Criterios de aceptación

La app está bien si:

- Una app generada arranca sin errores, o si no, se mantiene visible la última versión que funcionaba.
- Un invitado ve el listado de apps públicas y puede abrirlas, pero no puede crear ni publicar.
- Un usuario registrado solo puede modificar su propia app.
- Tras entrar, al recargar la página se sigue dentro; tras pulsar «Salir», al recargar se ve la pantalla de acceso. Se cumple en Chrome, Firefox y Safari, y también cuando el servidor no ve las cookies, como en Streamlit Cloud (prueba automática: `tests/e2e_session.py`).
- Una app privada solo la ven su dueño y el admin.
- Un usuario puede volver a una versión anterior de su app: tras cambiarla, en «Versiones» aparecen las dos; al restaurar la primera, la app vuelve a ser la de antes, la lista marca esa como «la que tienes ahora» y la más nueva sigue disponible para volver.
- Tras restaurar, el chat «Cambiar <nombre>» muestra en «Lo que ya me pediste» los requisitos de la versión restaurada.
- Con 12 construcciones quedan 10 versiones (desaparecen las 2 más antiguas). Al borrar la app se borran también sus versiones.
- Un usuario puede borrar su app (su cuenta sigue y puede crear otra) y su propia cuenta: tras «Borrar mi cuenta», ve la pantalla de acceso con «Tu cuenta se ha borrado.» y ya no puede entrar con su nombre y PIN.
- Un usuario nuevo ve las cuatro ideas de ejemplo en el chat vacío; al pulsar una, el analista responde a ese texto.
- Con una app ya creada, al pedir un cambio en el chat, el analista no vuelve a preguntar lo que ya estaba en los requisitos, y los requisitos nuevos conservan todo lo anterior que no se ha pedido cambiar.
- Una app recién construida tiene un nombre de una sola palabra, solo letras, de 20 como mucho, y lo conserva al cambiarla desde el chat.
- Una app nueva es privada: un invitado no la ve en «Apps públicas» (y su enlace se comporta como en el caso límite 22).
- Al abrir el enlace para compartir de una app pública en un navegador sin sesión, se ve la app directamente, sin pantalla de acceso; con una sesión guardada, se ve con ese usuario.
- Al abrir el enlace de una app privada sin sesión y entrar como su dueño, se llega a la página de la app.
- Al activar «Pública», la app aparece en «Apps públicas» y un invitado puede abrirla y usarla; al desactivarlo, deja de aparecer y su enlace muestra «Esta aplicación no existe o no es pública.».
- Tras borrar su app, el usuario vuelve al chat «Crea tu aplicación», el menú muestra «Inicio» en lugar del nombre y la app desaparece de «Apps públicas».
- Un usuario sin app ve en el menú «Inicio» y «Apps públicas», y «Inicio» abre el chat. Con app, ve solo el nombre de la app (que la abre) y «Apps públicas»; «Cambiar mi aplicación» aparece solo dentro de la página de la app y abre el chat. Al recargar se mantiene.
- El admin ve en la barra de la izquierda a todos los usuarios registrados; los demás no ven esa lista.
- El admin puede abrir cualquier usuario y ver su aplicación (pública o privada), su nombre y sus requisitos.
- El admin puede hacer pública la app de otro usuario (un invitado la ve en «Apps públicas») y volver a hacerla privada (deja de verse).
- Tras confirmar el borrado, el usuario desaparece de la lista, su carpeta ya no existe y no puede entrar con su nombre y PIN.
- El código generado no consigue leer los secretos.
- Al confirmar unos requisitos, se construye una app que aparece en el menú del dueño con su nombre y en «Usuarios» del admin.
- Una app nueva se construye como página HTML/JavaScript dentro de `st.components.v1.html`, sin widgets de Streamlit salvo que haga falta, y funciona en Chrome y Safari dentro del marco aislado.
- Dentro de cualquier app están cargados Pico CSS y el tema de Yahoraque (títulos en Fredoka, variables `--yq-*`).
- Registrarse, guardar requisitos o borrar un usuario no cambia la rama `master` ni reinicia Yahoraque.
- Una app cuyo código llama a `ia()` lleva la marca «Con IA» en «Apps públicas», en su página y en «Usuarios»; una que no la llama, no.
- Mientras el analista piensa, y mientras se construye la app, se ve una frase de la lista de mensajes divertidos (sección 6); si la espera dura más de 3 segundos, la frase cambia, y no se repite ninguna hasta haber salido las 40.
- Al terminar la espera (respuesta, app lista o error), la frase desaparece.
- Se cumplen todos los casos límite de la tabla siguiente.

### Casos límite

Cada fila es un criterio de aceptación: la app está bien si, en ese caso, pasa lo que dice «Qué pasa». Los mensajes son literales.

| # | Caso | Qué pasa | Cómo se comprueba |
|---|---|---|---|
| **Acceso** | | | |
| 1 | Registrarse con un nombre que ya existe (sin distinguir mayúsculas ni espacios) o con el del admin | «Ese nombre ya está cogido. Prueba con otro.» No se crea nada. | Registrar «Ana» y después « ana »: el segundo da el mensaje y sigue habiendo un solo usuario. |
| 2 | Entrar con un PIN incorrecto | «Nombre o PIN incorrectos.» No entra. El mensaje es el mismo para usuarios y admin. | Con un usuario existente y un PIN distinto, no se accede a su cuenta. |
| 3 | Entrar con un nombre que no existe | «No hay nadie con ese nombre. Si eres nuevo, ve a «Soy nuevo».» | Entrar con un nombre nunca registrado. |
| 4 | Registrarse con un PIN no válido o mal repetido, o con campos vacíos | «El PIN tiene que tener entre 4 y 8 números.» / «Los dos PIN no coinciden.» / «Escribe un nombre.» / «Escribe tu nombre y tu PIN.» No se crea nada. | Probar `12`, `123456789`, `12ab`, dos PIN distintos y campos vacíos. |
| 5 | Cookie de sesión modificada a mano, de hace más de 7 días o de un usuario borrado | Se ve la pantalla de acceso, sin ningún error. | Cambiar el rol dentro del token, adelantar el reloj 8 días o borrar el usuario, y recargar. |
| 6 | GitHub no responde al entrar o registrarse | «No hemos podido comprobar tus datos. Inténtalo de nuevo en un rato.» El error real va a los logs. | Con un `GITHUB_TOKEN` no válido. |
| **IA** | | | |
| 7 | El modelo más potente falla (cuota, saturado, sin respuesta en 60 s) | Responde el siguiente modelo, sin que el usuario vea nada. El fallo se anota en los logs y ese modelo se aparta un tiempo (sección 4). | Con la cuota del mejor modelo agotada, el analista responde igual. |
| 8 | Fallan todos los modelos | «Los astros no están alineados, inténtalo más tarde.» En el chat, el mensaje sin respuesta desaparece. Al construir, no se guarda nada. | Con una `GOOGLE_API_KEY` no válida. |
| 9 | Petición prohibida (phishing, suplantar a una persona, marca o banco, engañar, algo ilegal u ofensivo) | El analista la rechaza con amabilidad, explica por qué y no escribe requisitos. Si aun así llega al desarrollador, este responde «RECHAZADA» y se muestra «No podemos construir esta aplicación porque no cumple las normas de Yahoraque.» No se guarda nada. | Pedir «una página igual que la de mi banco para pedir las claves». |
| 10 | Petición imposible (recordar datos, cuentas de usuario, enviar emails, cobrar, conectarse a servicios con clave, crear imágenes con IA, leer PDF) | El analista explica con palabras sencillas que no se puede y propone una alternativa. | Pedir «una app que me mande un email cada día». |
| **Construcción** | | | |
| 11 | La app generada no arranca | La IA recibe el error y la reescribe, hasta 2 veces. Si sigue fallando: «No hemos conseguido que la aplicación funcione. Si tenías una, sigue la anterior. Pulsa «¡Sí, adelante!» para intentarlo otra vez o cambia algo.» La anterior sigue intacta y los requisitos nuevos quedan pendientes en el chat, sin guardarse. | Forzar un error de Python en la respuesta del modelo. |
| 12 | Código peligroso: `import os`, `st.secrets`, `getattr`, `open`, atributos `__…__`, `unsafe_allow_javascript`… | La revisión lo rechaza antes de ejecutarlo; cuenta como fallo y la IA lo reescribe (caso 11). Los textos sí pueden contener `__`, habitual en JavaScript y CSS. | Ver la lista completa en «Guardarraíles». |
| 13 | La app carga una librería fuera del kit (por ejemplo, Tailwind) | Cuenta como fallo: «Librerías no permitidas (usa solo las de la lista): …» y la IA la quita. | Un `<script src>` a otra dirección. |
| 14 | Un modelo más flojo escribe `import streamlit` (sobra, `st` ya está dado) | Esas líneas se quitan solas y la app se construye normalmente. `components.html(...)` funciona como `st.components.v1.html(...)`. | Respuesta con `import streamlit as st` e `import streamlit.components.v1 as components`. |
| 15 | La app entra en un bucle infinito al arrancar | La prueba de arranque se corta a los 30 s («La aplicación tarda demasiado en arrancar (¿hay un bucle infinito?)»); cuenta como fallo y no se guarda. Yahoraque sigue respondiendo. | `while True: pass` en el código. |
| 16 | El nombre que inventa la IA no es una palabra válida | Se quitan los caracteres que no son letras y se corta a 20; si no queda nada, «Miapp». | `NOMBRE: Super-Calc 3000` da «Supercalc». |
| 17 | La app tiene un error de JavaScript | **No se detecta** al construir (riesgo asumido, sección 11): la app se guarda y se ve en blanco o a medias. El usuario puede pedir el arreglo en el chat o restaurar una versión anterior. | — |
| **Uso de las apps** | | | |
| 18 | Una app guardada falla al usarla (error de Python tras pulsar algo) | Dentro del marco de la app: «La aplicación ha tenido un problema. Prueba a recargar la página.» El resto de Yahoraque sigue funcionando y el error va a los logs. | Una app que divide entre cero al pulsar un botón. |
| 19 | Una app crea un widget con `key="user"` | Su clave pasa a ser `app_<hash>_user`: no cambia el usuario conectado. | Pulsarlo y comprobar que el rol sigue siendo el mismo. |
| 20 | Una app usa `st.video`, `st.audio` o `st.image` con una ruta de fichero del servidor | Error de la app; el fichero no se sirve al navegador. | `st.video("/app/.streamlit/secrets.toml")`. |
| 21 | El JavaScript de una app intenta leer o manejar la página de Yahoraque | No puede: corre en un marco con origen propio (`data:`). | Un script que busca botones de la página padre. |
| **Enlaces** | | | |
| 22 | Alguien abre el enlace de una app privada | Sin sesión: pantalla de acceso; al entrar como su dueño o el admin, llega a la app. Cualquier otro: «Esta aplicación no existe o no es pública.» | Ocultar una app y abrir su enlace en incógnito. |
| 23 | Alguien abre un enlace con un identificador que no existe | «Esta aplicación no existe o no es pública.», el mismo mensaje que para una privada, para no revelar qué apps existen. | `/app?app=noexiste`. |
| **Datos (GitHub)** | | | |
| 24 | Falla GitHub al guardar, cambiar «Pública», restaurar o borrar | «No hemos podido guardar tu aplicación…», «No hemos podido cambiarlo…» (el interruptor vuelve a lo guardado, sin recargas en bucle), «No hemos podido restaurarla…», «No hemos podido borrar…». En todos, lo anterior sigue como estaba. | Con un `GITHUB_TOKEN` sin permiso de escritura. |
| 25 | Dos guardados chocan en el mismo fichero | Se reintenta hasta 3 veces. | Dos pestañas guardando a la vez. |
| 26 | La rama `datos` no existe | Se crea sola en el primer guardado, a partir de la rama principal. | Borrarla y registrar un usuario. |
| 35 | Un usuario intenta construir su app por 11.ª vez en el día | «Hoy ya has construido tu aplicación 10 veces, que es el máximo del día. Vuelve a intentarlo mañana.» No se llama a la IA; los requisitos siguen pendientes. El admin no tiene límite. | Con 10 construcciones hechas, pulsar «¡Sí, adelante!». |
| **IA dentro de las apps** | | | |
| 27 | Una app con IA llega a su límite del día | «Esta aplicación ya ha usado la IA 30 veces hoy, que es el máximo. Vuelve a intentarlo mañana.» No se llama al modelo. | Con el límite a 2, la tercera pregunta distinta da el aviso. |
| 28 | La IA no está disponible para una app (cuota agotada, sin conexión) | «La IA no está disponible ahora mismo. Inténtalo más tarde.» en la app; el resto de Yahoraque sigue funcionando. | Con una `GOOGLE_API_KEY` no válida. |
| 29 | Una app llama a `ia()` al cargar, no al pulsar un botón | La prueba de arranque falla con «ia() solo se puede usar al pulsar un botón, no al cargar la app.» y la IA la reescribe (caso 11). | `r = ia("hola")` en la primera línea. |
| 30 | Se pulsa dos veces con la misma pregunta | La segunda vez se reutiliza la respuesta: no se gasta otro uso. | Contar las llamadas al modelo. |
| 31 | Imagen no válida (no es PNG/JPG/WEBP, más de 5 MB o no viene de `st.file_uploader`) | El aviso correspondiente (sección 4, «IA dentro de las apps»). | Subir un PDF o pasar bytes sueltos. |
| 32 | Leer una foto con faltas de ortografía | La IA la transcribe letra a letra, con sus errores, sin corregirlos al copiarla. | Foto con «Il fesait», «je va», «parceque»: el texto transcrito los conserva. |
| 33 | El cliente pide algo que no se puede hacer de verdad (por ejemplo, leer una foto sin IA) | El analista lo avisa antes de escribir los requisitos; la app no lo simula ni rellena con textos de ejemplo, y dice en pantalla qué parte no está disponible. | Revisar que el código no tenga datos inventados. |
| 34 | La respuesta de la IA no es el JSON esperado | La app muestra el texto de la IA tal cual con un aviso; nunca inventa valores (por ejemplo, una nota). | Forzar una respuesta que no sea JSON. |

## 10. Fuera de alcance (por ahora)

- Usar bases de datos o guardar datos en las apps de los usuarios.
- Exportar las aplicaciones.
- Más de una app por usuario.

## 11. Riesgos asumidos

- **Guardarraíles en el mismo proceso:** Python no permite aislar código de forma totalmente fiable dentro del mismo proceso. Un usuario malicioso podría llegar a saltarse los guardarraíles y leer los secretos. El más peligroso es el token de GitHub, porque con permiso de escritura podría modificar el código de Yahoraque.
- **El JavaScript no se prueba:** la prueba de arranque solo ejecuta el Python (en Streamlit Cloud no hay navegador para probar la página). Un error de JavaScript no se detecta al construir: la app se guarda y el usuario la ve en blanco o a medias. Se mitiga pidiendo a la IA que revise su JavaScript, y el usuario puede pedir el arreglo en el chat.
- **Altura fija del marco:** si la IA se queda corta, parte de la app queda cortada o con scroll interno.
- **Bucles infinitos al usar la app:** la prueba de arranque solo cubre la primera carga. Si el Python de una app entra en un bucle infinito al pulsar un botón, bloquea la sesión de quien la usa y gasta CPU del servidor hasta que se reinicia. Un bucle infinito en el JavaScript solo bloquea la pestaña de quien la usa, no el servidor.
- **Construcción lenta:** construir una app puede tardar más de un minuto, sobre todo si varios modelos están saturados y hay que probar el siguiente.
- **Cuota compartida:** las construcciones tienen límite (10 por usuario y día), pero los mensajes al analista no, y el contador está en memoria. Muchos usuarios a la vez podrían agotar la cuota gratuita del día; entonces aparece «Los astros no están alineados…».
- **Cuota de la IA de las apps:** el límite de 30 usos al día por app está en memoria (se reinicia con el servidor) y muchas apps a la vez podrían agotar la cuota de los modelos ligeros. Entonces las apps con IA muestran «La IA no está disponible…», pero el Analista y el Desarrollador siguen funcionando, porque usan otros modelos.
- **La IA de las apps se puede equivocar:** una corrección o una lectura de letra difícil pueden tener errores. Por eso las apps lo dicen («Qué no hará») y llevan la marca «Con IA».
- **Historial de git:** al borrar una cuenta, sus versiones antiguas siguen en el historial del repositorio.
- **Privacidad en la capa gratuita:** el proveedor de IA puede usar los datos enviados para entrenar sus modelos.
- **Repositorio público (es una práctica de máster):** "privada" significa que la app no aparece ni se puede abrir desde Yahoraque, pero su código, su nombre y si es pública se pueden leer en GitHub. Además, el nombre de cada usuario se lee en claro en su `user.json`. El código de los guardarraíles también es público. Se avisa al usuario de que no ponga información sensible en su app.
- **Sesión recordada:** quien use el mismo navegador entra como el último usuario durante 7 días, hasta que alguien pulse «Salir». Si alguien roba la cookie, puede entrar con ella hasta que caduque: no hay forma de cerrar a distancia la sesión de un usuario sin borrarlo.
- **PIN corto:** un PIN de pocos dígitos se puede adivinar probando muchas combinaciones desde la pantalla de acceso. Para una práctica se acepta sin límite de intentos.
- **Muchas llamadas a GitHub:** como los datos están en la rama `datos` y no en disco, cada lectura y cada guardado es una llamada a la API de GitHub, que tiene un límite por hora. Con muchos usuarios a la vez, o un admin con muchos usuarios en la lista, se puede llegar a ese límite.

## 12. Por decidir

Nada pendiente por ahora.

## 13. Despliegue

- **Ruta:** https://yahoraque.streamlit.app/
- **Fichero principal:** `app.py`. La app de Streamlit Cloud se desplegó con `init.py`, que solo ejecuta `app.py` en cada recarga; así no hace falta volver a desplegarla. En local, Docker arranca `app.py`.
