<p align="center"><img src="assets/logo.png" alt="Yahoraque" width="220"></p>

# Yahoraque

Crea tu propia aplicación web sin saber programar.

**Pruébala:** https://yahoraque.streamlit.app/

## Qué hace

1. **Hablas con un analista.** Le cuentas con tus palabras qué quieres. Te hace preguntas y te devuelve los requisitos en lenguaje sencillo.
2. **La IA la construye.** Cuando confirmas los requisitos, la IA escribe la aplicación, le inventa un nombre y comprueba que arranca. Si falla, la arregla hasta 2 veces.
3. **La usas y la compartes.** Tu app aparece en el menú con su nombre. Puedes hacerla pública para que cualquiera la use con un enlace, sin cuenta, pedir cambios en el chat o borrarla.

Cada usuario entra con un nombre y un PIN y tiene una aplicación. Los invitados pueden usar las apps públicas. El admin ve y gestiona a todos los usuarios.

## Cómo funciona por dentro

- **Plataforma:** Python y [Streamlit](https://streamlit.io), desplegada en Streamlit Community Cloud.
- **IA:** modelos Gemini de la capa gratuita. Se usa el más potente disponible y, si falla, se pasa al siguiente sin que el usuario lo note.
- **Apps generadas:** páginas HTML, CSS y JavaScript dentro de un marco aislado, con el estilo de Yahoraque (Pico CSS) y un kit cerrado de librerías (Chart.js, canvas-confetti, Alpine.js, p5.js).
- **Seguridad:** el código generado pasa por guardarraíles antes de ejecutarse, para que no pueda leer los secretos ni tocar Yahoraque.
- **Datos:** usuarios y apps se guardan en la rama `datos` de este repositorio, nunca en `master`.

La especificación completa está en [especificacion.md](especificacion.md).

## Ejecutarla en local

Necesitas Docker.

```bash
cp .env.example .env   # rellena los valores
docker compose up
```

Abre http://localhost:8501. Con `STORAGE_MODE=local`, los datos se guardan en la carpeta `.data/` en lugar de GitHub.

Pruebas en navegador (Chrome, Firefox o Safari/WebKit):

```bash
docker compose --profile test run --rm e2e python e2e_session.py
```
