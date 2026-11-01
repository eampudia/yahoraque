import json

HTML_CODE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Desafío de Francés B2: Presente de Indicativo</title>
  <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"></script>
  <style>
    :root {
      --yq-blue: #1e88e5;
      --yq-green: #4caf50;
      --yq-yellow: #ffca28;
      --yq-purple: #7e57c2;
      --yq-navy: #1a237e;
      --yq-red: #e53935;
      --pico-primary: var(--yq-purple);
      --pico-primary-background: var(--yq-purple);
      --pico-border-radius: 12px;
      --pico-font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    body {
      background-color: #f8f9fa;
      margin: 0;
      padding: 12px;
      color: #2c3e50;
      font-size: 16px;
      font-family: var(--pico-font-family);
    }

    .app-card {
      max-width: 680px;
      margin: 0 auto;
      background: #ffffff;
      border-radius: 18px;
      padding: 24px;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.06);
      border: 1px solid rgba(0, 0, 0, 0.05);
      box-sizing: border-box;
    }

    .header-badge {
      display: inline-block;
      background-color: rgba(126, 87, 194, 0.12);
      color: var(--yq-purple);
      font-weight: 700;
      font-size: 0.85rem;
      padding: 4px 12px;
      border-radius: 20px;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    h1 {
      font-size: 1.65rem;
      font-weight: 800;
      color: var(--yq-navy);
      margin-top: 0;
      margin-bottom: 6px;
      line-height: 1.2;
    }

    .subtitle {
      color: #666;
      font-size: 0.95rem;
      margin-bottom: 20px;
      line-height: 1.4;
    }

    /* Top stats bar */
    .status-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #f1f3f9;
      padding: 10px 16px;
      border-radius: 12px;
      margin-bottom: 16px;
      font-weight: 600;
      font-size: 0.9rem;
    }

    .stat-box {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .stat-value {
      color: var(--yq-purple);
      font-size: 1.1rem;
      font-weight: 800;
    }

    /* Timer Progress */
    .timer-wrapper {
      width: 100%;
      height: 10px;
      background-color: #e0e0e0;
      border-radius: 10px;
      overflow: hidden;
      margin-bottom: 24px;
    }

    .timer-bar {
      height: 100%;
      width: 100%;
      background-color: var(--yq-blue);
      transition: width 0.1s linear, background-color 0.3s ease;
      border-radius: 10px;
    }

    .timer-warning {
      background-color: var(--yq-red) !important;
    }

    /* Question Box */
    .question-box {
      background: #fafbff;
      border: 2px solid #e2e8f0;
      border-radius: 14px;
      padding: 20px;
      margin-bottom: 20px;
      text-align: center;
    }

    .question-prompt {
      font-size: 0.9rem;
      color: #64748b;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      font-weight: 600;
    }

    .question-text {
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--yq-navy);
      line-height: 1.4;
      margin: 0;
    }

    /* Options Grid */
    .options-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 20px;
    }

    @media (max-width: 520px) {
      .options-grid {
        grid-template-columns: 1fr;
      }
    }

    .opt-btn {
      background-color: #ffffff;
      color: #334155;
      border: 2px solid #e2e8f0;
      border-radius: 12px;
      padding: 14px 16px;
      font-size: 1rem;
      font-weight: 600;
      text-align: left;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 10px;
      box-shadow: none;
      margin-bottom: 0;
      width: 100%;
      box-sizing: border-box;
    }

    .opt-btn:hover:not(:disabled) {
      border-color: var(--yq-purple);
      background-color: #f5f3ff;
      transform: translateY(-2px);
    }

    .opt-letter {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 26px;
      height: 26px;
      background-color: #f1f5f9;
      color: #475569;
      border-radius: 50%;
      font-size: 0.85rem;
      font-weight: 700;
      flex-shrink: 0;
    }

    /* Feedback Box */
    .feedback-box {
      border-radius: 12px;
      padding: 16px;
      margin-bottom: 20px;
      animation: fadeIn 0.3s ease;
      display: none;
    }

    .feedback-correct {
      background-color: #e8f5e9;
      border: 1px solid #a5d6a7;
      color: #1b5e20;
    }

    .feedback-incorrect {
      background-color: #ffebee;
      border: 1px solid #ef9a9a;
      color: #b71c1c;
    }

    .feedback-title {
      font-weight: 800;
      font-size: 1.05rem;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .feedback-explanation {
      font-size: 0.92rem;
      margin: 0;
      line-height: 1.4;
    }

    /* Option States */
    .opt-btn.correct {
      background-color: #e8f5e9 !important;
      border-color: var(--yq-green) !important;
      color: #1b5e20 !important;
    }

    .opt-btn.incorrect {
      background-color: #ffebee !important;
      border-color: var(--yq-red) !important;
      color: #b71c1c !important;
    }

    .opt-btn.correct .opt-letter {
      background-color: var(--yq-green);
      color: white;
    }

    .opt-btn.incorrect .opt-letter {
      background-color: var(--yq-red);
      color: white;
    }

    .action-btn {
      width: 100%;
      padding: 14px 20px;
      font-size: 1rem;
      font-weight: 700;
      border-radius: 12px;
      background-color: var(--yq-purple);
      border: none;
      color: white;
      cursor: pointer;
      transition: background-color 0.2s, transform 0.1s;
    }

    .action-btn:hover {
      background-color: #673ab7;
    }

    .action-btn:active {
      transform: scale(0.99);
    }

    /* Screens */
    .screen {
      display: none;
    }

    .screen.active {
      display: block;
    }

    /* Start Screen */
    .start-card {
      text-align: center;
      padding: 10px 0;
    }

    .rules-list {
      text-align: left;
      background: #f8fafc;
      padding: 16px 20px 16px 36px;
      border-radius: 12px;
      margin: 20px 0;
      font-size: 0.95rem;
      color: #334155;
    }

    .rules-list li {
      margin-bottom: 8px;
    }

    .rules-list li:last-child {
      margin-bottom: 0;
    }

    /* Summary Screen */
    .summary-card {
      text-align: center;
    }

    .score-badge-large {
      font-size: 3rem;
      font-weight: 900;
      color: var(--yq-purple);
      margin: 10px 0;
    }

    .summary-stats {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 10px;
      margin: 20px 0;
    }

    .stat-card {
      background: #f8fafc;
      border-radius: 12px;
      padding: 12px 8px;
      border: 1px solid #e2e8f0;
    }

    .stat-card-label {
      font-size: 0.75rem;
      color: #64748b;
      text-transform: uppercase;
      font-weight: 700;
    }

    .stat-card-val {
      font-size: 1.25rem;
      font-weight: 800;
      color: var(--yq-navy);
      margin-top: 4px;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }
  </style>
</head>
<body>

  <div class="app-card">

    <!-- Pantalla 1: Inicio -->
    <div id="screen-start" class="screen active">
      <div class="start-card">
        <span class="header-badge">Gramática B2 • Francés</span>
        <h1>Défi de Conjugaison</h1>
        <p class="subtitle">Pon a prueba tu dominio del <strong>Presente de Indicativo</strong> en nivel B2. ¿Serás capaz de resolver las excepciones e irregulares a tiempo?</p>

        <ul class="rules-list">
          <li>⏱️ Tienes <strong>15 segundos</strong> para responder cada pregunta.</li>
          <li>🎯 Verbos de nivel B2: irregulares, cambios ortográficos y excepciones.</li>
          <li>⚡ Ganas puntos extra por responder con rapidez.</li>
          <li>💡 Recibe explicación gramatical inmediata tras cada intento.</li>
        </ul>

        <button class="action-btn" onclick="startGame()">¡Empezar el Desafío!</button>
      </div>
    </div>

    <!-- Pantalla 2: Juego -->
    <div id="screen-quiz" class="screen">
      <div class="status-bar">
        <div class="stat-box">
          <span>Pregunta:</span>
          <span id="q-counter" class="stat-value">1/10</span>
        </div>
        <div class="stat-box">
          <span>Racha:</span>
          <span id="streak-counter" class="stat-value">🔥 0</span>
        </div>
        <div class="stat-box">
          <span>Puntos:</span>
          <span id="score-counter" class="stat-value">0</span>
        </div>
      </div>

      <div class="timer-wrapper">
        <div id="timer-bar" class="timer-bar"></div>
      </div>

      <div class="question-box">
        <div class="question-prompt">Completa la frase en presente:</div>
        <p id="question-text" class="question-text">Nous (acquérir) _______ de nouvelles compétences.</p>
      </div>

      <div id="options-container" class="options-grid">
        <!-- Generado por JS -->
      </div>

      <div id="feedback-box" class="feedback-box">
        <div id="feedback-title" class="feedback-title"></div>
        <p id="feedback-exp" class="feedback-explanation"></p>
      </div>

      <button id="next-btn" class="action-btn" style="display: none;" onclick="nextQuestion()">Siguiente pregunta ➔</button>
    </div>

    <!-- Pantalla 3: Resumen Final -->
    <div id="screen-end" class="screen">
      <div class="summary-card">
        <span class="header-badge">¡Desafío completado!</span>
        <h1 id="final-title">Résultat Final</h1>

        <div class="score-badge-large" id="final-score">0 pts</div>
        <p id="final-subtitle" style="color: #475569; font-weight: 600; margin-bottom: 20px;"></p>

        <div class="summary-stats">
          <div class="stat-card">
            <div class="stat-card-label">Aciertos</div>
            <div id="stat-correct" class="stat-card-val">0/10</div>
          </div>
          <div class="stat-card">
            <div class="stat-card-label">Precisión</div>
            <div id="stat-accuracy" class="stat-card-val">0%</div>
          </div>
          <div class="stat-card">
            <div class="stat-card-label">Mejor Racha</div>
            <div id="stat-streak" class="stat-card-val">0</div>
          </div>
        </div>

        <button class="action-btn" onclick="startGame()">Volver a Jugar 🔄</button>
      </div>
    </div>

  </div>

  <script>
    const QUESTIONS = [
      {
        sentence: "Nous _______ de nouvelles compétences chaque jour. (acquérir)",
        options: ["acquérons", "acquiérons", "acquissons", "acquirons"],
        correct: 0,
        explanation: "Le verbe 'acquérir' prend un accent grave sur le 'e' sauf aux 1re et 2e personnes du pluriel : nous acquérons, vous acquérez."
      },
      {
        sentence: "Tu _______ ce problème mathématique avec facilité. (résoudre)",
        options: ["résouds", "résous", "résolves", "résout"],
        correct: 1,
        explanation: "Les verbes en -soudre (résoudre, dissoudre) font leur terminaison en -s, -s, -t au singulier : je résous, tu résous, il résout."
      },
      {
        sentence: "Ils _______ les clients avec des arguments solides. (convaincre)",
        options: ["convaincent", "convainctionnent", "convainquent", "convainces"],
        correct: 2,
        explanation: "Le verbe 'convaincre' prend 'qu' au pluriel : nous convainquons, vous convainquez, ils convainquent."
      },
      {
        sentence: "Vous _______ dans la salle d'attente s'il vous plaît. (s'asseoir)",
        options: ["vous asseyez", "vous assisez", "vous asseoiriez", "vous assiez"],
        correct: 0,
        explanation: "Le verbe 's'asseoir' a deux formes usuelles au présent. La plus courante : je m'assieds... vous vous asseyez."
      },
      {
        sentence: "Le meunier _______ le grain pour faire de la farine. (moudre)",
        options: ["moud", "mous", "moue", "moudt"],
        correct: 0,
        explanation: "Au présent : je mouds, tu mouds, il moud, nous moulons, vous moulez, ils moulent."
      },
      {
        sentence: "Ils _______ la preuve au dossier de candidature. (joindre)",
        options: ["joindent", "joincent", "joignent", "joingnent"],
        correct: 2,
        explanation: "Les verbes en -eindre, -aindre, -oindre gardent 'gn' devant les voyelles au pluriel : ils joignent."
      },
      {
        sentence: "Elle _______ les détails de loin grâce à sa vue. (apercevoir)",
        options: ["aperceve", "aperçoit", "apercevoit", "aperçoive"],
        correct: 1,
        explanation: "Apercevoir prend une cédille devant le 'o' au singulier : j'aperçois, tu aperçois, elle aperçoit."
      },
      {
        sentence: "Nous _______ les murs de la cuisine en bleu marine. (peindre)",
        options: ["peignons", "peindrons", "peintons", "peignissons"],
        correct: 0,
        explanation: "Pour les verbes en -eindre comme peindre : nous peignons, vous peignez, ils peignent."
      },
      {
        sentence: "Il _______ le silence avec une réponse inattendue. (rompre)",
        options: ["romp", "rompe", "rompt", "rompit"],
        correct: 2,
        explanation: "Le verbe 'rompre' garde son 't' à la 3e personne du singulier au présent : il rompt."
      },
      {
        sentence: "Vous _______ l'injustice sous toutes ses formes. (haïr)",
        options: ["haïez", "haïssez", "haïtes", "haïssons"],
        correct: 1,
        explanation: "Le tréma de 'haïr' disparaît au singulier (je hais) mais réapparaît au pluriel avec le suffixe -iss- : vous haïssez."
      },
      {
        sentence: "Les enfants _______ des fleurs sauvages dans le parc. (cueillir)",
        options: ["cueillissent", "cueillent", "cueillon", "cueilleront"],
        correct: 1,
        explanation: "Bien que du 3e groupe, 'cueillir' se conjugue au présent comme un verbe du 1er groupe (-e, -es, -e, -ons, -ez, -ent)."
      },
      {
        sentence: "Elles _______ de voter lors du premier tour. (s'abstenir)",
        options: ["s'abstiennent", "s'abstenent", "s'abstenissent", "s'abstienent"],
        correct: 0,
        explanation: "Comme 'venir', les verbes en -tenir prennent 'ienne' à la 3e personne du pluriel : elles s'abstiennent."
      },
      {
        sentence: "Tu _______ ce contrat sans la moindre hésitation. (conclure)",
        options: ["conclues", "concluds", "conclus", "concluz"],
        correct: 2,
        explanation: "Les verbes en -clure se conjuguent au présent : je conclus, tu conclus, il conclut."
      },
      {
        sentence: "Ce moteur _______ les pales de la grande éolienne. (mouvoir)",
        options: ["meut", "mouve", "moud", "meus"],
        correct: 0,
        explanation: "'Mouvoir' devient 'meut' à la 3e personne du singulier au présent de l'indicatif : il meut."
      },
      {
        sentence: "Le champion _______ tous ses rivaux avec facilité. (vaincre)",
        options: ["vainque", "vainct", "vainc", "vaince"],
        correct: 2,
        explanation: "À la 3e personne du singulier de 'vaincre', le 'c' demeure sans 't' : il vainc."
      }
    ];

    const MAX_QUESTIONS = 10;
    const TIME_PER_QUESTION = 15;

    let currentQuestions = [];
    let currentIndex = 0;
    let score = 0;
    let streak = 0;
    let maxStreak = 0;
    let correctCount = 0;
    let timer = null;
    let timeLeft = TIME_PER_QUESTION;
    let isAnswered = false;

    function shuffle(array) {
      return [...array].sort(() => Math.random() - 0.5);
    }

    function showScreen(id) {
      document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
      document.getElementById(id).classList.add('active');
    }

    function startGame() {
      currentQuestions = shuffle(QUESTIONS).slice(0, MAX_QUESTIONS);
      currentIndex = 0;
      score = 0;
      streak = 0;
      maxStreak = 0;
      correctCount = 0;

      showScreen('screen-quiz');
      loadQuestion();
    }

    function loadQuestion() {
      isAnswered = false;
      const q = currentQuestions[currentIndex];

      document.getElementById('q-counter').textContent = `${currentIndex + 1}/${MAX_QUESTIONS}`;
      document.getElementById('score-counter').textContent = score;
      document.getElementById('streak-counter').textContent = `🔥 ${streak}`;
      document.getElementById('question-text').textContent = q.sentence;

      const container = document.getElementById('options-container');
      container.innerHTML = '';

      const letters = ['A', 'B', 'C', 'D'];
      q.options.forEach((opt, idx) => {
        const btn = document.createElement('button');
        btn.className = 'opt-btn';
        btn.onclick = () => selectOption(idx);
        btn.innerHTML = `<span class="opt-letter">${letters[idx]}</span><span>${opt}</span>`;
        container.appendChild(btn);
      });

      document.getElementById('feedback-box').style.display = 'none';
      document.getElementById('next-btn').style.display = 'none';

      startTimer();
    }

    function startTimer() {
      clearInterval(timer);
      timeLeft = TIME_PER_QUESTION;
      updateTimerBar();

      const startTime = Date.now();
      const totalMs = TIME_PER_QUESTION * 1000;

      timer = setInterval(() => {
        const elapsed = Date.now() - startTime;
        const remainingMs = Math.max(0, totalMs - elapsed);
        timeLeft = remainingMs / 1000;

        updateTimerBar();

        if (remainingMs <= 0) {
          clearInterval(timer);
          handleTimeout();
        }
      }, 50);
    }

    function updateTimerBar() {
      const bar = document.getElementById('timer-bar');
      const pct = (timeLeft / TIME_PER_QUESTION) * 100;
      bar.style.width = `${pct}%`;

      if (timeLeft <= 4) {
        bar.classList.add('timer-warning');
      } else {
        bar.classList.remove('timer-warning');
      }
    }

    function selectOption(index) {
      if (isAnswered) return;
      isAnswered = true;
      clearInterval(timer);

      const q = currentQuestions[currentIndex];
      const buttons = document.querySelectorAll('.opt-btn');
      buttons.forEach(btn => btn.disabled = true);

      const isCorrect = index === q.correct;
      const feedbackBox = document.getElementById('feedback-box');
      const feedbackTitle = document.getElementById('feedback-title');
      const feedbackExp = document.getElementById('feedback-exp');

      if (isCorrect) {
        buttons[index].classList.add('correct');
        streak++;
        if (streak > maxStreak) maxStreak = streak;
        correctCount++;

        const timeBonus = Math.round(timeLeft * 10);
        const streakBonus = (streak > 1) ? streak * 15 : 0;
        const ptsGained = 100 + timeBonus + streakBonus;
        score += ptsGained;

        feedbackBox.className = 'feedback-box feedback-correct';
        feedbackTitle.innerHTML = `✅ ¡Correcto! (+${ptsGained} pts)`;
      } else {
        buttons[index].classList.add('incorrect');
        buttons[q.correct].classList.add('correct');
        streak = 0;

        feedbackBox.className = 'feedback-box feedback-incorrect';
        feedbackTitle.innerHTML = `❌ Incorrecto`;
      }

      document.getElementById('score-counter').textContent = score;
      document.getElementById('streak-counter').textContent = `🔥 ${streak}`;

      feedbackExp.textContent = q.explanation;
      feedbackBox.style.display = 'block';

      document.getElementById('next-btn').style.display = 'block';
    }

    function handleTimeout() {
      if (isAnswered) return;
      isAnswered = true;

      const q = currentQuestions[currentIndex];
      const buttons = document.querySelectorAll('.opt-btn');
      buttons.forEach(btn => btn.disabled = true);
      buttons[q.correct].classList.add('correct');

      streak = 0;
      document.getElementById('streak-counter').textContent = `🔥 ${streak}`;

      const feedbackBox = document.getElementById('feedback-box');
      const feedbackTitle = document.getElementById('feedback-title');
      const feedbackExp = document.getElementById('feedback-exp');

      feedbackBox.className = 'feedback-box feedback-incorrect';
      feedbackTitle.innerHTML = `⏱️ ¡Tiempo agotado!`;
      feedbackExp.textContent = q.explanation;
      feedbackBox.style.display = 'block';

      document.getElementById('next-btn').style.display = 'block';
    }

    function nextQuestion() {
      currentIndex++;
      if (currentIndex < MAX_QUESTIONS) {
        loadQuestion();
      } else {
        endGame();
      }
    }

    function endGame() {
      showScreen('screen-end');

      const pct = Math.round((correctCount / MAX_QUESTIONS) * 100);
      document.getElementById('final-score').textContent = `${score} pts`;
      document.getElementById('stat-correct').textContent = `${correctCount}/${MAX_QUESTIONS}`;
      document.getElementById('stat-accuracy').textContent = `${pct}%`;
      document.getElementById('stat-streak').textContent = `${maxStreak}`;

      const titleEl = document.getElementById('final-title');
      const subtitleEl = document.getElementById('final-subtitle');

      if (pct >= 80) {
        titleEl.textContent = "🏆 ¡Niveau B2 Maîtrisé !";
        subtitleEl.textContent = "¡Excelente dominio del presente de indicativo en francés!";
        if (typeof confetti === 'function') {
          confetti({ particleCount: 120, spread: 70, origin: { y: 0.6 } });
        }
      } else if (pct >= 50) {
        titleEl.textContent = "👍 ¡Beau Travail !";
        subtitleEl.textContent = "Buen trabajo. Con un poco más de práctica dominarás todas las excepciones.";
      } else {
        titleEl.textContent = "📚 Continue à t'entraîner !";
        subtitleEl.textContent = "El presente B2 tiene sus trampas. ¡Repasa las explicaciones e inténtalo de nuevo!";
      }
    }
  </script>
</body>
</html>
"""

st.components.v1.html(HTML_CODE, height=820)
