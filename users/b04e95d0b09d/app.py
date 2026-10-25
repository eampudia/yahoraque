# Definimos el código HTML, CSS y JS de la aplicación
html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mi Mini Photoshop</title>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.5.1/dist/confetti.browser.min.js"></script>
    <style>
        :root {
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --text-color: #1e293b;
            --text-light: #64748b;
            --border-color: #e2e8f0;
            --shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -4px rgba(0, 0, 0, 0.05);
            --radius: 16px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-color);
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            padding: 20px;
        }

        header {
            text-align: center;
            margin-bottom: 24px;
        }

        header h1 {
            font-size: 1.8rem;
            color: var(--primary);
            margin-bottom: 6px;
        }

        header p {
            color: var(--text-light);
            font-size: 0.95rem;
        }

        .main-container {
            display: grid;
            grid-template-columns: 300px 1fr 300px;
            gap: 24px;
            max-width: 1300px;
            margin: 0 auto;
            width: 100%;
            flex: 1;
        }

        @media (max-width: 1024px) {
            .main-container {
                grid-template-columns: 1fr;
            }
        }

        .panel {
            background: var(--card-bg);
            border-radius: var(--radius);
            padding: 20px;
            box-shadow: var(--shadow);
            display: flex;
            flex-direction: column;
            gap: 20px;
            height: fit-content;
        }

        .panel h3 {
            font-size: 1.1rem;
            color: var(--text-color);
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Canvas / Visor Area */
        .canvas-area {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: var(--card-bg);
            border-radius: var(--radius);
            padding: 24px;
            box-shadow: var(--shadow);
            position: relative;
            min-height: 450px;
        }

        .upload-dropzone {
            border: 2px dashed var(--primary);
            border-radius: var(--radius);
            padding: 40px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: #eef2ff;
            width: 100%;
            max-width: 400px;
        }

        .upload-dropzone:hover {
            background: #e0e7ff;
        }

        .upload-dropzone input {
            display: none;
        }

        .upload-icon {
            font-size: 3rem;
            margin-bottom: 12px;
        }

        .canvas-wrapper {
            position: relative;
            max-width: 100%;
            max-height: 600px;
            overflow: hidden;
            display: none;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }

        canvas {
            display: block;
            max-width: 100%;
            height: auto;
        }

        /* Controles y Ajustes */
        .control-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .control-group label {
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text-light);
            display: flex;
            justify-content: space-between;
        }

        input[type="range"] {
            width: 100%;
            accent-color: var(--primary);
            cursor: pointer;
        }

        /* Filtros y Marcos Grids */
        .button-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }

        .btn-option {
            background: #f1f5f9;
            border: 2px solid transparent;
            padding: 10px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-color);
            transition: all 0.2s;
            text-align: center;
        }

        .btn-option:hover {
            background: #e2e8f0;
        }

        .btn-option.active {
            border-color: var(--primary);
            background: #eef2ff;
            color: var(--primary);
        }

        /* Inputs de texto */
        input[type="text"], select {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.2s;
        }

        input[type="text"]:focus, select:focus {
            border-color: var(--primary);
        }

        /* Botón de Acción Principal */
        .btn-primary {
            background: var(--primary);
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s, transform 0.1s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            width: 100%;
            text-decoration: none;
            box-shadow: 0 4px 6px -1px rgba(99, 102, 241, 0.3);
        }

        .btn-primary:hover {
            background: var(--primary-hover);
        }

        .btn-primary:active {
            transform: scale(0.98);
        }

        .btn-secondary {
            background: #f1f5f9;
            color: var(--text-color);
            border: none;
            padding: 10px;
            border-radius: 10px;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
            width: 100%;
        }

        .btn-secondary:hover {
            background: #e2e8f0;
        }

        .hidden {
            display: none !important;
        }

        .footer-actions {
            display: flex;
            gap: 10px;
            margin-top: 10px;
        }
    </style>
