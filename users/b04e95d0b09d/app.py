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
            background-color: #f4f6f9;
            color: #333;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
        }

        header {
            text-align: center;
            margin-bottom: 25px;
        }

        header h1 {
            color: #2c3e50;
            font-size: 28px;
            margin-bottom: 5px;
        }

        header p {
            color: #7f8c8d;
            font-size: 14px;
        }

        /* Upload Screen */
        .upload-screen {
            background: white;
            border: 2px dashed #cbd5e1;
            border-radius: 16px;
            padding: 50px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        }

        .upload-screen:hover {
            border-color: #3b82f6;
            background: #fafafa;
        }

        .upload-icon {
            font-size: 48px;
            margin-bottom: 15px;
        }

        .upload-screen h3 {
            color: #1e293b;
            margin-bottom: 8px;
        }

        .upload-screen p {
            color: #64748b;
            font-size: 13px;
            margin-bottom: 20px;
        }

        .btn-primary {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 8px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
            font-size: 14px;
        }

        .btn-primary:hover {
            background: #2563eb;
        }

        /* Editor Layout */
        .editor-layout {
            display: grid;
            grid-template-columns: 320px 1fr;
            gap: 24px;
            align-items: start;
        }

        @media (max-width: 850px) {
            .editor-layout {
                grid-template-columns: 1fr;
            }
        }

        .sidebar {
            background: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            max-height: 80vh;
            overflow-y: auto;
        }

        .control-group {
            margin-bottom: 20px;
            border-bottom: 1px solid #f1f5f9;
            padding-bottom: 16px;
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
            color: #475569;
            margin-bottom: 8px;
        }

        .slider-row {
            display: flex;
            align-items: center;
            gap: 10px;
        }

        input[type="range"] {
            flex: 1;
            accent-color: #3b82f6;
            cursor: pointer;
        }

        .slider-value {
            font-size: 12px;
            font-weight: 500;
            color: #64748b;
            width: 35px;
            text-align: right;
        }

        select, input[type="text"], input[type="color"] {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            font-size: 13px;
            outline: none;
            transition: border-color 0.2s;
            background: #fff;
        }

        select:focus, input[type="text"]:focus {
            border-color: #3b82f6;
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
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 8px;
            border-radius: 8px;
            font-size: 12px;
            cursor: pointer;
            text-align: center;
            transition: all 0.2s;
            font-weight: 500;
        }

        .filter-btn:hover {
            background: #f1f5f9;
        }

        .filter-btn.active {
            background: #eff6ff;
            border-color: #3b82f6;
            color: #1d4ed8;
        }

        .frames-container {
            display: flex;
            gap: 8px;
            overflow-x: auto;
            padding-bottom: 4px;
        }

        .frame-thumb {
            width: 45px;
            height: 45px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            background: #f8fafc;
            flex-shrink: 0;
            transition: all 0.2s;
        }

        .frame-thumb.active {
            border-color: #3b82f6;
            background: #eff6ff;
        }

        /* Canvas Workspace */
        .workspace {
            background: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 500px;
            position: relative;
        }

        .canvas-container {
            position: relative;
            max-width: 100%;
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #1e293b;
            border-radius: 12px;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.2);
        }

        canvas {
            display: block;
            max-width: 100%;
            height: auto;
            border-radius: 12px;
        }

        .action-bar {
            display: flex;
            gap: 12px;
            margin-top: 20px;
            width: 100%;
            justify-content: space-between;
        }

        .btn-secondary {
            background: #e2e8f0;
            color: #334155;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
            font-size: 13px;
        }

        .btn-secondary:hover {
            background: #cbd5e1;
        }

        .btn-success {
            background: #10b981;
            color: white;
            border: none;
            padding: 10px 24px;
            border-radius: 8px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
            font-size: 14px;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            text-decoration: none;
        }

        .btn-success:hover {
            background: #059669;
        }

        .hidden {
            display: none !important;
        }
    </style>
