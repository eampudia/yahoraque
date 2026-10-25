# Especificación · Yahoraque


## 1. Problema y usuario

- **Quién tiene el problema:** Cualquier persona sin conocimientos de desarrollo de software que quiera crear una aplicación web simple.
- **Cómo lo resuelve hoy:** Usando las herramientas que puedan existir o contratando un desarrollo.
- **Qué le molesta de cómo lo hace hoy:** La herramienta no hace todo lo que se necesita, o es caro de desarrollar.
- **Qué parte resuelve la IA:** La IA ayuda a la especificación y al desarrollo.

## 2. Qué hace el producto

1. Ayuda al usuario a saber qué necesita.
2. Desarrolla el código necesario.
3. Lo despliega de forma que sea accesible para el usuario.

## 3. Entradas y salidas

- El usuario describe su problema y el sistema le devuelve unos requerimientos en lenguaje humano, no técnico.
- Cuando el usuario los confirma, el sistema construye la aplicación.
- El usuario puede volver al chat en cualquier momento para pedir cambios.
- La aplicación queda accesible de forma pública o solo para su dueño.

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
- **Instrucciones para el modelo (system prompt):**
  - **Modo Analista:** se comporta como un analista tratando con un cliente. Hace las preguntas necesarias y, cuando ve que puede diseñar algo, muestra los requerimientos en lenguaje no técnico y pregunta si se empieza a construir.
  - **Modo Desarrollador:** se comporta como un programador senior. Recibe los requisitos confirmados (y el código actual de la app, si ya tenía una) y devuelve el código completo de la app en un único bloque, cumpliendo las reglas de los guardarraíles (sección 7), que se le explican en sus instrucciones. Si la app es de las prohibidas, responde «RECHAZADA» y no se construye nada.
  - En ambos modos rechaza peticiones de phishing, suplantación o acciones moralmente no deseables (ver sección 7).

## 5. Usuarios y permisos

| Acción | Invitado | Usuario registrado (nombre + PIN) | Admin |
|---|---|---|---|
| Ver el listado de apps públicas | Sí | Sí | Sí |
| Usar una app pública | Sí | Sí | Sí |
| Crear o modificar una app | No | Sí, solo la suya | Sí |
| Publicar una app | No | Sí, solo la suya | Sí |
| Ver una app privada | No | Solo la suya | Sí |
| Borrar su app o su cuenta | No | Sí | Sí, cualquiera |

- Cada usuario registrado tiene **una sola aplicación**.
- Hay un único admin (el propietario de Yahoraque). Puede borrar cualquier usuario junto con su aplicación.

### Acceso
- No hay login con Google. El usuario escribe **su nombre y un PIN**.
- **Primera vez:** en la pestaña «Soy nuevo» elige un nombre libre y un PIN de 4 a 8 números (lo escribe dos veces). Se separa de «Entrar» para que una errata en el nombre no cree un usuario nuevo sin querer.
- **Siguientes veces:** en la pestaña «Entrar» escribe su nombre y su PIN. Si no coinciden, no entra.
- La sesión dura mientras la pestaña del navegador esté abierta. Al recargar la página hay que volver a entrar.
- Los nombres no distinguen mayúsculas ni espacios al principio o al final: "Ana" y " ana " son el mismo usuario.
- El PIN nunca se guarda en claro. Se guarda su hash, combinado con un secreto (`PIN_SECRET`), para que no se pueda adivinar a partir del repositorio público.
- **PIN olvidado:** no hay recuperación. El admin puede borrar el usuario para que vuelva a registrarse.
- **Admin:** entra con el nombre `ADMIN_NAME` y la contraseña `ADMIN_PASSWORD`, ambos en los secretos.
- El nombre se guarda tal cual lo escribió el usuario (sin espacios al principio o al final) en su `user.json`, para que el admin pueda reconocerlo. Los usuarios registrados antes de este cambio aparecen con su hash en lugar del nombre.
- Se recomienda al usuario usar un alias en lugar de su nombre real.
- **"Privada" significa que solo se puede usar desde Yahoraque por su dueño**, no que el código sea secreto. El repositorio de GitHub es público (ver sección 11).