</head>
<body>

    <header>
        <h1>🎨 Mi Mini Photoshop</h1>
        <p>Edita tus fotos al instante de forma fácil, divertida y sin complicaciones.</p>
    </header>

    <div class="main-container">
        <!-- Panel Izquierdo: Ajustes y Filtros -->
        <div class="panel" id="left-panel" style="opacity: 0.5; pointer-events: none;">
            <h3>🛠️ Ajustes y Filtros</h3>
            
            <div class="control-group">
                <label>Brillo <span id="val-brightness">100%</span></label>
                <input type="range" id="brightness" min="0" max="200" value="100">
            </div>

            <div class="control-group">
                <label>Contraste <span id="val-contrast">100%</span></label>
                <input type="range" id="contrast" min="0" max="200" value="100">
            </div>

            <div class="control-group">
                <label>Saturación <span id="val-saturation">100%</span></label>
                <input type="range" id="saturation" min="0" max="200" value="100">
            </div>

            <div class="control-group">
                <label>Filtros Mágicos</label>
                <div class="button-grid">
                    <button class="btn-option active" data-filter="normal">Normal</button>
                    <button class="btn-option" data-filter="grayscale">Blanco y Negro</button>
                    <button class="btn-option" data-filter="vintage">Vintage</button>
                    <button class="btn-option" data-filter="cyberpunk">Ciberpunk</button>
                    <button class="btn-option" data-filter="sepia">Sepia</button>
                    <button class="btn-option" data-filter="invert">Negativo</button>
                </div>
            </div>

            <button class="btn-secondary" id="btn-reset">Restablecer todo</button>
        </div>

        <!-- Área Central: Visor de Imagen -->
        <div class="canvas-area">
            <div class="upload-dropzone" id="dropzone">
                <div class="upload-icon">📷</div>
                <h3>Sube tu foto aquí</h3>
                <p style="color: var(--text-light); font-size: 0.85rem; margin-top: 6px;">Haz clic para buscar en tu ordenador</p>
                <input type="file" id="fileInput" accept="image/*">
            </div>

            <div class="canvas-wrapper" id="canvasWrapper">
                <canvas id="imageCanvas"></canvas>
            </div>

            <div class="footer-actions hidden" id="footerActions" style="width: 100%; max-width: 400px; margin-top: 20px;">
                <button class="btn-secondary" id="btn-change-image" style="flex: 1;">Cambiar Foto</button>
                <a id="downloadBtn" class="btn-primary" style="flex: 2; text-align: center;">📥 Descargar Foto</a>
            </div>
        </div>

        <!-- Panel Derecho: Texto y Marcos -->
        <div class="panel" id="right-panel" style="opacity: 0.5; pointer-events: none;">
            <h3>✍️ Texto y Marcos</h3>

            <div class="control-group">
                <label>Texto Personalizado</label>
                <input type="text" id="customText" placeholder="Escribe tu frase aquí...">
            </div>

            <div class="control-group">
                <label>Posición del Texto</label>
                <select id="textPosition">
                    <option value="bottom">Abajo</option>
                    <option value="top">Arriba</option>
                    <option value="center">Centro</option>
                </select>
            </div>

            <div class="control-group">
                <label>Estilo de Letra</label>
                <select id="textFont">
                    <option value="bold 36px sans-serif">Moderna</option>
                    <option value="italic 36px serif">Clásica / Elegante</option>
                    <option value="bold 42px monospace">Ciber / Digital</option>
                    <option value="bold 40px 'Comic Sans MS', cursive">Divertida</option>
                </select>
            </div>

            <div class="control-group">
                <label>Marcos Divertidos</label>
                <div class="button-grid">
                    <button class="btn-option active" data-frame="none">Sin Marco</button>
                    <button class="btn-option" data-frame="polaroid">Polaroid</button>
                    <button class="btn-option" data-frame="neon">Neón Rosa</button>
                    <button class="btn-option" data-frame="gold">Elegante Dorado</button>
                    <button class="btn-option" data-frame="retro">Cinta Retro</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const dropzone = document.getElementById('dropzone');
        const canvasWrapper = document.getElementById('canvasWrapper');
        const canvas = document.getElementById('imageCanvas');
        const ctx = canvas.getContext('2d');
        const footerActions = document.getElementById('footerActions');
        const leftPanel = document.getElementById('left-panel');
        const rightPanel = document.getElementById('right-panel');
        const btnChangeImage = document.getElementById('btn-change-image');
        const downloadBtn = document.getElementById('downloadBtn');
        const btnReset = document.getElementById('btn-reset');

        // Controles de ajuste
        const brightnessInput = document.getElementById('brightness');
        const contrastInput = document.getElementById('contrast');
        const saturationInput = document.getElementById('saturation');
        const valBrightness = document.getElementById('val-brightness');
        const valContrast = document.getElementById('val-contrast');
        const valSaturation = document.getElementById('val-saturation');

        // Texto y marcos
        const customText = document.getElementById('customText');
        const textPosition = document.getElementById('textPosition');
        const textFont = document.getElementById('textFont');

        let originalImage = null;
        let currentFilter = 'normal';
        let currentFrame = 'none';

        // Click en dropzone abre selector de archivos
        dropzone.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const img = new Image();
                    img.onload = function() {
                        originalImage = img;
                        setupCanvas();
                        enablePanels();
                        applyEdits();
                    }
                    img.src = event.target.result;
                }
                reader.readAsDataURL(file);
            }
        });

        btnChangeImage.addEventListener('click', () => {
            fileInput.value = '';
            fileInput.click();
        });

        function enablePanels() {
            dropzone.classList.add('hidden');
            canvasWrapper.style.display = 'block';
            footerActions.classList.remove('hidden');
            leftPanel.style.opacity = '1';
            leftPanel.style.pointerEvents = 'auto';
            rightPanel.style.opacity = '1';
            rightPanel.style.pointerEvents = 'auto';
        }

        function setupCanvas() {
            if (!originalImage) return;
            // Mantener tamaño razonable para rendimiento
            let maxWidth = 1000;
            let maxHeight = 800;
            let width = originalImage.width;
            let height = originalImage.height;

            if (width > maxWidth || height > maxHeight) {
                let ratio = Math.min(maxWidth / width, maxHeight / height);
                width = width * ratio;
                height = height * ratio;
            }

            canvas.width = width;
            canvas.height = height;
        }

        function applyEdits() {
            if (!originalImage) return;

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Guardar estado y aplicar filtros de color CSS al contexto
            ctx.save();
            
            let b = brightnessInput.value;
            let c = contrastInput.value;
            let s = saturationInput.value;

            valBrightness.innerText = b + '%';
            valContrast.innerText = c + '%';
            valSaturation.innerText = s + '%';

            let filterString = `brightness(${b}%) contrast(${c}%) saturate(${s}%)`;

            if (currentFilter === 'grayscale') filterString += ' grayscale(100%)';
            if (currentFilter === 'sepia') filterString += ' sepia(100%)';
            if (currentFilter === 'invert') filterString += ' invert(100%)';
            if (currentFilter === 'vintage') filterString += ' sepia(60%) hue-rotate(-30deg) contrast(120%)';
            if (currentFilter === 'cyberpunk') filterString += ' saturate(200%) hue-rotate(90deg) contrast(130%)';

            ctx.filter = filterString;
            ctx.drawImage(originalImage, 0, 0, canvas.width, canvas.height);
            ctx.restore();

            // Dibujar Marcos
            drawFrame();

            // Dibujar Texto
            drawText();

            // Actualizar botón descarga
            downloadBtn.href = canvas.toDataURL('image/png');
            downloadBtn.download = 'foto-editada.png';
        }

        function drawFrame() {
            if (currentFrame === 'none') return;
            const w = canvas.width;
            const h = canvas.height;

            ctx.save();
            if (currentFrame === 'polaroid') {
                let border = Math.min(w, h) * 0.06;
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(0, 0, w, h);
                ctx.strokeStyle = '#cbd5e1';
                ctx.lineWidth = 2;
                ctx.strokeRect(border/2, border/2, w - border, h - border);
            } else if (currentFrame === 'neon') {
                ctx.strokeStyle = '#ec4899';
                ctx.lineWidth = Math.max(8, w * 0.02);
                ctx.shadowColor = '#f43f5e';
                ctx.shadowBlur = 15;
                ctx.strokeRect(10, 10, w - 20, h - 20);
            } else if (currentFrame === 'gold') {
                ctx.strokeStyle = '#d97706';
                ctx.lineWidth = Math.max(10, w * 0.025);
                ctx.strokeRect(0, 0, w, h);
                ctx.strokeStyle = '#fbbf24';
                ctx.lineWidth = Math.max(3, w * 0.005);
                ctx.strokeRect(10, 10, w - 20, h - 20);
            } else if (currentFrame === 'retro') {
                ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
                let b = 25;
                ctx.fillRect(0, 0, w, b);
                ctx.fillRect(0, h - b, w, b);
            }
            ctx.restore();
        }

        function drawText() {
            const text = customText.value.trim();
            if (!text) return;

            ctx.save();
            ctx.font = textFont.value;
            ctx.fillStyle = '#ffffff';
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = 4;
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';

            let x = canvas.width / 2;
            let y = canvas.height - 40;

            const pos = textPosition.value;
            if (pos === 'top') {
                y = 50;
            } else if (pos === 'center') {
                y = canvas.height / 2;
            }

            ctx.strokeText(text, x, y);
            ctx.fillText(text, x, y);
            ctx.restore();
        }

        // Eventos de cambios en tiempo real
        [brightnessInput, contrastInput, saturationInput].forEach(input => {
            input.addEventListener('input', applyEdits);
        });

        customText.addEventListener('input', applyEdits);
        textPosition.addEventListener('change', applyEdits);
        textFont.addEventListener('change', applyEdits);

        // Selector de Filtros
        document.querySelectorAll('[data-filter]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('[data-filter]').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                currentFilter = e.target.getAttribute('data-filter');
                applyEdits();
            });
        });

        // Selector de Marcos
        document.querySelectorAll('[data-frame]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('[data-frame]').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                currentFrame = e.target.getAttribute('data-frame');
                applyEdits();
            });
        });

        // Restablecer
        btnReset.addEventListener('click', () => {
            brightnessInput.value = 100;
            contrastInput.value = 100;
            saturationInput.value = 100;
            currentFilter = 'normal';
            currentFrame = 'none';
            customText.value = '';
            
            document.querySelectorAll('[data-filter]').forEach(b => b.classList.remove('active'));
            document.querySelector('[data-filter="normal"]').classList.add('active');
            
            document.querySelectorAll('[data-frame]').forEach(b => b.classList.remove('active'));
            document.querySelector('[data-frame="none"]').classList.add('active');

            applyEdits();
        });

        // Efecto de celebración al descargar
        downloadBtn.addEventListener('click', () => {
            confetti({
                particleCount: 60,
                spread: 70,
                origin: { y: 0.8 }
            });
        });
    </script>
</body>
</html>
"""

st.components.v1.html(html_content, height=750)
