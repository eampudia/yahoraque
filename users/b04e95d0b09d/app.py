st.components.v1.html("""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fotina - Mi Mini Photoshop</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Poppins', sans-serif;
        }

        body {
            background-color: #fdfbf7;
            color: #4a403a;
            padding: 16px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 20px;
        }

        header h1 {
            color: #6b5b95;
            font-size: 26px;
            margin-bottom: 4px;
        }

        header p {
            color: #8c7b8e;
            font-size: 13px;
        }

        /* Upload Screen */
        .upload-screen {
            background: #ffffff;
            border: 2px dashed #e8d7f1;
            border-radius: 20px;
            padding: 50px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 8px 20px rgba(107, 91, 149, 0.05);
        }

        .upload-screen:hover {
            border-color: #b19cd9;
            background: #faf6fc;
        }

        .upload-icon {
            font-size: 50px;
            margin-bottom: 12px;
        }

        .upload-screen h3 {
            color: #5c4b69;
            margin-bottom: 6px;
            font-size: 18px;
        }

        .upload-screen p {
            color: #9a8c98;
            font-size: 13px;
            margin-bottom: 20px;
        }

        .btn-primary {
            background: #b19cd9;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 12px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
            font-size: 14px;
            box-shadow: 0 4px 10px rgba(177, 156, 217, 0.3);
        }

        .btn-primary:hover {
            background: #9f8bc7;
        }

        /* Editor Layout pastel style */
        .editor-layout {
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 20px;
            align-items: start;
        }

        @media (max-width: 850px) {
            .editor-layout {
                grid-template-columns: 1fr;
            }
        }

        .sidebar {
            background: #ffffff;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 8px 20px rgba(107, 91, 149, 0.05);
            max-height: 80vh;
            overflow-y: auto;
            border: 1px solid #f3ecf7;
        }

        .control-group {
            margin-bottom: 18px;
            border-bottom: 1px solid #f7f2fa;
            padding-bottom: 14px;
        }

        .control-group:last-child {
            border-bottom: none;
            padding-bottom: 0;
            margin-bottom: 0;
        }

        .control-group label {
            display: block;
            font-weight: 600;
            font-size: 13px;
            color: #6b5b95;
            margin-bottom: 8px;
        }

        .slider-row {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        input[type="range"] {
            flex: 1;
            accent-color: #b19cd9;
            cursor: pointer;
        }

        .slider-value {
            font-size: 12px;
            font-weight: 500;
            color: #9a8c98;
            width: 35px;
            text-align: right;
        }

        select, input[type="text"], input[type="color"] {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #e8d7f1;
            border-radius: 10px;
            font-size: 13px;
            outline: none;
            transition: border-color 0.2s;
            background: #fdfbf7;
            color: #4a403a;
        }

        select:focus, input[type="text"]:focus {
            border-color: #b19cd9;
        }

        input[type="color"] {
            height: 38px;
            padding: 4px;
            cursor: pointer;
        }

        .filters-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
        }

        .filter-btn {
            background: #faf6fc;
            border: 1px solid #e8d7f1;
            padding: 8px;
            border-radius: 10px;
            font-size: 12px;
            cursor: pointer;
            text-align: center;
            transition: all 0.2s;
            font-weight: 500;
            color: #6b5b95;
        }

        .filter-btn:hover {
            background: #f0e6f5;
        }

        .filter-btn.active {
            background: #b19cd9;
            border-color: #b19cd9;
            color: white;
        }

        .frames-container {
            display: flex;
            gap: 8px;
            overflow-x: auto;
            padding-bottom: 4px;
        }

        .frame-thumb {
            width: 50px;
            height: 50px;
            border: 2px solid #e8d7f1;
            border-radius: 10px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            background: #faf6fc;
            flex-shrink: 0;
            transition: all 0.2s;
            color: #6b5b95;
            font-weight: 500;
        }

        .frame-thumb.active {
            border-color: #b19cd9;
            background: #f0e6f5;
            font-weight: 600;
        }

        /* Canvas Workspace */
        .workspace {
            background: #ffffff;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 8px 20px rgba(107, 91, 149, 0.05);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 480px;
            position: relative;
            border: 1px solid #f3ecf7;
        }

        .canvas-container {
            position: relative;
            max-width: 100%;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #faf6fc;
            border-radius: 14px;
            border: 1px solid #e8d7f1;
            box-shadow: inset 0 2px 6px rgba(107, 91, 149, 0.03);
            max-height: 60vh;
        }

        canvas {
            display: block;
            max-width: 100%;
            height: auto;
            border-radius: 12px;
            object-fit: contain;
        }

        .action-bar {
            display: flex;
            gap: 12px;
            margin-top: 18px;
            width: 100%;
            justify-content: space-between;
        }

        .btn-secondary {
            background: #f0e6f5;
            color: #6b5b95;
            border: none;
            padding: 10px 20px;
            border-radius: 12px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
            font-size: 13px;
        }

        .btn-secondary:hover {
            background: #e4d3ed;
        }

        .btn-success {
            background: #a8e6cf;
            color: #2d5a43;
            border: none;
            padding: 10px 24px;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
            font-size: 14px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            text-decoration: none;
            box-shadow: 0 4px 10px rgba(168, 230, 207, 0.3);
        }

        .btn-success:hover {
            background: #95dfc2;
        }

        .hidden {
            display: none !important;
        }
    </style>
</head>
<body>

    <div class="container">
        <header>
            <h1>🌸 Fotina</h1>
            <p>Tu mini Photoshop personal con toque pastel</p>
        </header>

        <!-- Pantalla de subida -->
        <div id="uploadScreen" class="upload-screen" onclick="document.getElementById('fileInput').click()">
            <div class="upload-icon">🎨</div>
            <h3>Sube una foto para empezar</h3>
            <p>Arrastra tu imagen o haz clic aquí para seleccionarla (PNG, JPG, JPEG)</p>
            <button class="btn-primary">Seleccionar archivo</button>
            <input type="file" id="fileInput" accept="image/*" class="hidden">
        </div>

        <!-- Pantalla de Editor -->
        <div id="editorScreen" class="editor-layout hidden">
            <!-- Barra lateral de controles en tonos pastel -->
            <div class="sidebar">
                <!-- Ajustes básicos -->
                <div class="control-group">
                    <label>☀️ Brillo</label>
                    <div class="slider-row">
                        <input type="range" id="brightness" min="0" max="200" value="100">
                        <span id="brightnessVal" class="slider-value">100%</span>
                    </div>
                </div>

                <div class="control-group">
                    <label>🌗 Contraste</label>
                    <div class="slider-row">
                        <input type="range" id="contrast" min="0" max="200" value="100">
                        <span id="contrastVal" class="slider-value">100%</span>
                    </div>
                </div>

                <!-- Filtros de color -->
                <div class="control-group">
                    <label>🎨 Filtros de color</label>
                    <div class="filters-grid">
                        <button class="filter-btn active" data-filter="normal">Normal</button>
                        <button class="filter-btn" data-filter="grayscale">Grises</button>
                        <button class="filter-btn" data-filter="sepia">Sepia</button>
                        <button class="filter-btn" data-filter="pastel">Pastel 🌸</button>
                        <button class="filter-btn" data-filter="sunset">Atardecer 🌅</button>
                        <button class="filter-btn" data-filter="mint">Menta 🌿</button>
                    </div>
                </div>

                <!-- Texto -->
                <div class="control-group">
                    <label>✍️ Texto personalizado</label>
                    <input type="text" id="customText" placeholder="Escribe algo bonito..." style="margin-bottom: 8px;">
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <input type="color" id="textColor" value="#ffffff" title="Color de texto" style="width: 50px;">
                        <input type="range" id="textSize" min="12" max="72" value="32" title="Tamaño">
                    </div>
                </div>

                <!-- Marcos -->
                <div class="control-group">
                    <label>🖼️ Marcos decorativos</label>
                    <div class="frames-container">
                        <div class="frame-thumb active" onclick="setFrame('none', event)">Ninguno</div>
                        <div class="frame-thumb" onclick="setFrame('white', event)" style="border: 3px solid #fff; background: #eee;">Clásico</div>
                        <div class="frame-thumb" onclick="setFrame('pastelpink', event)" style="background: #ffd3b6; color: #4a403a;">Rosa</div>
                        <div class="frame-thumb" onclick="setFrame('lavender', event)" style="background: #dcd0ff; color: #4a403a;">Lila</div>
                        <div class="frame-thumb" onclick="setFrame('polaroid', event)">Polaroid</div>
                    </div>
                </div>
            </div>

            <!-- Vista previa y acciones -->
            <div class="workspace">
                <div class="canvas-container">
                    <canvas id="imageCanvas"></canvas>
                </div>

                <div class="action-bar">
                    <button class="btn-secondary" onclick="resetImage()">🔄 Cambiar foto</button>
                    <a id="downloadBtn" class="btn-success" download="fotina-editada.jpg">📥 Descargar imagen</a>
                </div>
            </div>
        </div>
    </div>

    <script>
        const fileInput = document.getElementById('fileInput');
        const uploadScreen = document.getElementById('uploadScreen');
        const editorScreen = document.getElementById('editorScreen');
        const canvas = document.getElementById('imageCanvas');
        const ctx = canvas.getContext('2d');
        const downloadBtn = document.getElementById('downloadBtn');

        // Controles
        const brightnessInput = document.getElementById('brightness');
        const contrastInput = document.getElementById('contrast');
        const brightnessVal = document.getElementById('brightnessVal');
        const contrastVal = document.getElementById('contrastVal');
        const customText = document.getElementById('customText');
        const textColor = document.getElementById('textColor');
        const textSize = document.getElementById('textSize');

        let img = new Image();
        let currentFilter = 'normal';
        let currentFrame = 'none';
        let originalWidth = 0;
        let originalHeight = 0;

        // Cargar archivo
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    img.src = event.target.result;
                };
                reader.readAsDataURL(file);
            }
        });

        img.onload = () => {
            originalWidth = img.width;
            originalHeight = img.height;
            uploadScreen.classList.add('hidden');
            editorScreen.classList.remove('hidden');
            renderImage();
        };

        function resetImage() {
            fileInput.value = '';
            editorScreen.classList.add('hidden');
            uploadScreen.classList.remove('hidden');
        }

        // Eventos para actualizar valores en tiempo real
        brightnessInput.addEventListener('input', (e) => {
            brightnessVal.innerText = e.target.value + '%';
            renderImage();
        });

        contrastInput.addEventListener('input', (e) => {
            contrastVal.innerText = e.target.value + '%';
            renderImage();
        });

        customText.addEventListener('input', renderImage);
        textColor.addEventListener('input', renderImage);
        textSize.addEventListener('input', renderImage);

        // Filtros
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                currentFilter = e.target.getAttribute('data-filter');
                renderImage();
            });
        });

        // Marcos
        function setFrame(frameType, event) {
            currentFrame = frameType;
            document.querySelectorAll('.frame-thumb').forEach(t => t.classList.remove('active'));
            event.currentTarget.classList.add('active');
            renderImage();
        }

        // Renderizado principal en Canvas
        function renderImage() {
            if (!img.src) return;

            let w = originalWidth;
            let h = originalHeight;

            // Calcular tamaño del marco si aplica
            let frameSize = 0;
            let bottomExtra = 0;

            if (currentFrame === 'white' || currentFrame === 'pastelpink' || currentFrame === 'lavender') {
                frameSize = Math.max(w, h) * 0.05; // 5% de marco
            } else if (currentFrame === 'polaroid') {
                frameSize = Math.max(w, h) * 0.06;
                bottomExtra = h * 0.18; // Espacio extra inferior estilo polaroid
            }

            canvas.width = w + (frameSize * 2);
            canvas.height = h + (frameSize * 2) + bottomExtra;

            // Color de fondo del marco
            ctx.fillStyle = '#ffffff';
            if (currentFrame === 'pastelpink') ctx.fillStyle = '#ffd3b6';
            if (currentFrame === 'lavender') ctx.fillStyle = '#dcd0ff';
            if (currentFrame === 'polaroid') ctx.fillStyle = '#ffffff';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Coordenadas para dibujar la imagen dentro del marco
            let imgX = frameSize;
            let imgY = frameSize;

            // Aplicar efectos de brillo, contraste y filtros
            ctx.save();
            ctx.translate(imgX, imgY);

            let b = brightnessInput.value / 100;
            let c = contrastInput.value / 100;
            
            let filterStr = `brightness(${b}) contrast(${c})`;
            if (currentFilter === 'grayscale') filterStr += ' grayscale(100%)';
            if (currentFilter === 'sepia') filterStr += ' sepia(100%)';
            if (currentFilter === 'pastel') filterStr += ' sepia(30%) saturate(120%) brightness(105%)';
            if (currentFilter === 'sunset') filterStr += ' sepia(40%) hue-rotate(-20deg) saturate(130%)';
            if (currentFilter === 'mint') filterStr += ' sepia(20%) hue-rotate(70deg) saturate(90%)';

            ctx.filter = filterStr;
            ctx.drawImage(img, 0, 0, w, h);
            ctx.restore();

            // Dibujar texto personalizado si existe
            const textVal = customText.value.trim();
            if (textVal) {
                ctx.save();
                let scaledTextSize = (textSize.value / 500) * Math.max(w, h);
                ctx.font = `bold ${scaledTextSize}px 'Poppins', sans-serif`;
                ctx.fillStyle = textColor.value;
                ctx.strokeStyle = 'rgba(0, 0, 0, 0.7)';
                ctx.lineWidth = scaledTextSize / 10;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';

                let textX = imgX + (w / 2);
                let textY;

                if (currentFrame === 'polaroid') {
                    textY = imgY + h + (bottomExtra / 2) + (scaledTextSize / 3);
                } else {
                    textY = imgY + h - (h * 0.08);
                }

                ctx.strokeText(textVal, textX, textY);
                ctx.fillText(textVal, textX, textY);
                ctx.restore();
            }

            // Actualizar enlace de descarga
            downloadBtn.href = canvas.toDataURL('image/jpeg', 0.95);
        }
    </script>
</body>
</html>
""", height=750)