### Gestión de usuarios (solo admin)
- **Listado:** cuando entra el admin, la barra de la izquierda muestra, debajo del menú, todos los usuarios registrados ordenados por nombre (sin distinguir mayúsculas). El admin no aparece en la lista. Los invitados y los usuarios no ven esta lista.
- **Detalle:** al pulsar un usuario se abre la página «Usuarios» con su nombre, la fecha de registro y su aplicación. Mientras no exista la construcción de apps, se muestran sus requisitos guardados, o «Todavía no ha pedido ninguna aplicación» si no tiene.
- **Borrado:** en esa página, «Borrar usuario» pide confirmación («Sí, borrar» / «Cancelar»). Al confirmar se elimina la carpeta del usuario entera (cuenta, requisitos y app) y desaparece de la lista. Con ese nombre se puede volver a registrar cualquiera.
- Si falla la lectura o el borrado, se muestra un mensaje sencillo y el error real va a los logs.
- La lista se guarda en memoria hasta 5 minutos para no hacer una llamada a GitHub por usuario en cada clic. Se refresca al momento cuando alguien se registra o se borra un usuario.

## 6. Flujo del usuario

1. El usuario entra con su nombre y PIN, o como invitado.
2. **Invitado:** ve el listado de apps públicas y puede abrirlas. No puede hacer nada más.
3. **Usuario registrado:** ve su aplicación (o una pantalla para crearla si aún no tiene) y el listado de apps públicas.
4. Para crear o modificar su app, entra en **modo Analista**: describe lo que quiere y el sistema le hace preguntas hasta tener los requerimientos.
5. El sistema le muestra los requerimientos en lenguaje sencillo y le pregunta si quiere empezar.
6. Al confirmar, el sistema construye la app y guarda una nueva versión.
7. El usuario elige si su app es pública o privada.
8. El usuario puede volver a cualquier versión anterior de su app.

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
- **Dónde se ven ahora:** el dueño la ve en «Inicio», dentro de un marco, con el enlace «Crear o cambiar mi aplicación» encima. El admin la ve en la página «Usuarios» al elegir al usuario.
- **Pendiente:** cada app tendrá su propia ruta, cuyo nombre es el **hash del nombre** del usuario (el usuario no lo elige). Llegará con el listado de apps públicas.
- Las apps se generan en Python con Streamlit. Pueden incluir HTML y JavaScript propios, que se muestran aislados (ver «Guardarraíles»).
- **Las apps no recuerdan nada:** no guardan datos entre sesiones. Se avisa al usuario de esto durante el modo Analista.

### Guardarraíles
- **Seguridad:** el código generado no puede leer los secretos (clave de la IA, token de GitHub), ni el código de Yahoraque o de otras apps, ni cambiar quién es el usuario conectado. Se implementa en dos capas:
  1. **Revisión antes de ejecutar:** se rechaza el código que:
     - importa módulos fuera de esta lista: `calendar`, `collections`, `datetime`, `decimal`, `fractions`, `functools`, `itertools`, `json`, `math`, `random`, `re`, `statistics`, `textwrap` (tampoco `streamlit`, que ya viene dado como `st`);
     - usa `eval`, `exec`, `compile`, `open`, `getattr`, `setattr`, `delattr`, `globals`, `locals`, `vars`, `dir`, `type`, `object`, `super`, `input`, `help`, `breakpoint` o `memoryview`;
     - usa nombres o atributos que empiecen por guion bajo, `.format`/`.format_map`, o atributos de frames y código (`gi_`, `f_`, `co_`, `tb_`, `cr_`, `ag_`);
     - contiene textos con `__`;
     - usa funciones de `st` fuera de la lista permitida (por ejemplo `st.secrets`, `st.sidebar`, `st.set_page_config`, `st.navigation`).
  2. **Ejecución limitada:**
     - Solo hay funciones básicas de Python (`len`, `range`, `sorted`…).
     - Los módulos permitidos llegan sin sus partes privadas ni otros módulos dentro.
     - `st` solo tiene las funciones permitidas, también en columnas, pestañas, formularios y demás contenedores.
     - Las claves de los widgets y `st.session_state` llevan el prefijo `app_<hash>_`, así que una app no puede leer ni cambiar el estado de Yahoraque (por ejemplo, el usuario conectado) ni el de otras apps.
     - `st.image`, `st.audio` y `st.video` solo aceptan direcciones web o datos, nunca rutas de ficheros del servidor.
     - El HTML/JavaScript propio (`st.components.v1.html`) se muestra en un marco con origen propio (URL `data:`): su JavaScript no puede leer ni manejar la página de Yahoraque de quien la está viendo.
