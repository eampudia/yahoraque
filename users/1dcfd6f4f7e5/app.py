import json
import re

# Título y encabezado principal en Streamlit
st.title("✨ Generador de Pelis de Los Javis")
st.markdown("Crea películas únicas e intensas al estilo de **Javier Calvo y Javier Ambrossi** (*La Llamada*, *Paquita Salas*, *Veneno*, *La Mesías*): drama pop, devoción, música y costumbrismo.")

# Formulario para la idea o tema del usuario
idea_usuario = st.text_input(
    "💡 ¿Tienes alguna idea o tema en mente? (opcional)",
    placeholder="Ej: Extraterrestres en la Feria de Abril, karaoke embrujado en Gran Vía...",
    key="idea_input"
)

col_btn, _ = st.columns([1, 1])
with col_btn:
    generar = st.button("🎬 ¡Rodar Película!", type="primary", use_container_width=True, key="btn_generar")

if generar:
    prompt = f"""Eres un guionista estrella del universo cinematográfico de Los Javis (Javier Calvo y Javier Ambrossi).
Tu misión es inventar una película o serie ficticia con su estilo inconfundible: melodrama apasionado, cultura pop española, folclore, fe o misticismo, comedia costumbrista, personajes al borde del colapso emocional y versiones o temazos musicales épicos.

{f'La idea de partida del usuario es: "{idea_usuario.strip()}"' if idea_usuario.strip() else 'No hay idea de partida: inventa un concepto 100% libre, sorprendente, gracioso y emotivo al puro estilo Javis.'}

Devuelve ÚNICAMENTE un objeto JSON válido (sin texto antes ni después, sin marcas markdown de bloque ```json) con la siguiente estructura exactas:
{{
  "titulo": "Título llamativo y poético en español",
  "genero": "Nombre de género inventado estilo Javis (ej: Thriller Pop-Místico, Melodrama Flamenco-Galáctico, Dramedia de Culto)",
  "sinopsis": "Argumento de 3 a 4 frases explicando los personajes principales, el conflicto dramático y su revelación o clímax emocional.",
  "actores": ["Nombre Actor/Actriz Real 1 como Personaje 1", "Nombre Actor/Actriz Real 2 como Personaje 2", "Nombre Actor/Actriz Real 3 como Personaje 3"],
  "canciones": ["Título de canción conocida 1 con un toque gracioso o versión emotiva", "Título de canción conocida 2...", "Título de canción conocida 3...", "Título de canción conocida 4..."]
}}
"""
    with st.spinner("🔮 Los Javis están buscando la inspiración y escribiendo el guion..."):
        respuesta = ia(prompt)
        try:
            texto_limpio = respuesta.strip()
            if texto_limpio.startswith("```"):
                texto_limpio = re.sub(r"^```(?:json)?", "", texto_limpio)
                texto_limpio = re.sub(r"```$", "", texto_limpio).strip()
            
            data = json.loads(texto_limpio)
            st.session_state["pelicula"] = data
            st.session_state["error"] = None
        except Exception:
            st.session_state["pelicula"] = None
            st.session_state["error"] = respuesta

if st.session_state.get("error"):
    st.warning("La IA ha respondido con un formato libre. Aquí tienes la propuesta de guion:")
    st.markdown(st.session_state["error"])