</head>
<body>

    <div class="container">
        <header>
            <h1>📸 Fotina</h1>
            <p>Edita tus fotos con filtros, texto y marcos de forma fácil y rápida</p>
        </header>

        <!-- Pantalla de subida -->
        <div id="uploadScreen" class="upload-screen" onclick="document.getElementById('fileInput').click()">
            <div class="upload-icon">📁</div>
            <h3>Sube una foto para empezar</h3>
            <p>Arrastra tu imagen o haz clic aquí (PNG, JPG, JPEG)</p>
            <button class="btn-primary">Seleccionar archivo</button>
            <input type="file" id="fileInput" accept="image/*" class="hidden">
        </div>

        <!-- Pantalla de Editor -->
        <div id="editorScreen" class="editor-layout hidden">
            <!-- Barra lateral de controles -->
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
                        <button class="filter-btn" data-filter="invert">Invertir</button>
                        <button class="filter-btn" data-filter="warm">Cálido</button>
                        <button class="filter-btn" data-filter="cool">Frío</button>
                    </div>
                </div>

                <!-- Texto -->
                <div class="control-group">
                    <label>✍️ Texto personalizado</label>
                    <input type="text" id="customText" placeholder="Escribe algo aquí..." style="margin-bottom: 8px;">
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
                        <div class="frame-thumb" onclick="setFrame('classic', event)" style="border: 4px solid #fff; box-shadow: 0 0 0 1px #000;">Blanco</div>
                        <div class="frame-thumb" onclick="setFrame('dark', event)" style="background: #111; color: white;">Negro</div>
                        <div class="frame-thumb" onclick="setFrame('gold', event)" style="border: 4px solid #d4af37;">Dorado</div>
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
            if (currentFrame === 'classic' || currentFrame === 'dark' || currentFrame === 'gold') {
                frameSize = Math.max(w, h) * 0.05; // 5% de marco
            } else if (currentFrame === 'polaroid') {
                frameSize = Math.max(w, h) * 0.06;
            }

            canvas.width = w + (frameSize * 2);
            canvas.height = h + (frameSize * 2) + (currentFrame === 'polaroid' ? h * 0.15 : 0);

            // Fondo del marco
            ctx.fillStyle = '#ffffff';
            if (currentFrame === 'dark') ctx.fillStyle = '#111111';
            if (currentFrame === 'gold') ctx.fillStyle = '#d4af37';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            // Coordenadas para dibujar la imagen dentro del marco
            let imgX = frameSize;
            let imgY = frameSize;

            if (currentFrame === 'polaroid') {
                imgX = frameSize;
                imgY = frameSize;
            }

            // Aplicar efectos de brillo y contraste vía contexto temporal o filtros CSS en ImageData
            ctx.save();
            ctx.translate(imgX, imgY);

            // Construir cadena de filtro CSS para el contexto de canvas
            let b = brightnessInput.value / 100;
            let c = contrastInput.value / 100;
            
            let filterStr = `brightness(${b}) contrast(${c})`;
            if (currentFilter === 'grayscale') filterStr += ' grayscale(100%)';
            if (currentFilter === 'sepia') filterStr += ' sepia(100%)';
            if (currentFilter === 'invert') filterStr += ' invert(100%)';
            if (currentFilter === 'warm') filterStr += ' sepia(50%) saturate(140%)';
            if (currentFilter === 'cool') filterStr += ' hue-rotate(180deg) saturate(90%)';

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
                ctx.strokeStyle = 'rgba(0, 0, 0, 0.8)';
                ctx.lineWidth = scaledTextSize / 8;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'bottom';

                let textX = imgX + (w / 2);
                let textY = imgY + h - (h * 0.08);

                ctx.strokeText(textVal, textX, textY);
                ctx.fillText(textVal, textX, textY);
                ctx.restore();
            }

            // Actualizar enlace de descarga
            downloadBtn.href = canvas.toDataURL('image/jpeg', 0.9);
        }
    </script>
</body>
</html>
""", height=750)