- Si una app que ya estaba guardada falla al ejecutarse, se muestra «La aplicación ha tenido un problema. Prueba a recargar la página.» y el error real va a los logs.
- **Contenido:** no se generan apps de phishing, de suplantación de marcas o personas, ni con fines moralmente no deseables.

### Almacenamiento y versiones
- Los datos de los usuarios se guardan en el **mismo repositorio de GitHub que Yahoraque**, pero en una rama aparte. El acceso se hace con un token guardado en los secretos.
- **Rama `master`:** es la que despliega Streamlit Cloud. Contiene solo el código de Yahoraque, nunca datos de usuarios.
- **Rama `datos`** (nombre configurable con `DATA_BRANCH`): contiene solo los datos de los usuarios. Yahoraque la lee y escribe a través de la API de GitHub; Streamlit no la despliega, así que guardar en ella no reinicia la plataforma.
  - Si la rama no existe, se crea sola, a partir de la rama principal del repositorio, la primera vez que se guarda algo.
  - El código de las apps de los usuarios se lee de esta rama en el momento de ejecutarlas, no de los ficheros desplegados.
- Cada usuario tiene **una carpeta `users/<hash del nombre>/`** en la rama `datos`. Dentro se guardan su cuenta (`user.json`: nombre, hash del PIN y fecha de registro), sus requisitos (`requisitos.md`) y el código de su app.
- En desarrollo (`STORAGE_MODE=local`) la misma estructura se guarda en la carpeta `.data/` del disco, que está fuera de git.
- Cada guardado es un commit, así que el historial de commits de la carpeta es el historial de versiones. Volver atrás es restaurar una versión anterior de esa carpeta.
- Si dos guardados coinciden y chocan, se reintenta.
- Al borrar una cuenta o app se elimina su carpeta, pero **no se reescribe el historial de git**: las versiones antiguas siguen existiendo.
- **Reset total de la plataforma:** se borra la rama `datos`. Desaparecen todos los usuarios y sus apps; el código de Yahoraque no cambia.
### Apps rotas
- Antes de dejar visible una nueva versión, se comprueba que pasa la revisión de los guardarraíles y que arranca sin errores.
- **La prueba de arranque** se hace en un proceso aparte, sin ningún secreto en su entorno, fuera de la carpeta del proyecto y con un límite de 30 segundos. Así una app rota o con un bucle infinito no bloquea Yahoraque. Solo se comprueba la primera carga de la app, no lo que pasa al pulsar sus botones.
- Si falla, la IA recibe el error y reescribe la app completa, **hasta 2 veces**.
- La app y sus requisitos solo se guardan si la nueva versión funciona. Si sigue fallando, se mantiene la última versión que funcionaba, los requisitos siguen pendientes en el chat y se muestra: «No hemos conseguido que la aplicación funcione. Si tenías una, sigue la anterior. Pulsa «¡Sí, adelante!» para intentarlo otra vez o cambia algo.»
- Si la IA rechaza la app por su contenido: «No podemos construir esta aplicación porque no cumple las normas de Yahoraque.»
- Si se agotan todos los modelos: «Los astros no están alineados, inténtalo más tarde.»
- Si todo va bien: «¡Tu aplicación está lista!» con un enlace «Ver mi aplicación».

