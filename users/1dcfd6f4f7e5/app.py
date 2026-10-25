import json

# Definimos el contenido HTML, CSS y JavaScript para la aplicación
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Cargamos Confetti para celebraciones -->
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
            font-family: system-ui, -apple-system, sans-serif;
            background: linear-gradient(135deg, #fdf4ff 0%, #fae8ff 50%, #f3e8ff 100%);
            color: #2e1065;
            padding: 1rem;
            margin: 0;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 2rem;
        }

        h1 {
            font-size: 2.5rem;
            background: linear-gradient(to right, #ec4899, #8b5cf6, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            font-weight: 800;
        }

        .subtitle {
            font-size: 1.1rem;
            color: #6b21a8;
        }

        .controls-card {
            background: white;
            border-radius: 1.5rem;
            padding: 1.5rem;
            box-shadow: 0 10px 25px -5px rgba(139, 92, 246, 0.15);
            margin-bottom: 2rem;
            border: 2px solid #f3e8ff;
        }

        .form-group {
            margin-bottom: 1.2rem;
        }

        label {
            display: block;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #581c87;
        }

        select {
            width: 100%;
            padding: 0.75rem 1rem;
            border-radius: 0.75rem;
            border: 2px solid #e9d5ff;
            background-color: #faf5ff;
            font-size: 1rem;
            color: #3b0764;
            font-weight: 500;
            outline: none;
            transition: all 0.2s;
        }

        select:focus {
            border-color: #8b5cf6;
            box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2);
        }

        .btn-generate {
            width: 100%;
            background: linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%);
            color: white;
            border: none;
            padding: 1rem;
            font-size: 1.2rem;
            font-weight: bold;
            border-radius: 0.75rem;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(236, 72, 153, 0.4);
            transition: transform 0.1s, box-shadow 0.1s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .btn-generate:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(236, 72, 153, 0.6);
        }

        .btn-generate:active {
            transform: translateY(1px);
        }

        /* Estilo Cartel de Cine */
        .poster {
            background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%);
            color: white;
            border-radius: 2rem;
            padding: 2.5rem;
            box-shadow: 0 20px 40px -10px rgba(30, 27, 75, 0.5);
            position: relative;
            overflow: hidden;
            border: 4px solid #f472b6;
            text-align: center;
            display: none;
            animation: fadeIn 0.5s ease-out forwards;
        }

        .poster.visible {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: scale(0.95); }
            to { opacity: 1; transform: scale(1); }
        }

        .poster::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(236,72,153,0.15) 0%, transparent 70%);
            pointer-events: none;
        }

        .badge {
            display: inline-block;
            background: #f472b6;
            color: #fff;
            padding: 0.4rem 1rem;
            border-radius: 2rem;
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px rgba(244, 114, 182, 0.4);
        }

        .poster-title {
            font-size: 2.8rem;
            font-weight: 900;
            line-height: 1.1;
            margin-bottom: 1.5rem;
            text-transform: uppercase;
            font-family: 'Impact', Charcoal, sans-serif;
            letter-spacing: 1px;
            color: #fef08a;
            text-shadow: 3px 3px 0px #db2777, 6px 6px 0px #7c3aed;
        }

        .poster-synopsis {
            font-size: 1.25rem;
            line-height: 1.6;
            margin-bottom: 2rem;
            color: #f3e8ff;
            font-style: italic;
            max-width: 90%;
            margin-left: auto;
            margin-right: auto;
        }

        .poster-footer {
            display: flex;
            justify-content: space-around;
            align-items: center;
            border-top: 1px dashed rgba(255,255,255,0.2);
            padding-top: 1.5rem;
            font-size: 0.95rem;
            color: #cbd5e1;
            flex-wrap: wrap;
            gap: 1rem;
        }

        .tag-pill {
            background: rgba(255, 255, 255, 0.1);
            padding: 0.3rem 0.8rem;
            border-radius: 1rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .cast-list {
            font-weight: bold;
            color: #f472b6;
        }
    </style>
</head>
<body>
    <div class="container" x-data="javijatorApp()">
        <header>
            <h1>✨ Generador de Pelis Los Javis ✨</h1>
            <p class="subtitle">Crea obras maestras modernas con folclóricas, misterio, lágrimas y temazos pop.</p>
        </header>

        <div class="controls-card">
            <div class="form-group">
                <label for="universe">🔮 Elige la temática principal:</label>
                <select id="universe" x-model="selectedUniverse">
                    <option value="random">¡Sorpréndeme (Aleatorio)! 🌟</option>
                    <option value="malasana">Misterio oscuro en Malasaña 🕵️‍♀️</option>
                    <option value="extraterrestres">Extraterrestres muy flamencos 👽💃</option>
                    <option value="folclorica">Folclórica espacial en Benidorm 🚀🎤</option>
                    <option value="operacion">Academia de talentos con drama místico 🎹✨</option>
                    <option value="costumbrismo">Costumbrismo mágico en el extrarradio 🏘️💖</option>
                </select>
            </div>

            <button class="btn-generate" @click="generateMovie()">
                <span>🎬 ¡Rodar Película!</span>
            </button>
        </div>

        <!-- Cartel Generado -->
        <div class="poster" :class="{ 'visible': movieGenerated }">
            <div class="badge" x-text="movie.genre"></div>
            <h2 class="poster-title" x-text="movie.title"></h2>
            <p class="poster-synopsis" x-text="movie.synopsis"></p>
            
            <div class="poster-footer">
                <div>✨ Estreno: <span x-text="movie.platform"></span></div>
                <div>⭐ Protagoniza: <span class="cast-list" x-text="movie.cast"></span></div>
                <div class="tag-pill" x-text="movie.ost"></div>
            </div>
        </div>
    </div>

    <!-- Cargamos Alpine.js -->
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.1/dist/cdn.min.js"></script>

    <script>
        function javijatorApp() {
            return {
                selectedUniverse: 'random',
                movieGenerated: false,
                movie: {
                    title: '',
                    synopsis: '',
                    genre: '',
                    platform: '',
                    cast: '',
                    ost: ''
                },
                
                databases: {
                    malasana: {
                        genre: 'Thriller Neón-Cañí',
                        platforms: ['Atresplayer Premium', 'Movistar+ Originales'],
                        casts: ['Macarena García y Brays Efe', 'Ana Castillo y Javier Calvo', 'Najwa Nimri con peluca rubia platino'],
                        osts: ['🎵 BSO: "Llantos en la Plazuela de San Ildefonso" por Rigoberta Bandini', '🎵 BSO: Versión trágica de un tema de Mecano'],
                        titles: [
                            'Las Niñas del 4º B',
                            'Secreto a Voces en Malasaña',
                            'Luces de Neón y Lágrimas de Rímel',
                            'El Misterio de la Croqueta Perdida'
                        ],
                        synopses: [
                            'Tres amigas que comparten piso en la calle Corredera baja de San Pablo descubren un portal dimensional dentro de un armario empotrado de Ikea, donde resuenan los grandes éxitos de Rocío Jurado mientras el mundo se acaba.',
                            'Tras una noche loca en un bar indie de Malasaña, una joven influencer despierta con superpoderes telepáticos que solo se activan cuando come churros con chocolate caliente y llora recordando a su ex.',
                            'Un detective con flequillo impoluto y gabardina rosa investiga la extraña desaparición de la mascota de un bar vegano, destapando una conspiración interdimensional de haters de OT.'
                        ]
                    },
                    extraterrestres: {
                        genre: 'Sci-Fi Costumbrista',
                        platforms: ['Netflix España', 'Filmin (Edición Especial)'],
                        casts: ['Loles León y un extraterrestre CGI', 'Amaia Romero y cameos sorpresa', 'Carmen Machi como abuela abducida'],
                        osts: ['🎵 BSO: "El OVNI que me trajo a Torrevieja" (Electro-copla)', '🎵 BSO: Sintetizadores ochenteros y palmas flamencas'],
                        titles: [
                            'Mi Abuela es de Alfa Centauri',
                            'Marcianos en el Rocío',
                            'Luces Extrañas sobre Albacete',
                            'El Contacto del Jamón'
                        ],
                        synopses: [
                            'Una nave nodriza aterriza por error en medio de la Feria de Abril. Los alienígenas quedan tan fascinados por el rebujito y los volantes que deciden cancelar la invasión terrestre para montar una caseta.',
                            'Un modesto matrimonio de jubilados en Benidorm acoge en su apartamento de la playa a un extraterrestre verde que resulta ser un fan absoluto de Raphael y experto en dominó.',
                            'Cuando una lluvia de meteoritos cae sobre un pueblo de Cuenca, los habitantes descubren que el mineral espacial potencia las voces de los coros parroquiales hasta niveles intergalácticos.'
                        ]
                    },
                    folclorica: {
                        genre: 'Melodrama Galáctico',
                        platforms: ['Prime Video', 'Atresplayer Premium'],
                        casts: ['Rossy de Palma y Belén Cuesta', 'Isabel Pantoja (en espíritu holográfico)', 'Macarena Ramírez y bailarines enmallados'],
                        osts: ['🎵 BSO: "Se me rompió el traje espacial por quererte"', '🎵 BSO: Copla futurista con autotune'],
                        titles: [
                            'Lágrimas de Luz en la Vía Láctea',
                            'La Faraona de Andrómeda',
                            'Copla Cósmica',
                            'Estrellas, Volantes y Soledad'
                        ],
                        synopses: [
                            'En el año 3050, la última folclórica viva cruza la galaxia a bordo de un crucero espacial con forma de abanico gigante, cantando coplas de desamor a planetas deshabitados.',
                            'Una gran diva de la copla es exiliada al planeta Marte tras un escándalo con Hacienda intergaláctica, donde monta el tablao más exclusivo del sistema solar.',
                            'Un joven aspirante a artista encuentra un viejo radiocasete que emite coplas grabadas por una nave perdida en un agujero negro en 1984.'
                        ]
                    },
                    operacion: {
                        genre: 'Musical Místico-Emocional',
                        platforms: ['Movistar+ Originales', 'Netflix España'],
                        casts: ['Los Javis (cameo autoconsciente)', 'Chenoa y un coro de ángeles modernos', 'Alumnos de academia ficticia y drama intenso'],
                        osts: ['🎵 BSO: "Cruzar la pasarela hacia el infinito"', '🎵 BSO: Balada al piano grabada en plano secuencia'],
                        titles: [
                            'La Última Nota de la Academia',
                            'Sálvate si Puedes, Cariño',
                            'Tragedia en el Conservatorio',
                            'El Canto de las Sirenas Autodidactas'
                        ],
                        synopses: [
                            'En una academia de canto aislada en la sierra madrileña, los concursantes descubren que el profesor principal es en realidad un espíritu atrapado desde los años 90 que solo liberará su talento si hacen un trío vocal perfecto.',
                            'Un reality show musical se convierte en una experiencia mística cuando todos los participantes empiezan a levitar durante los pases de micros de los lunes.',
                            'Nadie sabe qué pasa dentro de la habitación del piano de cola, pero quienes entran salen convertidos en estrellas del pop alternativo con una profunda crisis existencial.'
                        ]
                    },
                    costumbrismo: {
                        genre: 'Realismo Mágico Cañí',
                        platforms: ['Filmin', 'Atresplayer Premium'],
                        casts: ['Carmen Maura y Yolanda Ramos', 'Secun de la Rosa y Eva Ugarte', 'Todo el reparto de una corrala madrileña'],
                        osts: ['🎵 BSO: "Café, Colesterol y Esperanza"', '🎵 BSO: Rumba flamenca melancólica'],
                        titles: [
                            'El Portal de los Milagros',
                            'Vecinos del Tercer Tercera',
                            'La Mercería del Más Allá',
                            'Magia en el Barrio'
                        ],
                        synopses: [
                            'En una corrala castiza donde nunca pasa nada, las vecinas descubren que el felpudo del portal es capaz de conceder cualquier deseo a cambio de un cotilleo jugoso y una taza de café.',
                            'Una modesta mercería de barrio esconde en su trastienda un taller clandestino donde se arreglan los corazones rotos de todo el distrito centro usando hilo de oro y nostalgia.',
                            'Un apagón general en pleno agosto madrileño obliga a los vecinos a salir a la calle, donde una abuela empieza a contar historias que cobran vida en forma de proyecciones holográficas en las fachadas.'
                        ]
                    }
                },

                generateMovie() {
                    // Seleccionar categoría
                    let universeKey = this.selectedUniverse;
                    if (universeKey === 'random') {
                        const keys = Object.keys(this.databases);
                        universeKey = keys[Math.floor(Math.random() * keys.length)];
                    }

                    const db = this.databases[universeKey];
                    
                    // Elegir elementos aleatorios dentro de la base de datos elegida
                    this.movie.genre = db.genre;
                    this.movie.platform = db.platforms[Math.floor(Math.random() * db.platforms.length)];
                    this.movie.cast = db.casts[Math.floor(Math.random() * db.casts.length)];
                    this.movie.ost = db.osts[Math.floor(Math.random() * db.osts.length)];
                    this.movie.title = db.titles[Math.floor(Math.random() * db.titles.length)];
                    this.movie.synopsis = db.synopses[Math.floor(Math.random() * db.synopses.length)];

                    this.movieGenerated = true;

                    // Lanzar confeti fiestero estilo Javis
                    confetti({
                        particleCount: 100,
                        spread: 70,
                        origin: { y: 0.6 },
                        colors: ['#ec4899', '#8b5cf6', '#3b82f6', '#fef08a']
                    });
                }
            }
        }
    </script>
</body>
</html>
"""

# Renderizamos el componente con altura suficiente para que no haya scroll cortado
st.components.v1.html(HTML_CONTENT, height=850)
