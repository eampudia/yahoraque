import json

HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reto de Inglés Básico</title>
  <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"></script>
  <style>
    body {
      padding: 0.5rem;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: #f8f9fa;
      color: #2d3436;
    }
    .game-container {
      max-width: 620px;
      margin: 0 auto;
    }
    .game-header {
      text-align: center;
      margin-bottom: 1rem;
    }
    .game-header h2 {
      margin-bottom: 0.2rem;
      color: var(--yq-navy, #2d3436);
      font-weight: 800;
    }
    .game-header p {
      color: #636e72;
      font-size: 0.95rem;
      margin-top: 0;
    }
    .status-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: white;
      border-radius: 12px;
      padding: 0.75rem 1rem;
      margin-bottom: 1rem;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
      border: 1px solid #e9ecef;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      padding: 0.35rem 0.75rem;
      border-radius: 20px;
      font-weight: 700;
      font-size: 0.85rem;
    }
    .badge-progress {
      background-color: #eaf2ff;
      color: var(--yq-blue, #0984e3);
    }
    .badge-streak {
      background-color: #fff9e6;
      color: #d63031;
    }
    .badge-score {
      background-color: #f3f0ff;
      color: var(--yq-purple, #6c5ce7);
    }
    .progress-bar-bg {
      height: 8px;
      background: #e9ecef;
      border-radius: 4px;
      overflow: hidden;
      margin-bottom: 1rem;
    }
    .progress-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, var(--yq-blue, #74b9ff), var(--yq-purple, #6c5ce7));
      width: 0%;
      transition: width 0.3s ease;
    }
    .question-card {
      background: white;
      border-radius: 16px;
      padding: 1.75rem 1.25rem;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.06);
      border: 1px solid #e9ecef;
      text-align: center;
    }
    .question-prompt {
      font-size: 0.9rem;
      color: #b2bec3;
      text-transform: uppercase;
      letter-spacing: 1px;
      font-weight: 700;
      margin-bottom: 0.5rem;
    }
    .question-word {
      font-size: 2.2rem;
      font-weight: 800;
      color: #2d3436;
      margin-bottom: 1.5rem;
      line-height: 1.2;
    }
    .options-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.8rem;
      margin-top: 1rem;
    }
    @media (max-width: 480px) {
      .options-grid {
        grid-template-columns: 1fr;
      }
    }
    .option-btn {
      width: 100%;
      padding: 0.9rem 1rem;
      font-size: 1.05rem;
      font-weight: 600;
      border-radius: 12px;
      border: 2px solid #dfe6e9;
      background: #ffffff;
      color: #2d3436;
      cursor: pointer;
      transition: all 0.15s ease-in-out;
      box-shadow: 0 2px 5px rgba(0,0,0,0.03);
      margin-bottom: 0;
    }
    .option-btn:hover:not(:disabled) {
      border-color: var(--yq-purple, #6c5ce7);
      background-color: #f8f7ff;
      transform: translateY(-2px);
    }
    .option-btn.correct {
      background-color: #00b894 !important;
      border-color: #00997b !important;
      color: white !important;
    }
    .option-btn.incorrect {
      background-color: #d63031 !important;
      border-color: #b22222 !important;
      color: white !important;
    }
    .option-btn:disabled {
      cursor: default;
      opacity: 0.9;
    }
    .feedback-message {
      height: 2.2rem;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 1.05rem;
      margin-top: 1rem;
    }
    .summary-card {
      text-align: center;
      background: white;
      border-radius: 16px;
      padding: 2.5rem 1.5rem;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
      border: 1px solid #e9ecef;
    }
    .summary-emoji {
      font-size: 4rem;
      margin-bottom: 0.5rem;
      line-height: 1;
    }
    .summary-stats {
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      gap: 1rem;
      margin: 1.5rem 0;
    }
    .stat-box {
      flex: 1;
      min-width: 110px;
      padding: 1rem;
      border-radius: 12px;
      background: #f8f9fa;
      border: 1px solid #e9ecef;
    }
    .stat-num {
      font-size: 1.8rem;
      font-weight: 800;
      color: var(--yq-purple, #6c5ce7);
    }
    .stat-label {
      font-size: 0.8rem;
      color: #6c757d;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-top: 0.2rem;
    }
    .btn-restart {
      background-color: var(--yq-green, #00b894);
      border: none;
      color: white;
      font-size: 1.1rem;
      padding: 0.8rem 2.2rem;
      border-radius: 30px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 4px 14px rgba(0, 184, 148, 0.35);
      transition: all 0.2s ease;
    }
    .btn-restart:hover {
      background-color: #00997b;
      transform: scale(1.03);
    }
  </style>
</head>
<body>
  <div class="game-container">
    <div class="game-header">
      <h2>🇬🇧 Reto de Inglés Básico 🇪🇸</h2>
      <p>Adivina la palabra correcta y suma la mayor cantidad de puntos</p>
    </div>

    <!-- PANTALLA DE JUEGO -->
    <div id="game-screen">
      <div class="progress-bar-bg">
        <div id="progress-fill" class="progress-bar-fill"></div>
      </div>

      <div class="status-bar">
        <span class="badge badge-progress" id="question-counter">Pregunta 1/10</span>
        <span class="badge badge-streak" id="streak-counter">🔥 Racha: 0</span>
        <span class="badge badge-score" id="score-counter">⭐ Puntos: 0</span>
      </div>

      <div class="question-card">
        <div class="question-prompt" id="question-prompt">¿CÓMO SE DICE EN INGLÉS?</div>
        <div class="question-word" id="question-word">Perro</div>

        <div class="options-grid" id="options-container">
          <!-- Botones dinámicos -->
        </div>

        <div class="feedback-message" id="feedback-msg"></div>
      </div>
    </div>

    <!-- PANTALLA RESUMEN -->
    <div id="summary-screen" style="display: none;">
      <div class="summary-card">
        <div class="summary-emoji" id="summary-emoji">🏆</div>
        <h3 id="summary-title" style="margin-bottom: 0.2rem;">¡Partida Completada!</h3>
        <p id="summary-subtitle" style="color: #636e72; font-size: 0.95rem;">¡Buen esfuerzo!</p>

        <div class="summary-stats">
          <div class="stat-box">
            <div class="stat-num" id="final-score">0</div>
            <div class="stat-label">Puntos Totales</div>
          </div>
          <div class="stat-box">
            <div class="stat-num" id="final-accuracy">0/10</div>
            <div class="stat-label">Aciertos</div>
          </div>
          <div class="stat-box">
            <div class="stat-num" id="max-streak">0</div>
            <div class="stat-label">Mejor Racha</div>
          </div>
        </div>

        <button class="btn-restart" onclick="startNewGame()">
          🔄 Volver a Jugar
        </button>
      </div>
    </div>
  </div>

  <script>
    const VOCABULARY = [
      { es: "Perro", en: "Dog", distractors: ["Cat", "Bird", "Rabbit"] },
      { es: "Gato", en: "Cat", distractors: ["Dog", "Mouse", "Tiger"] },
      { es: "Manzana", en: "Apple", distractors: ["Banana", "Orange", "Grape"] },
      { es: "Libro", en: "Book", distractors: ["Pen", "Pencil", "Paper"] },
      { es: "Casa", en: "House", distractors: ["Car", "Street", "Garden"] },
      { es: "Agua", en: "Water", distractors: ["Milk", "Juice", "Coffee"] },
      { es: "Rojo", en: "Red", distractors: ["Blue", "Green", "Yellow"] },
      { es: "Sol", en: "Sun", distractors: ["Moon", "Star", "Cloud"] },
      { es: "Amigo", en: "Friend", distractors: ["Teacher", "Doctor", "Brother"] },
      { es: "Gracias", en: "Thank you", distractors: ["Please", "Hello", "Goodbye"] },
      { es: "Feliz", en: "Happy", distractors: ["Sad", "Angry", "Tired"] },
      { es: "Escuchar", en: "Listen", distractors: ["Speak", "Read", "Write"] },
      { es: "Correr", en: "Run", distractors: ["Walk", "Jump", "Swim"] },
      { es: "Grande", en: "Big", distractors: ["Small", "Short", "Thin"] },
      { es: "Pequeño", en: "Small", distractors: ["Big", "Tall", "Long"] },
      { es: "Ventana", en: "Window", distractors: ["Door", "Wall", "Floor"] },
      { es: "Puerta", en: "Door", distractors: ["Window", "Roof", "Key"] },
      { es: "Ciudad", en: "City", distractors: ["Country", "Village", "Beach"] },
      { es: "Noche", en: "Night", distractors: ["Day", "Morning", "Afternoon"] },
      { es: "Buenos días", en: "Good morning", distractors: ["Good night", "Good evening", "Goodbye"] },
      { es: "Comida", en: "Food", distractors: ["Drink", "Water", "Fruit"] },
      { es: "Hora / Tiempo", en: "Time", distractors: ["Money", "Day", "Year"] },
      { es: "Trabajo", en: "Job", distractors: ["Game", "School", "Hobby"] },
      { es: "Familia", en: "Family", distractors: ["Friends", "People", "Team"] },
      { es: "Escuela", en: "School", distractors: ["Hospital", "Store", "Bank"] },
      { es: "Coche", en: "Car", distractors: ["Bus", "Bike", "Plane"] },
      { es: "Hermano", en: "Brother", distractors: ["Sister", "Father", "Mother"] },
      { es: "Verde", en: "Green", distractors: ["Red", "Yellow", "Black"] },
      { es: "Mesa", en: "Table", distractors: ["Chair", "Bed", "Desk"] },
      { es: "Leche", en: "Milk", distractors: ["Water", "Wine", "Tea"] },
      { es: "Pájaro", en: "Bird", distractors: ["Fish", "Dog", "Horse"] },
      { es: "Dinero", en: "Money", distractors: ["Time", "Work", "Price"] },
      { es: "Día", en: "Day", distractors: ["Night", "Week", "Month"] },
      { es: "Dormir", en: "Sleep", distractors: ["Eat", "Drink", "Play"] },
      { es: "Siempre", en: "Always", distractors: ["Never", "Sometimes", "Often"] },
      { es: "Nunca", en: "Never", distractors: ["Always", "Sometimes", "Rarely"] },
      { es: "Azul", en: "Blue", distractors: ["Red", "Yellow", "Green"] },
      { es: "Zapato", en: "Shoe", distractors: ["Shirt", "Pants", "Hat"] },
      { es: "Comprar", en: "Buy", distractors: ["Sell", "Pay", "Give"] },
      { es: "Flor", en: "Flower", distractors: ["Tree", "Grass", "Plant"] }
    ];

    let currentQuestions = [];
    let currentIndex = 0;
    let score = 0;
    let correctCount = 0;
    let streak = 0;
    let maxStreak = 0;
    let canAnswer = true;

    function shuffle(array) {
      const arr = [...array];
      for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
      }
      return arr;
    }

    function generateQuestions() {
      const selectedItems = shuffle(VOCABULARY).slice(0, 10);
      return selectedItems.map(item => {
        const isEsToEn = Math.random() > 0.4;
        let prompt, word, correctAnswer, options;

        if (isEsToEn) {
          prompt = "¿CÓMO SE DICE EN INGLÉS?";
          word = item.es;
          correctAnswer = item.en;
          options = shuffle([item.en, ...item.distractors]);
        } else {
          prompt = "¿QUÉ SIGNIFICA EN ESPAÑOL?";
          word = item.en;
          correctAnswer = item.es;
          const distractorsPool = VOCABULARY.filter(v => v.es !== item.es);
          const randomDistractors = shuffle(distractorsPool).slice(0, 3).map(v => v.es);
          options = shuffle([item.es, ...randomDistractors]);
        }

        return { prompt, word, correctAnswer, options };
      });
    }

    function startNewGame() {
      currentQuestions = generateQuestions();
      currentIndex = 0;
      score = 0;
      correctCount = 0;
      streak = 0;
      maxStreak = 0;
      canAnswer = true;

      document.getElementById('game-screen').style.display = 'block';
      document.getElementById('summary-screen').style.display = 'none';

      renderQuestion();
    }

    function updateStatsDisplay() {
      document.getElementById('question-counter').innerText = `Pregunta ${currentIndex + 1}/10`;
      document.getElementById('streak-counter').innerText = `🔥 Racha: ${streak}`;
      document.getElementById('score-counter').innerText = `⭐ Puntos: ${score.toLocaleString('es-ES')}`;

      const progressPercent = ((currentIndex) / 10) * 100;
      document.getElementById('progress-fill').style.width = `${progressPercent}%`;
    }

    function renderQuestion() {
      if (currentIndex >= currentQuestions.length) {
        showSummary();
        return;
      }

      updateStatsDisplay();
      const q = currentQuestions[currentIndex];

      document.getElementById('question-prompt').innerText = q.prompt;
      document.getElementById('question-word').innerText = q.word;
      document.getElementById('feedback-msg').innerText = '';

      const container = document.getElementById('options-container');
      container.innerHTML = '';

      q.options.forEach(optText => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.innerText = optText;
        btn.onclick = () => checkAnswer(optText, q.correctAnswer, btn);
        container.appendChild(btn);
      });

      canAnswer = true;
    }

    function checkAnswer(selected, correct, clickedBtn) {
      if (!canAnswer) return;
      canAnswer = false;

      const buttons = document.querySelectorAll('.option-btn');
      buttons.forEach(b => b.disabled = true);

      const feedbackEl = document.getElementById('feedback-msg');

      if (selected === correct) {
        clickedBtn.classList.add('correct');
        streak++;
        if (streak > maxStreak) maxStreak = streak;

        const bonus = (streak - 1) * 25;
        const pts = 100 + bonus;
        score += pts;
        correctCount++;

        feedbackEl.style.color = '#00b894';
        feedbackEl.innerText = streak > 1 
          ? `¡Excelente! +${pts} pts (🔥 Racha x${streak})` 
          : `¡Correcto! +${pts} pts`;

        if (streak >= 3 && typeof confetti === 'function') {
          confetti({ particleCount: 25, spread: 50, origin: { y: 0.75 } });
        }
      } else {
        clickedBtn.classList.add('incorrect');
        streak = 0;

        buttons.forEach(b => {
          if (b.innerText === correct) {
            b.classList.add('correct');
          }
        });

        feedbackEl.style.color = '#d63031';
        feedbackEl.innerText = `Incorrecto. La respuesta era "${correct}"`;
      }

      document.getElementById('streak-counter').innerText = `🔥 Racha: ${streak}`;
      document.getElementById('score-counter').innerText = `⭐ Puntos: ${score.toLocaleString('es-ES')}`;

      setTimeout(() => {
        currentIndex++;
        renderQuestion();
      }, 1300);
    }

    function showSummary() {
      document.getElementById('game-screen').style.display = 'none';
      document.getElementById('summary-screen').style.display = 'block';

      document.getElementById('final-score').innerText = score.toLocaleString('es-ES');
      document.getElementById('final-accuracy').innerText = `${correctCount}/10`;
      document.getElementById('max-streak').innerText = `${maxStreak}`;

      let emoji = "🏆";
      let title = "¡Partida Finalizada!";
      let subtitle = "¡Buen trabajo practicando tu vocabulario!";

      if (correctCount === 10) {
        emoji = "👑";
        title = "¡Puntuación Perfecta!";
        subtitle = "¡Impresionante! Has acertado 10 de 10 sin fallar ninguna.";
      } else if (correctCount >= 8) {
        emoji = "🌟";
        title = "¡Excelente Resultado!";
        subtitle = "Tienes un nivel de vocabulario fantástico.";
      } else if (correctCount >= 5) {
        emoji = "👍";
        title = "¡Buen Trabajo!";
        subtitle = "Estás progresando muy bien. Sigue practicando.";
      } else {
        emoji = "📚";
        title = "¡Sigue Entrenando!";
        subtitle = "Cada partida te ayuda a aprender nuevas palabras.";
      }

      document.getElementById('summary-emoji').innerText = emoji;
      document.getElementById('summary-title').innerText = title;
      document.getElementById('summary-subtitle').innerText = subtitle;

      if (correctCount >= 7 && typeof confetti === 'function') {
        confetti({ particleCount: 90, spread: 70, origin: { y: 0.6 } });
      }
    }

    window.onload = startNewGame;
  </script>
</body>
</html>
"""

st.components.v1.html(HTML, height=720, scrolling=True)
