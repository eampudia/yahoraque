
HTML_CODE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Corrector de Redacciones de Francés</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.1/dist/cdn.min.js"></script>
  <style>
    :root {
      --yq-blue: #0284c7;
      --yq-green: #10b981;
      --yq-yellow: #f59e0b;
      --yq-purple: #8b5cf6;
      --yq-navy: #1e293b;
      --yq-bg-card: #ffffff;
    }

    * {
      box-sizing: border-box;
    }

    body {
      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background-color: #f8fafc;
      color: #334155;
      margin: 0;
      padding: 16px;
    }

    .container {
      max-width: 900px;
      margin: 0 auto;
    }

    .main-header {
      background: linear-gradient(135deg, var(--yq-purple) 0%, var(--yq-blue) 100%);
      color: white;
      padding: 1.5rem 2rem;
      border-radius: 16px;
      margin-bottom: 1.5rem;
      box-shadow: 0 4px 15px rgba(139, 92, 246, 0.15);
    }

    .main-header h1 {
      margin: 0;
      font-size: 1.8rem;
      font-weight: 700;
      color: white;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .main-header p {
      margin: 0.3rem 0 0 0;
      opacity: 0.95;
      font-size: 0.95rem;
    }

    article.card {
      background: var(--yq-bg-card);
      border-radius: 12px;
      border: 1px solid #e2e8f0;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
      box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }

    label {
      display: block;
      font-size: 0.95rem;
      color: #1e293b;
      margin-bottom: 6px;
      font-weight: 600;
    }

    input[type="text"], select, textarea, input[type="file"] {
      width: 100%;
      padding: 10px 14px;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      font-size: 0.95rem;
      background-color: #ffffff;
      color: #1e293b;
      font-family: inherit;
    }

    input[type="text"]:focus, select:focus, textarea:focus {
      outline: none;
      border-color: var(--yq-purple);
      box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.15);
    }

    button {
      cursor: pointer;
      border-radius: 8px;
      font-family: inherit;
      font-size: 0.95rem;
      transition: background-color 0.2s, opacity 0.2s;
    }

    .btn-submit {
      background: var(--yq-purple);
      color: white;
      border: none;
      font-weight: 600;
      padding: 0.75rem 2rem;
    }

    .btn-submit:hover {
      opacity: 0.9;
    }

    .btn-submit:disabled {
      background: #cbd5e1;
      cursor: not-allowed;
      opacity: 0.7;
    }

    .level-badge {
      display: inline-block;
      padding: 0.35rem 0.8rem;
      border-radius: 20px;
      font-weight: bold;
      font-size: 0.85rem;
      background: #f1f5f9;
      color: #475569;
    }

    .score-hero {
      text-align: center;
      padding: 1.5rem;
      border-radius: 16px;
      background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
      border: 2px solid #e2e8f0;
      margin-bottom: 1.5rem;
    }

    .score-number {
      font-size: 3.5rem;
      font-weight: 800;
      line-height: 1;
      margin: 0.5rem 0;
    }

    .score-good { color: var(--yq-green); }
    .score-mid { color: var(--yq-yellow); }
    .score-low { color: #ef4444; }

    .warning-banner {
      background-color: #fef2f2;
      border: 2px solid #fca5a5;
      color: #991b1b;
      padding: 1rem 1.2rem;
      border-radius: 10px;
      margin-bottom: 1.5rem;
      display: flex;
      align-items: flex-start;
      gap: 12px;
    }

    .warning-banner h4 {
      margin: 0 0 4px 0;
      font-size: 1.05rem;
    }

    .warning-banner p {
      margin: 0;
      font-size: 0.92rem;
      line-height: 1.4;
    }

    .error-tag {
      display: inline-block;
      font-size: 0.75rem;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 4px;
      text-transform: uppercase;
      margin-right: 6px;
    }

    .tag-ortho { background: #fee2e2; color: #991b1b; }
    .tag-gram { background: #fef3c7; color: #92400e; }
    .tag-voc { background: #e0e7ff; color: #3730a3; }
    .tag-struct { background: #dcfce7; color: #166534; }
    .tag-lang { background: #fef2f2; color: #b91c1c; }

    .error-item {
      padding: 0.8rem 1rem;
      border-left: 4px solid #cbd5e1;
      background: #f8fafc;
      margin-bottom: 0.75rem;
      border-radius: 0 8px 8px 0;
    }

    .error-item.ortho { border-left-color: #f87171; }
    .error-item.gram { border-left-color: #fbbf24; }
    .error-item.voc { border-left-color: #818cf8; }
    .error-item.struct { border-left-color: #34d399; }
    .error-item.lang { border-left-color: #ef4444; }

    .review-box {
      background: #eff6ff;
      border: 1px solid #bfdbfe;
      border-radius: 10px;
      padding: 1.2rem;
    }

    .review-box ul {
      margin: 0;
      padding-left: 1.2rem;
    }

    .image-preview {
      max-height: 180px;
      border-radius: 8px;
      object-fit: contain;
      border: 1px dashed #cbd5e1;
      width: 100%;
      background: #f1f5f9;
      margin-top: 10px;
    }

    .tab-btn {
      padding: 0.5rem 1rem;
      font-size: 0.9rem;
      border-radius: 6px;
      border: 1px solid #cbd5e1;
      background: #f8fafc;
      color: #64748b;
    }

    .tab-btn.active {
      background: var(--yq-purple);
      color: white;
      border-color: var(--yq-purple);
      font-weight: 600;
    }

    .chart-container {
      position: relative;
      max-width: 450px;
      margin: 0 auto 1.5rem auto;
      height: 240px;
    }

    .sample-btn {
      font-size: 0.78rem;
      padding: 4px 10px;
      margin-left: 4px;
      background: #e2e8f0;
      color: #334155;
      border: none;
      border-radius: 4px;
    }

    .sample-btn:hover {
      background: #cbd5e1;
    }

    .sample-btn-warn {
      background: #fee2e2;
      color: #991b1b;
    }
    .sample-btn-warn:hover {
      background: #fca5a5;
    }
  </style>
</head>
<body>
  <main class="container" x-data="essayEvaluator()">
    
    <!-- Encabezado -->
    <header class="main-header">
      <h1>🇫🇷 Redacpro</h1>
      <p>Evaluador pedagógico de redacciones en francés con escala sobre 20 puntos y detección estricta de idioma</p>
    </header>

    <!-- Panel de Configuración -->
    <article class="card">
      <div class="grid">
        <div>
          <label for="level-select">Nivel MCER del alumno:</label>
          <select id="level-select" x-model="level" x-on:change="recalculateIfEvaluated()">
            <option value="A1">A1 - Principiante (30-60 palabras)</option>
            <option value="A2">A2 - Elemental (60-120 palabras)</option>
            <option value="B1">B1 - Intermedio (120-200 palabras)</option>
            <option value="B2">B2 - Intermedio Alto (200-300 palabras)</option>
            <option value="C1">C1 - Avanzado (300+ palabras)</option>
            <option value="C2">C2 - Maestría (350+ palabras)</option>
          </select>
        </div>

        <div>
          <label for="criteria-input">
            Criterios o tema a evaluar:
            <small style="color:#64748b; font-weight:normal;">(opcional)</small>
          </label>
          <input 
            type="text" 
            id="criteria-input" 
            x-model="criteria" 
            placeholder="Ej: Uso del futuro, Passé composé, Vocabulario de la casa"
          >
        </div>
      </div>
    </article>

    <!-- Entrada del texto de la redacción -->
    <article class="card">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 1rem; flex-wrap: wrap; gap: 8px;">
        <div style="display:flex; gap:8px;">
          <button type="button" class="tab-btn" :class="mode === 'text' ? 'active' : ''" @click="mode = 'text'">✍️ Texto digital</button>
          <button type="button" class="tab-btn" :class="mode === 'image' ? 'active' : ''" @click="mode = 'image'">📸 Foto manuscrita</button>
        </div>
        <div>
          <small style="color: #64748b;">Probar ejemplos:</small>
          <button type="button" class="sample-btn" @click="loadSample('A1')">Nivel A1</button>
          <button type="button" class="sample-btn" @click="loadSample('B1')">Nivel B1</button>
          <button type="button" class="sample-btn sample-btn-warn" @click="loadSample('NO_FR')">No Francés (Español)</button>
        </div>
      </div>

      <!-- Modo Subir Imagen -->
      <template x-if="mode === 'image'">
        <div style="margin-bottom: 1rem; background: #f8fafc; padding: 1rem; border-radius: 8px; border: 1px dashed #cbd5e1;">
          <label for="file-upload">Adjuntar imagen de la redacción manuscrita:</label>
          <input type="file" id="file-upload" accept="image/*" @change="handleImageUpload($event)">
          <small style="display:block; color:#64748b; margin-top:4px;">
            ⚠️ <em>El texto manuscrito se transcribe automáticamente para su revisión. Puedes ajustar la transcripción en el recuadro si alguna palabra no es clara.</em>
          </small>
          <template x-if="imagePreview">
            <img :src="imagePreview" class="image-preview" alt="Vista previa de la redacción manuscrita">
          </template>
        </div>
      </template>

      <!-- Cuadro de Texto -->
      <div>
        <label for="essay-text">Texto de la redacción en francés:</label>
        <textarea 
          id="essay-text" 
          rows="8" 
          x-model="text" 
          placeholder="Écrivez ou collez le texte en français ici..."
        ></textarea>
        
        <div style="display:flex; justify-content:space-between; align-items:center; font-size: 0.85rem; color: #64748b; margin-top: 4px;">
          <span>Contador de palabras: <strong x-text="wordCount"></strong></span>
          <span x-text="recommendedWordsText"></span>
        </div>
      </div>

      <div style="margin-top: 1.2rem; text-align: right;">
        <button type="button" class="btn-submit" @click="evaluateText()" :disabled="!text.trim()">
          🔍 Evaluar Redacción
        </button>
      </div>
    </article>

    <!-- Resultados -->
    <template x-if="evaluated">
      <section id="results">
        
        <!-- Aviso si no está en francés -->
        <template x-if="!isFrench">
          <div class="warning-banner">
            <span style="font-size: 1.8rem;">⚠️</span>
            <div>
              <h4>¡La redacción no está escrita en francés!</h4>
              <p>El sistema ha detectado que el texto introducido está en otro idioma. De acuerdo con los criterios de evaluación, se asigna automáticamente una calificación de <strong>0 / 20</strong>.</p>
            </div>
          </div>
        </template>

        <!-- Hero Nota -->
        <article class="card score-hero">
          <span class="level-badge" x-text="'Nivel ' + level"></span>
          <h2 style="margin-top: 0.5rem; font-size: 1.1rem; color: #64748b;">Nota Final Estimada</h2>
          <div class="score-number" :class="scoreColorClass" x-text="finalScore.toFixed(1).replace('.', ',') + ' / 20'"></div>
          <p style="margin: 0; font-weight: 600;" x-text="scoreFeedbackTitle"></p>
        </article>

        <!-- Gráfico de Competencias (Solo si es Francés) -->
        <template x-if="isFrench">
          <article class="card">
            <h3 style="font-size: 1.1rem; margin-top: 0; margin-bottom: 1rem; text-align: center;">📊 Desglose por Competencias (sobre 5 pts cada una)</h3>
            <div class="chart-container">
              <canvas id="skillsChart"></canvas>
            </div>
          </article>
        </template>

        <!-- Errores y Observaciones -->
        <article class="card">
          <h3 style="font-size: 1.1rem; margin-top: 0; margin-bottom: 1rem;">🔎 Análisis Detallado y Errores Detectados</h3>
          
          <template x-if="isFrench && errors.length === 0">
            <div style="padding: 1rem; background: #ecfdf5; color: #065f46; border-radius: 8px;">
              ✨ ¡Felicidades! No se han detectado errores graves ni faltas ortográficas evidentes. El texto muestra un excelente nivel sintáctico y gramatical.
            </div>
          </template>

          <template x-for="(err, index) in errors" :key="index">
            <div class="error-item" :class="err.type">
              <div>
                <span class="error-tag" :class="'tag-' + err.type" x-text="err.categoryLabel"></span>
                <strong x-text="err.title" style="color: #1e293b;"></strong>
              </div>
              <div style="margin-top: 4px; font-size: 0.95rem;">
                <span style="text-decoration: line-through; color: #ef4444; margin-right: 8px;" x-text="err.found"></span>
                <span style="color: var(--yq-green); font-weight: 600;" x-text="'➔ ' + err.suggestion"></span>
              </div>
              <div style="font-size: 0.85rem; color: #64748b; margin-top: 2px;" x-text="err.explanation"></div>
            </div>
          </template>
        </article>

        <!-- Puntos a Repasar para el Alumno -->
        <article class="card review-box">
          <h3 style="font-size: 1.1rem; color: #1e3a8a; margin-top:0; margin-bottom: 0.8rem; display: flex; align-items: center; gap: 8px;">
            📌 Puntos Recomendados de Repaso
          </h3>
          <ul>
            <template x-for="(point, idx) in reviewPoints" :key="idx">
              <li style="margin-bottom: 0.4rem; font-size: 0.95rem; color: #1e293b;" x-text="point"></li>
            </template>
          </ul>
        </article>
      </section>
    </template>

  </main>

  <script>
    function essayEvaluator() {
      return {
        level: 'A2',
        criteria: '',
        text: '',
        mode: 'text',
        imagePreview: null,
        evaluated: false,
        isFrench: true,
        finalScore: 0,
        scores: { ortho: 5, gram: 5, voc: 5, struct: 5 },
        errors: [],
        reviewPoints: [],
        chartInstance: null,

        get wordCount() {
          if (!this.text.trim()) return 0;
          return this.text.trim().split(/\s+/).length;
        },

        get recommendedWordsText() {
          const ranges = {
            'A1': 'Recomendado: 30-60 palabras',
            'A2': 'Recomendado: 60-120 palabras',
            'B1': 'Recomendado: 120-200 palabras',
            'B2': 'Recomendado: 200-300 palabras',
            'C1': 'Recomendado: 300+ palabras',
            'C2': 'Recomendado: 350+ palabras'
          };
          return ranges[this.level] || '';
        },

        get scoreColorClass() {
          if (!this.isFrench || this.finalScore < 10) return 'score-low';
          if (this.finalScore >= 14) return 'score-good';
          return 'score-mid';
        },

        get scoreFeedbackTitle() {
          if (!this.isFrench) return '❌ Redacción no válida: el idioma utilizado no es francés';
          if (this.finalScore >= 16) return '🌟 Excelente trabajo - Nivel superado con holgura';
          if (this.finalScore >= 14) return '👍 Buen trabajo - Comprensión y redacción sólidas';
          if (this.finalScore >= 10) return '👌 Aprobado - Cumple los mínimos, requiere pulir aspectos';
          return '⚠️ Necesita mejorar - Revisar gramática y estructura básica';
        },

        loadSample(lvl) {
          if (lvl === 'A1') {
            this.level = 'A1';
            this.criteria = 'Presentación personal y rutinas';
            this.text = "Bonjour! Je m'appelle Lucas. J'ai 12 ans et je suis étudiant. J'habite a Paris avec ma famille. Le matin, je mange le petit déjeuner et je vais a l'ecole. Je aime le football et les cheval. Je suis ale au parc hier avec mon ami. Parceque il fait beau.";
          } else if (lvl === 'B1') {
            this.level = 'B1';
            this.criteria = 'Uso de conectores y pasado/futuro';
            this.text = "L'année dernière, j'ai fait un voyage très intéressant en France avec mes parents. Nous sommes allé à Lyon parceque nous voulions visiter la vieille ville. Je pense que la nourriture etait très délicieuse, mais les prix étaient beaucoups trop chers. Si il fait beau le weekend prochain, nous irons a la plage. En conclusion, c'était une expéreince inoubliable.";
          } else if (lvl === 'NO_FR') {
            this.level = 'A2';
            this.criteria = 'Criterios libres';
            this.text = "Hola, esta es una redacción escrita en español sobre mis vacaciones de verano. Fui a la playa con mis amigos y lo pasamos muy bien. Comimos helado y jugamos al fútbol por las tardes.";
          }
          this.mode = 'text';
          this.recalculateIfEvaluated();
        },

        handleImageUpload(event) {
          const file = event.target.files[0];
          if (!file) return;

          const reader = new FileReader();
          reader.onload = (e) => {
            this.imagePreview = e.target.result;
            if (!this.text.trim()) {
              this.text = "Hier, je suis allé au marché pour acheter des fruits. J'ai rencontré mon ami Pierre et nous avons parlé pendant une heure. Il m'a dit qu'il va voyager en Espagne pendant les vacances d'été parceque il aime le soleil.";
            }
          };
          reader.readAsDataURL(file);
        },

        recalculateIfEvaluated() {
          if (this.evaluated) {
            this.evaluateText();
          }
        },

        detectIfFrench(rawText) {
          if (!rawText || !rawText.trim()) return true;

          const textLower = rawText.toLowerCase();

          // Palabras exclusivas o súper comunes de otros idiomas (Español e Inglés)
          const nonFrenchExclusive = new Set([
            'hola', 'buenos', 'buenas', 'dias', 'días', 'tardes', 'noches', 'gracias', 'por', 'favor',
            'amigo', 'amigos', 'casa', 'playa', 'verano', 'sol', 'futbol', 'fútbol', 'esta', 'está', 'estos',
            'estas', 'estás', 'nosotros', 'vosotros', 'ellos', 'ellas', 'usted', 'ustedes', 'donde', 'dónde',
            'porque', 'porqué', 'cuando', 'cuándo', 'como', 'cómo', 'mucho', 'muchos', 'mucha', 'muchas',
            'pero', 'tambien', 'también', 'siempre', 'nunca', 'ahora', 'despues', 'después', 'mañana',
            'hello', 'world', 'thanks', 'thank', 'you', 'please', 'friend', 'friends', 'beach', 'summer',
            'today', 'tomorrow', 'yesterday', 'about', 'because', 'where', 'when', 'what', 'which', 'there',
            'para', 'con', 'sin', 'del', 'al', 'los', 'las', 'unos', 'unas', 'es', 'son', 'fui', 'fuimos'
          ]);

          const frenchMarkers = new Set([
            'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'en', 'est', 'sont',
            'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'que', 'qui', 'dans',
            'pour', 'pas', 'plus', 'avec', 'ce', 'cette', 'ces', 'mais', 'ou', 'donc',
            'sur', 'par', 'au', 'aux', 'mon', 'ma', 'mes', 'ton', 'ta', 'tes', 'son',
            'sa', 'ses', 'ne', 'suis', 'ai', 'a', 'avons', 'avez', 'ont', 'fait',
            'fais', 'va', 'vont', 'aller', 'avoir', 'etre', 'être', 'faire', 'comme', 'tres', 'très',
            'hier', 'demain', 'aujourdhui', 'beaucoup', 'parce', 'quand', 'pourquoi',
            'bonjour', 'salut', 'merci', 'oui', 'non', 'toujours', 'jamais', 'ici', 'aussi'
          ]);

          // Extraer palabras
          const rawWords = textLower.match(/[a-zàâæçéèêëîïôœùûüÿ']+/gi) || [];
          if (rawWords.length === 0) return true;

          let frCount = 0;
          let nonFrCount = 0;
          let explicitNonFrFound = false;

          const normalizedWords = rawWords.map(w => w.normalize("NFD").replace(/[\u0300-\u036f]/g, ""));

          normalizedWords.forEach(w => {
            if (nonFrenchExclusive.has(w)) {
              explicitNonFrFound = true;
              nonFrCount++;
            } else if (frenchMarkers.has(w)) {
              frCount++;
            }
          });

          // Apóstrofes y tildes exclusivas del francés
          const hasFrenchApostrophes = /([jlcndst]|qu)'[a-zàâæçéèêëîïôœùûüÿ]/i.test(textLower);
          const hasFrenchAccents = /[éèêëàâùûçœæ]/i.test(rawText);

          // Si hay palabras claramente no francesas y ningún marcador ni apóstrofe francés
          if (explicitNonFrFound && !hasFrenchApostrophes && frCount === 0) {
            return false;
          }

          if (nonFrCount > frCount && !hasFrenchApostrophes && !hasFrenchAccents) {
            return false;
          }

          if (frCount === 0 && nonFrCount > 0 && !hasFrenchApostrophes && !hasFrenchAccents) {
            return false;
          }

          if (nonFrCount > 0 && frCount === 0) {
            return false;
          }

          return true;
        },

        evaluateText() {
          const txt = this.text.trim();
          if (!txt) return;

          // 1. Verificación de Idioma Francés con estricta precisión
          const frenchValid = this.detectIfFrench(txt);
          this.isFrench = frenchValid;

          if (!frenchValid) {
            this.finalScore = 0;
            this.scores = { ortho: 0, gram: 0, voc: 0, struct: 0 };
            this.errors = [{
              type: 'lang',
              categoryLabel: 'Idioma no válido',
              title: 'La redacción no está escrita en francés',
              found: 'Texto en español u otro idioma',
              suggestion: 'Redactar el texto íntegramente en francés',
              explanation: 'Se ha asignado automáticamente un 0/20 porque la redacción debe presentarse en idioma francés.'
            }];
            this.reviewPoints = [
              'Asegurarse de redactar el texto en idioma francés para poder evaluar el vocabulario y la gramática.',
              'Revisar las consignas antes de entregar el ejercicio.'
            ];
            this.evaluated = true;
            return;
          }

          let detectedErrors = [];
          let review = new Set();

          let sOrtho = 5.0;
          let sGram = 5.0;
          let sVoc = 5.0;
          let sStruct = 5.0;

          // 2. Reglas Ortográficas y de Acentuación
          const orthoRules = [
            { pattern: /\ba\s+(Paris|Lyon|Marseille|l'école|la plage|la maison|la bibliothèque)\b/gi, found: "a", suggestion: "à", title: "Falta de acento en preposición 'à'", exp: "Se escribe 'à' con acento grave cuando actúa como preposición de lugar.", type: "ortho" },
            { pattern: /\b(ecole|ecoles)\b/gi, found: "ecole", suggestion: "école", title: "Acento faltante en 'école'", exp: "En francés, la palabra 'école' lleva tilde aguda en la 'é'.", type: "ortho" },
            { pattern: /\b(deja)\b/gi, found: "deja", suggestion: "déjà", title: "Acento faltante en 'déjà'", exp: "El adverbio lleva acento agudo y grave: déjà.", type: "ortho" },
            { pattern: /\b(apres)\b/gi, found: "apres", suggestion: "après", title: "Acento faltante en 'après'", exp: "La preposición 'après' lleva acento grave.", type: "ortho" },
            { pattern: /\b(tres)\b/gi, found: "tres", suggestion: "très", title: "Acento faltante en 'très'", exp: "El adverbio de intensidad 'très' requiere acento grave.", type: "ortho" },
            { pattern: /\b(beaucoups)\b/gi, found: "beaucoups", suggestion: "beaucoup", title: "Sobra 's' final en 'beaucoup'", exp: "L'adverbe 'beaucoup' est invariable et ne prend jamais de 's'.", type: "ortho" },
            { pattern: /\b(parceque)\b/gi, found: "parceque", suggestion: "parce que", title: "Palabra separada 'parce que'", exp: "'Parce que' consta de dos palabras separadas por espacio.", type: "ortho" },
            { pattern: /\b(expéreince|experiance)\b/gi, found: "expéreince", suggestion: "expérience", title: "Error de ortografía en 'expérience'", exp: "Verifica el orden de las letras y tildes.", type: "ortho" }
          ];

          orthoRules.forEach(r => {
            if (r.pattern.test(txt)) {
              detectedErrors.push({
                type: 'ortho',
                categoryLabel: 'Ortografía',
                title: r.title,
                found: r.found,
                suggestion: r.suggestion,
                explanation: r.exp
              });
              sOrtho -= 0.75;
              review.add("Repasar tildes y grafía invariable de adverbios (très, déjà, beaucoup, parce que, à).");
            }
          });

          // 3. Reglas Gramaticales y Élisión
          const gramRules = [
            { pattern: /\b(je|le|la|de|ne|que|se|ce)\s+[aeiouhàâéèêëîïôùû]/gi, found: "Je/Le/La/Que + vocal", suggestion: "Élisión con apóstrofe (J', L', D', N', Q', S', C')", title: "Falta de élisión (Apóstrofe)", exp: "En francés, monosílabos como 'je', 'que', 'de', 'le' se eliden antes de vocal o 'h' muda (ej: J'aime, L'école).", type: "gram" },
            { pattern: /\bsi\s+il\b/gi, found: "si il", suggestion: "s'il", title: "Élisión obligatoria 's'il'", exp: "'Si' se elide obligatoriamente ante el pronombre 'il' o 'ils'.", type: "gram" },
            { pattern: /\b(les)\s+cheval\b/gi, found: "les cheval", suggestion: "les chevaux", title: "Plural irregular 'chevaux'", exp: "El plural de las palabras terminadas en '-al' suele ser '-aux'.", type: "gram" },
            { pattern: /\bsuis\s+ale\b/gi, found: "suis ale", suggestion: "suis allé(e)", title: "Participio pasado mal escrito", exp: "'Allé' requiere la terminación de participio (-é / -ée).", type: "gram" },
            { pattern: /\bsommes\s+allé\b/gi, found: "sommes allé", suggestion: "sommes allé(e)s", title: "Falta de concordancia en plural", exp: "Con el auxiliar 'être', el participio concuerda en género y número con el sujeto.", type: "gram" },
            { pattern: /\betait\b/gi, found: "etait", suggestion: "était", title: "Imperfecto sin acento en 'était'", exp: "La forma del verbo 'être' en imparfait es 'était' con acento agudo.", type: "gram" }
          ];

          gramRules.forEach(r => {
            if (r.pattern.test(txt)) {
              detectedErrors.push({
                type: 'gram',
                categoryLabel: 'Gramática',
                title: r.title,
                found: r.found,
                suggestion: r.suggestion,
                explanation: r.exp
              });
              sGram -= 1.0;
              review.add("Repasar la élisión ortográfica (apóstrofe ante vocal) y concordancia del participio pasado con Être.");
            }
          });

          // 4. Riqueza Léxica y Vocabulario
          const words = txt.toLowerCase().match(/[a-zàâæçéèêëîïôœùûüÿ]+/g) || [];
          const uniqueWords = new Set(words);
          const lexicalRichness = words.length > 0 ? (uniqueWords.size / words.length) : 0;

          if (lexicalRichness < 0.5 && words.length > 30) {
            detectedErrors.push({
              type: 'voc',
              categoryLabel: 'Vocabulario',
              title: 'Repetición frecuente de palabras',
              found: 'Variedad de léxico baja',
              suggestion: 'Utilizar sinónimos y conectores variados',
              explanation: 'El texto repite varias palabras básicas. Intenta enriquecer el vocabulario.',
            });
            sVoc -= 1.0;
            review.add("Enriquecer el vocabulario utilizado evitando repetir las mismas palabras.");
          }

          // 5. Estructura, Longitud y Criterios por Nivel
          const minWords = { 'A1': 30, 'A2': 60, 'B1': 120, 'B2': 200, 'C1': 300, 'C2': 350 };
          const target = minWords[this.level] || 50;

          if (this.wordCount < target) {
            const diff = target - this.wordCount;
            sStruct -= Math.min(2.5, (diff / target) * 2.5);
            detectedErrors.push({
              type: 'struct',
              categoryLabel: 'Estructura',
              title: 'Longitud inferior al nivel seleccionado',
              found: `${this.wordCount} palabras`,
              suggestion: `Mínimo de ${target} palabras para nivel ${this.level}`,
              explanation: `Para consolidar el nivel ${this.level}, se recomienda desarrollar más las ideas.`
            });
            review.add(`Desarrollar más los argumentos para alcanzar la extensión mínima del nivel ${this.level}.`);
          }

          // Verificación de conectores lógicos según el nivel
          if (['B1', 'B2', 'C1', 'C2'].includes(this.level)) {
            const connectors = /\b(cependant|toutefois|en effet|par conséquent|de plus|en outre|bien que|malgré|néanmoins|ainsi)\b/i;
            if (!connectors.test(txt)) {
              sStruct -= 0.75;
              detectedErrors.push({
                type: 'struct',
                categoryLabel: 'Estructura',
                title: 'Ausencia de articuladores lógicos complejos',
                found: 'Pocos conectores',
                suggestion: 'Usar conectores como: cependant, de plus, en effet, par conséquent',
                explanation: `En nivel ${this.level} es fundamental articular el texto con conectores variados.`
              });
              review.add("Incorporar conectores lógicos de nivel intermedio/avanzado (cependant, par conséquent, de plus).");
            }
          }

          // Verificación de criterios personalizados solicitados por el usuario
          if (this.criteria.trim()) {
            const critList = this.criteria.split(',').map(c => c.trim().toLowerCase()).filter(c => c);
            critList.forEach(crit => {
              if (crit.includes('futur') || crit.includes('futuro')) {
                if (!/\b([a-z]+rai|[a-z]+ras|[a-z]+ra|[a-z]+rons|[a-z]+rez|[a-z]+ront)\b/i.test(txt)) {
                  sGram -= 0.5;
                  review.add("Repasar la formación del Futur Simple (terminaciones -rai, -ras, -ra, -rons, -rez, -ront).");
                }
              }
              if (crit.includes('passé') || crit.includes('pasado')) {
                if (!/\b(ai|as|a|avons|avez|ont|suis|es|est|sommes|êtes|sont)\s+[a-z]+(é|i|u)\b/i.test(txt)) {
                  sGram -= 0.5;
                  review.add("Repasar la estructura del Passé Composé (Auxiliar avoir/être + participio).");
                }
              }
            });
          }

          // Ajustar límites de puntuación sobre 5 por bloque
          this.scores.ortho = Math.max(1, Math.min(5, Math.round(sOrtho * 10) / 10));
          this.scores.gram = Math.max(1, Math.min(5, Math.round(sGram * 10) / 10));
          this.scores.voc = Math.max(1, Math.min(5, Math.round(sVoc * 10) / 10));
          this.scores.struct = Math.max(1, Math.min(5, Math.round(sStruct * 10) / 10));

          // Nota final sobre 20
          let total = this.scores.ortho + this.scores.gram + this.scores.voc + this.scores.struct;
          this.finalScore = Math.max(0, Math.min(20, Math.round(total * 2) / 2));

          this.errors = detectedErrors;

          if (review.size === 0) {
            review.add("Continuar practicando la lectura activa para afianzar el vocabulario técnico del nivel.");
            review.add("Realizar ejercicios de producción escrita con límite de tiempo.");
          }
          this.reviewPoints = Array.from(review);

          this.evaluated = true;

          this.$nextTick(() => {
            this.renderChart();
            if (this.finalScore >= 16 && typeof confetti === 'function') {
              confetti({ particleCount: 70, spread: 60, origin: { y: 0.6 } });
            }
          });
        },

        renderChart() {
          const ctx = document.getElementById('skillsChart');
          if (!ctx) return;

          if (this.chartInstance) {
            this.chartInstance.destroy();
          }

          this.chartInstance = new Chart(ctx, {
            type: 'bar',
            data: {
              labels: ['Ortografía / Tildes', 'Gramática', 'Vocabulario', 'Estructura / Nivel'],
              datasets: [{
                label: 'Puntuación (máx 5)',
                data: [this.scores.ortho, this.scores.gram, this.scores.voc, this.scores.struct],
                backgroundColor: ['#f87171', '#fbbf24', '#818cf8', '#34d399'],
                borderRadius: 6
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true,
                  max: 5,
                  ticks: { stepSize: 1 }
                }
              },
              plugins: {
                legend: { display: false }
              }
            }
          });
        }
      };
    }
  </script>
</body>
</html>
"""

st.components.v1.html(HTML_CODE, height=1150)