if st.session_state.get("pelicula"):
    peli = st.session_state["pelicula"]
    
    html_code = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"></script>
    <style>
        :root {
            --yq-blue: #0284c7;
            --yq-green: #10b981;
            --yq-yellow: #f59e0b;
            --yq-purple: #8b5cf6;
            --yq-navy: #1e1b4b;
        }

        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 1rem;
            background: transparent;
            color: #1e1b4b;
        }

        .poster-card {
            background: linear-gradient(145deg, #1e1b4b 0%, #311042 50%, #4c1d95 100%);
            border-radius: 24px;
            padding: 2.5rem 2rem;
            color: #ffffff;
            box-shadow: 0 20px 40px rgba(30, 27, 75, 0.4);
            border: 3px solid #ec4899;
            position: relative;
            overflow: hidden;
            max-width: 800px;
            margin: 0 auto;
        }

        .header-center {
            text-align: center;
            margin-bottom: 2rem;
        }

        .badge-genre {
            display: inline-block;
            background: linear-gradient(90deg, #ec4899, #8b5cf6);
            color: #ffffff;
            padding: 0.5rem 1.2rem;
            border-radius: 50px;
            font-weight: 700;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin-bottom: 1.2rem;
            box-shadow: 0 4px 15px rgba(236, 72, 153, 0.4);
        }

        .poster-title {
            font-size: 2.5rem;
            font-weight: 900;
            margin: 0;
            line-height: 1.1;
            color: #fef08a;
            text-transform: uppercase;
            text-shadow: 3px 3px 0px #be185d, 6px 6px 0px #5b21b6;
            letter-spacing: 0.5px;
        }

        .section-box {
            background: rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 1.25rem 1.5rem;
            margin-bottom: 1.25rem;
            border: 1px solid rgba(255, 255, 255, 0.15);
        }

        .section-title {
            font-size: 1.1rem;
            font-weight: 800;
            color: #f472b6;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .synopsis-text {
            font-size: 1.05rem;
            line-height: 1.6;
            color: #f3e8ff;
            margin: 0;
            font-style: italic;
        }

        .cast-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 0.75rem;
        }

        .cast-item {
            background: rgba(255, 255, 255, 0.08);
            padding: 0.6rem 1rem;
            border-radius: 12px;
            font-size: 0.95rem;
            color: #fef08a;
            border-left: 3px solid #ec4899;
        }

        .music-list {
            list-style: none;
            padding: 0;
            margin: 0;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 0.6rem;
        }

        .music-item {
            background: rgba(255, 255, 255, 0.08);
            padding: 0.6rem 1rem;
            border-radius: 12px;
            font-size: 0.95rem;
            color: #a7f3d0;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            border-left: 3px solid #10b981;
        }

        .footer-tag {
            text-align: center;
            margin-top: 1.8rem;
            font-size: 0.85rem;
            color: rgba(255, 255, 255, 0.6);
            letter-spacing: 2px;
            text-transform: uppercase;
        }

        @media (max-width: 600px) {
            .poster-title {
                font-size: 1.8rem;
            }
            .poster-card {
                padding: 1.5rem 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="poster-card">
        <div class="header-center">
            <span class="badge-genre" id="genre"></span>
            <h1 class="poster-title" id="title"></h1>
        </div>

        <div class="section-box">
            <div class="section-title">📖 Argumento de la Película</div>
            <p class="synopsis-text" id="synopsis"></p>
        </div>

        <div class="section-box">
            <div class="section-title">🎭 Reparto Principal</div>
            <div class="cast-grid" id="cast"></div>
        </div>

        <div class="section-box">
            <div class="section-title">🎵 Banda Sonora Original</div>
            <ul class="music-list" id="music"></ul>
        </div>

        <div class="footer-tag">
            ✨ Una producción original del Universo Los Javis ✨
        </div>
    </div>

    <script>
        const movie = MOVIE_DATA_PLACEHOLDER;

        document.getElementById('genre').textContent = movie.genero || 'Película Javis';
        document.getElementById('title').textContent = movie.titulo || 'Sin título';
        document.getElementById('synopsis').textContent = movie.sinopsis || '';

        const castContainer = document.getElementById('cast');
        castContainer.innerHTML = '';
        (movie.actores || []).forEach(actor => {
            const div = document.createElement('div');
            div.className = 'cast-item';
            div.textContent = '⭐ ' + actor;
            castContainer.appendChild(div);
        });

        const musicContainer = document.getElementById('music');
        musicContainer.innerHTML = '';
        (movie.canciones || []).forEach(song => {
            const li = document.createElement('li');
            li.className = 'music-item';
            li.textContent = '🎤 ' + song;
            musicContainer.appendChild(li);
        });

        if (window.confetti) {
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 },
                colors: ['#ec4899', '#8b5cf6', '#fef08a', '#10b981']
            });
        }
    </script>
</body>
</html>"""

    html_renderizado = html_code.replace("MOVIE_DATA_PLACEHOLDER", json.dumps(peli))
    st.components.v1.html(html_renderizado, height=820)