### Uso de la IA
- La elección del modelo y el cambio automático cuando falla se describen en la sección 4 («Elección del modelo»).
- Una app se genera en una sola petición, para que todo su código salga del mismo modelo. Si esa petición falla, se repite entera con el siguiente modelo.
- No hay límite de mensajes por usuario.

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
- Con un PIN incorrecto no se puede entrar en la cuenta de otro usuario.
- Una app privada solo la ven su dueño y el admin.
- Un usuario puede volver a una versión anterior de su app.
- Un usuario puede borrar su app y su cuenta.
- El admin ve en la barra de la izquierda a todos los usuarios registrados; los demás no ven esa lista.
- El admin puede abrir cualquier usuario y ver su aplicación (o sus requisitos, mientras no se construyan apps).
- Tras confirmar el borrado, el usuario desaparece de la lista, su carpeta ya no existe y no puede entrar con su nombre y PIN.
- El código generado no consigue leer los secretos.
- Al confirmar unos requisitos, se construye una app que aparece en «Inicio» del dueño y en «Usuarios» del admin.
- Si la nueva versión no arranca tras 2 arreglos, se sigue viendo la anterior y los requisitos nuevos no se guardan.
- Una app con `import os`, `st.secrets`, `getattr`, `open` o atributos `__…__` se rechaza antes de ejecutarse.
- Una app con un widget `key="user"` no cambia el usuario conectado.
- `st.video`, `st.audio` o `st.image` con una ruta de fichero del servidor dan error.
- Una app con un bucle infinito no se guarda y Yahoraque sigue respondiendo.
- Registrarse, guardar requisitos o borrar un usuario no cambia la rama `master` ni reinicia Yahoraque.
- Con la rama `datos` sin crear, el primer guardado funciona y la crea.
- Si el modelo más potente falla, el usuario recibe la respuesta de otro modelo sin ver ningún error.
- Cuando se agota la IA, aparece el mensaje "Los astros no están alineados, inténtalo más tarde."
- Mientras el analista piensa, y mientras se construye la app, se ve una frase de la lista de mensajes divertidos (sección 6); si la espera dura más de 3 segundos, la frase cambia, y no se repite ninguna hasta haber salido las 40.
- Al terminar la espera (respuesta, app lista o error), la frase desaparece.

## 10. Fuera de alcance (por ahora)

- Usar bases de datos o guardar datos en las apps de los usuarios.
- Exportar las aplicaciones.
- Más de una app por usuario.

## 11. Riesgos asumidos

- **Guardarraíles en el mismo proceso:** Python no permite aislar código de forma totalmente fiable dentro del mismo proceso. Un usuario malicioso podría llegar a saltarse los guardarraíles y leer los secretos. El más peligroso es el token de GitHub, porque con permiso de escritura podría modificar el código de Yahoraque.
- **Bucles infinitos al usar la app:** la prueba de arranque solo cubre la primera carga. Si una app entra en un bucle infinito al pulsar un botón, bloquea la sesión de quien la usa y gasta CPU del servidor hasta que se reinicia.
- **Construcción lenta:** construir una app puede tardar más de un minuto, sobre todo si varios modelos están saturados y hay que probar el siguiente.
- **Sin límite de mensajes:** un único usuario muy activo puede agotar la cuota gratuita del día para todos.
- **Historial de git:** al borrar una cuenta, sus versiones antiguas siguen en el historial del repositorio.
- **Privacidad en la capa gratuita:** el proveedor de IA puede usar los datos enviados para entrenar sus modelos.
- **Repositorio público (es una práctica de máster):** "privada" significa que la app no aparece ni se puede abrir desde Yahoraque, pero su código se puede leer en GitHub. Además, el nombre de cada usuario se lee en claro en su `user.json`. El código de los guardarraíles también es público. Se avisa al usuario de que no ponga información sensible en su app.
- **PIN corto:** un PIN de pocos dígitos se puede adivinar probando muchas combinaciones desde la pantalla de acceso. Para una práctica se acepta sin límite de intentos.
- **Muchas llamadas a GitHub:** como los datos están en la rama `datos` y no en disco, cada lectura y cada guardado es una llamada a la API de GitHub, que tiene un límite por hora. Con muchos usuarios a la vez, o un admin con muchos usuarios en la lista, se puede llegar a ese límite.

## 12. Por decidir

- **Título visible en el listado público.** El hash no es legible. ¿Se muestra un título generado por la IA a partir de los requerimientos?

## 13. Despliegue

- **Ruta:** https://yahoraque.streamlit.app/
