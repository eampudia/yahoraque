import json

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trivial de Ciencia Express</title>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"></script>
    <style>
        :root {
            --primary: #4f46e5;
            --success: var(--yq-green, #10b981);
            --danger: #ef4444;
            --warning: var(--yq-yellow, #f59e0b);
            --background: #f8fafc;
            --card-bg: #ffffff;
            --text: #1e293b;
        }

        body {
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: transparent;
            color: var(--text);
            margin: 0;
            padding: 10px;
        }

        .container {
            max-width: 650px;
            margin: 0 auto;
        }

        .card {
            background: var(--card-bg);
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            padding: 24px;
            margin-bottom: 20px;
            border: 1px solid #e2e8f0;
        }

        /* Pantalla de inicio */
        .start-screen {
            text-align: center;
            padding: 20px;
        }
        .start-screen h1 {
            color: var(--primary);
            font-size: 2.2rem;
            margin-bottom: 10px;
        }
        .start-screen p {
            font-size: 1.1rem;
            color: #64748b;
            margin-bottom: 25px;
        }

        /* Cabecera del juego */
        .game-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            font-weight: bold;
            font-size: 1.1rem;
            background: #f1f5f9;
            padding: 10px 16px;
            border-radius: 12px;
        }

        .badge-score {
            color: var(--yq-blue, #2563eb);
        }

        /* Temporizador */
        .timer-container {
            width: 100%;
            height: 10px;
            background-color: #e2e8f0;
            border-radius: 5px;
            margin-bottom: 20px;
            overflow: hidden;
        }
        .timer-bar {
            height: 100%;
            width: 100%;
            background-color: var(--warning);
            transition: width 1s linear, background-color 0.5s ease;
        }
        .timer-bar.danger {
            background-color: var(--danger);
        }

        /* Pregunta */
        .question-title {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 20px;
            line-height: 1.4;
        }

        /* Opciones */
        .options-grid {
            display: grid;
            gap: 12px;
        }

        .option-btn {
            background-color: #ffffff;
            border: 2px solid #cbd5e1;
            border-radius: 12px;
            padding: 14px 18px;
            font-size: 1rem;
            font-weight: 600;
            text-align: left;
            cursor: pointer;
            transition: all 0.2s ease;
            color: var(--text);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .option-btn:hover:not(:disabled) {
            border-color: var(--primary);
            background-color: #eef2ff;
        }

        .option-btn.correct {
            background-color: #d1fae5 !important;
            border-color: var(--success) !important;
            color: #065f46;
        }

        .option-btn.incorrect {
            background-color: #fee2e2 !important;
            border-color: var(--danger) !important;
            color: #991b1b;
        }

        .option-btn:disabled {
            cursor: default;
        }

        /* Botones generales */
        .btn-main {
            background-color: var(--primary);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 14px 28px;
            font-size: 1.1rem;
            font-weight: bold;
            cursor: pointer;
            transition: opacity 0.2s;
            width: 100%;
            margin-top: 10px;
        }
        .btn-main:hover {
            opacity: 0.9;
        }

        /* Pantalla de Resultados */
        .results-screen {
            text-align: center;
            padding: 20px;
        }
        .results-screen h2 {
            font-size: 2rem;
            margin-bottom: 10px;
            color: var(--primary);
        }
        .final-score {
            font-size: 3rem;
            font-weight: 800;
            color: var(--yq-green, #10b981);
            margin: 15px 0;
        }
        .results-message {
            font-size: 1.2rem;
            color: #475569;
            margin-bottom: 25px;
        }

        .hidden {
            display: none !important;
        }
    </style>
</head>
<body>

<main class="container">
    <!-- PANTALLA DE INICIO -->
    <div id="startScreen" class="card start-screen">
        <h1>🧬 Trivial de Ciencia Express</h1>
        <p>¿Tienes 15 segundos por pregunta para demostrar lo que sabes? Responde 10 preguntas y consigue la máxima puntuación.</p>
        <button class="btn-main" onclick="startGame()">¡Comenzar Partida!</button>
    </div>

    <!-- PANTALLA DE JUEGO -->
    <div id="gameScreen" class="card hidden">
        <div class="game-header">
            <span id="questionCounter">Pregunta 1/10</span>
            <span class="badge-score">Puntos: <span id="currentScore">0</span></span>
        </div>
        
        <div class="timer-container">
            <div id="timerBar" class="timer-bar"></div>
        </div>

        <div id="questionText" class="question-title">Cargando pregunta...</div>

        <div class="options-grid" id="optionsContainer">
            <!-- Opciones inyectadas por JS -->
        </div>
    </div>

    <!-- PANTALLA DE RESULTADOS -->
    <div id="resultsScreen" class="card results-screen hidden">
        <h2>🎉 ¡Partida Finalizada!</h2>
        <p class="results-message" id="resultsMessage">Has completado el trivial científico.</p>
        <div class="final-score" id="finalScoreDisplay">0 / 10</div>
        <button class="btn-main" onclick="startGame()">Jugar de Nuevo</button>
    </div>
</main>

<script>
    const bancoPreguntas = [
        {
            pregunta: "¿Cuál es el planeta más caliente del Sistema Solar?",
            opciones: ["Mercurio", "Venus", "Marte", "Júpiter"],
            correcta: 1
        },
        {
            pregunta: "¿Qué gas abunda más en la atmósfera de la Tierra?",
            opciones: ["Oxígeno", "Dióxido de carbono", "Nitrógeno", "Hidrógeno"],
            correcta: 2
        },
        {
            pregunta: "¿Cuál es el órgano más grande del cuerpo humano?",
            opciones: ["El hígado", "El cerebro", "La piel", "El intestino delgado"],
            correcta: 2
        },
        {
            pregunta: "¿Qué partícula subatómica tiene carga eléctrica negativa?",
            opciones: ["Protón", "Neutrón", "Electrón", "Positrón"],
            correcta: 2
        },
        {
            pregunta: "¿A qué velocidad viaja aproximadamente la luz en el vacío?",
            opciones: ["300.000 km/s", "150.000 km/s", "1.080 km/h", "3.000.000 km/s"],
            correcta: 0
        },
        {
            pregunta: "¿Cómo se llama el proceso por el cual las plantas fabrican su propio alimento?",
            opciones: ["Respiración celular", "Fotosíntesis", "Transpiración", "Fermentación"],
            correcta: 1
        },
        {
            pregunta: "¿Cuál es el símbolo químico del Oro?",
            opciones: ["Ag", "Au", "Pb", "Fe"],
            correcta: 1
        },
        {
            pregunta: "¿Quién formuló la teoría de la relatividad?",
            opciones: ["Isaac Newton", "Galileo Galilei", "Albert Einstein", "Nikola Tesla"],
            correcta: 2
        },
        {
            pregunta: "¿Qué rama de la ciencia estudia los fósiles?",
            opciones: ["Geología", "Paleontología", "Arqueología", "Zoología"],
            correcta: 1
        },
        {
            pregunta: "¿Cuántos huesos tiene aproximadamente el cuerpo humano adulto?",
            opciones: ["150", "206", "300", "450"],
            correcta: 1
        },
        {
            pregunta: "¿Qué vitamina produce nuestro cuerpo al exponernos al sol?",
            opciones: ["Vitamina A", "Vitamina C", "Vitamina D", "Vitamina B12"],
            correcta: 2
        },
        {
            pregunta: "¿Cuál es el animal terrestre más rápido del mundo?",
            opciones: ["León", "Gacela", "Guepardo", "Caballo"],
            correcta: 2
        }
    ];

    let preguntasPartida = [];
    let indiceActual = 0;
    let puntuacion = 0;
    let temporizador = null;
    let tiempoRestante = 15;
    let respondido = false;

    function mezclarArray(array) {
        return [...array].sort(() => Math.random() - 0.5);
    }

    function startGame() {
        // Seleccionar 10 preguntas al azar
        preguntasPartida = mezclarArray(bancoPreguntas).slice(0, 10);
        indiceActual = 0;
        puntuacion = 0;

        document.getElementById("startScreen").classList.add("hidden");
        document.getElementById("resultsScreen").classList.add("hidden");
        document.getElementById("gameScreen").classList.remove("hidden");

        cargarPregunta();
    }

    function cargarPregunta() {
        if (indiceActual >= preguntasPartida.length) {
            finalizarPartida();
            return;
        }

        respondido = false;
        tiempoRestante = 15;
        
        const q = preguntasPartida[indiceActual];
        
        document.getElementById("questionCounter").innerText = `Pregunta ${indiceActual + 1}/10`;
        document.getElementById("currentScore").innerText = puntuacion;
        document.getElementById("questionText").innerText = q.pregunta;

        const container = document.getElementById("optionsContainer");
        container.innerHTML = "";

        q.opciones.forEach((opcion, index) => {
            const btn = document.createElement("button");
            btn.className = "option-btn";
            btn.innerHTML = `<span>${opcion}</span>`;
            btn.onclick = () => seleccionarRespuesta(index, btn);
            container.appendChild(btn);
        });

        iniciarTemporizador();
    }

    function iniciarTemporizador() {
        clearInterval(temporizador);
        const bar = document.getElementById("timerBar");
        bar.style.width = "100%";
        bar.classList.remove("danger");

        const inicio = Date.now();
        const duracion = 15000; // 15 segundos

        temporizador = setInterval(() => {
            if (respondido) {
                clearInterval(temporizador);
                return;
            }

            const transcurrido = Date.now() - inicio;
            const restante = Math.max(0, duracion - transcurrido);
            const porcentaje = (restante / duracion) * 100;

            bar.style.width = porcentaje + "%";

            if (porcentaje < 30) {
                bar.classList.add("danger");
            }

            if (restante <= 0) {
                clearInterval(temporizador);
                tiempoAgotado();
            }
        }, 50);
    }

    function seleccionarRespuesta(seleccionada, btnElement) {
        if (respondido) return;
        respondido = true;
        clearInterval(temporizador);

        const q = preguntasPartida[indiceActual];
        const botones = document.querySelectorAll(".option-btn");

        // Deshabilitar todos
        botones.forEach(b => b.disabled = true);

        if (seleccionada === q.correcta) {
            btnElement.classList.add("correct");
            puntuacion++;
            document.getElementById("currentScore").innerText = puntuacion;
        } else {
            btnElement.classList.add("incorrect");
            botones[q.correcta].classList.add("correct");
        }

        setTimeout(() => {
            indiceActual++;
            cargarPregunta();
        }, 1500);
    }

    function tiempoAgotado() {
        if (respondido) return;
        respondido = true;

        const q = preguntasPartida[indiceActual];
        const botones = document.querySelectorAll(".option-btn");
        botones.forEach(b => b.disabled = true);

        // Mostrar la correcta
        botones[q.correcta].classList.add("correct");

        setTimeout(() => {
            indiceActual++;
            cargarPregunta();
        }, 1500);
    }

    function finalizarPartida() {
        clearInterval(temporizador);
        document.getElementById("gameScreen").classList.add("hidden");
        document.getElementById("resultsScreen").classList.remove("hidden");

        document.getElementById("finalScoreDisplay").innerText = `${puntuacion} / 10`;

        let mensaje = "";
        if (puntuacion === 10) {
            mensaje = "¡Impecable! Eres una auténtica eminencia científica.";
            confetti({ particleCount: 120, spread: 70, origin: { y: 0.6 } });
        } else if (puntuacion >= 7) {
            mensaje = "¡Muy bien! Tienes unos conocimientos científicos geniales.";
            confetti({ particleCount: 60, spread: 50, origin: { y: 0.6 } });
        } else if (puntuacion >= 4) {
            mensaje = "¡No está mal! Sigue repasando para dominar la ciencia.";
        } else {
            mensaje = "¡A estudiar más! La ciencia requiere práctica y curiosidad.";
        }

        document.getElementById("resultsMessage").innerText = mensaje;
    }
</script>

</body>
</html>
"""

components.v1.html(HTML, height=650)
