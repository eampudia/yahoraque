import json

# Título y descripción principal
st.title("📷 Editor de Fotos Fácil")
st.markdown(
    "Ajusta el brillo, aplica filtros, gira, añade textos o stickers a tu foto y descárgala en segundos."
)

# Aplicación interactiva de edición de fotos en HTML/JS Canvas
html_editor_code = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<style>
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }
  
  body {
    background-color: #f8fafc;
    color: #1e293b;
    padding: 10px;
  }

  .editor-container {
    display: flex;
    flex-direction: row;
    gap: 16px;
    max-width: 1200px;
    margin: 0 auto;
    height: 670px;
  }

  @media (max-width: 768px) {
    .editor-container {
      flex-direction: column;
      height: auto;
    }
  }

  /* Control Panel */
  .panel {
    width: 320px;
    background: #ffffff;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    border: 1px solid #e2e8f0;
    display: flex;
    flex-direction: column;
    gap: 12px;
    overflow-y: auto;
  }

  .tabs {
    display: flex;
    gap: 4px;
    border-bottom: 2px solid #e2e8f0;
    padding-bottom: 8px;
    overflow-x: auto;
  }

  .tab-btn {
    background: none;
    border: none;
    padding: 6px 10px;
    font-size: 13px;
    font-weight: 600;
    color: #64748b;
    cursor: pointer;
    border-radius: 6px;
    white-space: nowrap;
    transition: all 0.2s;
  }

  .tab-btn.active {
    background-color: #eff6ff;
    color: #2563eb;
  }

  .tab-content {
    display: none;
    flex-direction: column;
    gap: 12px;
  }

  .tab-content.active {
    display: flex;
  }

  .control-group {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .control-group label {
    font-size: 12px;
    font-weight: 600;
    color: #475569;
    display: flex;
    justify-content: space-between;
  }

  input[type="range"] {
    width: 100%;
    accent-color: #2563eb;
    cursor: pointer;
  }

  .btn-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
  }

  .btn {
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    color: #334155;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    text-align: center;
    transition: all 0.2s;
  }

  .btn:hover {
    background: #e2e8f0;
  }

  .btn-primary {
    background: #2563eb;
    color: white;
    border: none;
  }

  .btn-primary:hover {
    background: #1d4ed8;
  }

  .btn-success {
    background: #10b981;
    color: white;
    border: none;
  }

  .btn-success:hover {
    background: #059669;
  }

  .btn-danger {
    background: #ef4444;
    color: white;
    border: none;
  }

  .btn-danger:hover {
    background: #dc2626;
  }

  .sticker-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 6px;
  }

  .sticker-btn {
    font-size: 20px;
    padding: 6px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    cursor: pointer;
  }

  .sticker-btn:hover {
    background: #e2e8f0;
  }

  /* Main Canvas Area */
  .canvas-area {
    flex: 1;
    background: #0f172a;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    padding: 16px;
  }

  .upload-box {
    text-align: center;
    color: #94a3b8;
    cursor: pointer;
    border: 2px dashed #334155;
    padding: 40px;
    border-radius: 12px;
    transition: all 0.2s;
  }

  .upload-box:hover {
    border-color: #60a5fa;
    color: #f8fafc;
  }

  #canvas {
    max-width: 100%;
    max-height: 580px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    border-radius: 4px;
    display: none;
    cursor: crosshair;
  }

  .canvas-tip {
    position: absolute;
    bottom: 12px;
    background: rgba(0, 0, 0, 0.6);
    color: #f1f5f9;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 11px;
    pointer-events: none;
  }

  .color-picker-row {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  input[type="color"] {
    border: none;
    width: 32px;
    height: 32px;
    border-radius: 6px;
    cursor: pointer;
    background: none;
  }

  input[type="text"] {
    width: 100%;
    padding: 8px;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    font-size: 13px;
  }
</style>
</head>
<body>

<div class="editor-container">
  <!-- Panel Lateral de Controles -->
  <div class="panel">
    <label class="btn btn-primary" style="display:block; text-align:center;">
      📁 Cargar Imagen
      <input type="file" id="fileInput" accept="image/*" style="display:none;">
    </label>

    <div class="tabs">
      <button class="tab-btn active" onclick="switchTab('tab-adjust')">🎛️ Ajustes</button>
      <button class="tab-btn" onclick="switchTab('tab-filters')">🎨 Filtros</button>
      <button class="tab-btn" onclick="switchTab('tab-transform')">🔄 Girar</button>
      <button class="tab-btn" onclick="switchTab('tab-elements')">✏️ Texto/Sticker</button>
      <button class="tab-btn" onclick="switchTab('tab-export')">💾 Guardar</button>
    </div>

    <!-- Tab 1: Ajustes Básicos -->
    <div id="tab-adjust" class="tab-content active">
      <div class="control-group">
        <label>Brillo <span id="val-brightness">100%</span></label>
        <input type="range" id="brightness" min="0" max="200" value="100" oninput="updateFilters()">
      </div>

      <div class="control-group">
        <label>Contraste <span id="val-contrast">100%</span></label>
        <input type="range" id="contrast" min="0" max="200" value="100" oninput="updateFilters()">
      </div>

      <div class="control-group">
        <label>Saturación <span id="val-saturation">100%</span></label>
        <input type="range" id="saturation" min="0" max="200" value="100" oninput="updateFilters()">
      </div>

      <button class="btn" onclick="resetAdjustments()">🔄 Restablecer Ajustes</button>
    </div>

    <!-- Tab 2: Filtros Estilo -->
    <div id="tab-filters" class="tab-content">
      <div class="btn-grid">
        <button class="btn" onclick="applyPreset('normal')">Normal</button>
        <button class="btn" onclick="applyPreset('bw')">Blanco y Negro</button>
        <button class="btn" onclick="applyPreset('sepia')">Sepia</button>
        <button class="btn" onclick="applyPreset('vintage')">Vintage</button>
        <button class="btn" onclick="applyPreset('invert')">Invertido</button>
        <button class="btn" onclick="applyPreset('warm')">Cálido</button>
      </div>
    </div>

    <!-- Tab 3: Transformar -->
    <div id="tab-transform" class="tab-content">
      <div class="btn-grid">
        <button class="btn" onclick="rotateImage(90)">🔄 Girar 90°</button>
        <button class="btn" onclick="flipImage('h')">↔️ Voltear H</button>
        <button class="btn" onclick="flipImage('v')">↕️ Voltear V</button>
        <button class="btn" onclick="rotateImage(-90)">↩️ Girar -90°</button>
      </div>
    </div>

    <!-- Tab 4: Texto y Stickers -->
    <div id="tab-elements" class="tab-content">
      <div class="control-group">
        <label>Escribir Texto sobre la Foto:</label>
        <input type="text" id="textInput" placeholder="Ej: Recuerdo inolvidable...">
      </div>

      <div class="control-group">
        <label>Color y Tamaño de Texto:</label>
        <div class="color-picker-row">
          <input type="color" id="textColor" value="#ffffff">
          <input type="range" id="textSize" min="16" max="100" value="36">
        </div>
      </div>

      <button class="btn btn-primary" onclick="addTextOverlay()">➕ Añadir Texto</button>

      <div class="control-group" style="margin-top: 8px;">
        <label>Añadir Adhesivos / Emojis:</label>
        <div class="sticker-grid">
          <button class="sticker-btn" onclick="addSticker('❤️')">❤️</button>
          <button class="sticker-btn" onclick="addSticker('⭐')">⭐</button>
          <button class="sticker-btn" onclick="addSticker('🔥')">🔥</button>
          <button class="sticker-btn" onclick="addSticker('😎')">😎</button>
          <button class="sticker-btn" onclick="addSticker('🎉')">🎉</button>
          <button class="sticker-btn" onclick="addSticker('👑')">👑</button>
          <button class="sticker-btn" onclick="addSticker('📍')">📍</button>
          <button class="sticker-btn" onclick="addSticker('💬')">💬</button>
          <button class="sticker-btn" onclick="addSticker('⚡')">⚡</button>
          <button class="sticker-btn" onclick="addSticker('✨')">✨</button>
        </div>
      </div>

      <button class="btn btn-danger" style="margin-top: 8px;" onclick="clearOverlays()">🗑️ Borrar Textos y Emojis</button>
    </div>

    <!-- Tab 5: Exportar / Descargar -->
    <div id="tab-export" class="tab-content">
      <div class="control-group">
        <label>Formato de Guardado:</label>
        <select id="exportFormat" class="btn" style="text-align:left;">
          <option value="image/png">PNG (Máxima calidad)</option>
          <option value="image/jpeg">JPG (Para fotos ligeras)</option>
        </select>
      </div>

      <button class="btn btn-success" style="padding:12px; font-size:14px;" onclick="downloadImage()">⬇️ Descargar Foto Editada</button>
    </div>
  </div>

  <!-- Zona Central Canvas -->
  <div class="canvas-area" id="canvasArea">
    <div class="upload-box" id="uploadBox" onclick="document.getElementById('fileInput').click()">
      <div style="font-size: 48px; margin-bottom: 8px;">📷</div>
      <p style="font-weight: 600; font-size: 16px;">Haz clic para seleccionar una foto</p>
      <p style="font-size: 12px; opacity: 0.8; margin-top: 4px;">Soporta JPG, PNG y WebP de tu dispositivo</p>
    </div>

    <canvas id="canvas"></canvas>
    <div class="canvas-tip" id="canvasTip" style="display:none;">💡 Consejo: Haz clic y arrastra los textos o emojis sobre la foto para posicionarlos.</div>
  </div>
</div>

<script>
  let image = new Image();
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  
  // States
  let brightness = 100;
  let contrast = 100;
  let saturation = 100;
  let grayscale = 0;
  let sepia = 0;
  let invert = 0;
  let rotation = 0;
  let flipH = 1;
  let flipV = 1;

  let overlays = [];
  let selectedOverlay = null;
  let isDragging = false;
  let startX = 0;
  let startY = 0;

  document.getElementById('fileInput').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function(event) {
      image = new Image();
      image.onload = function() {
        document.getElementById('uploadBox').style.display = 'none';
        canvas.style.display = 'block';
        document.getElementById('canvasTip').style.display = 'block';
        resetAdjustments();
        overlays = [];
        render();
      };
      image.src = event.target.result;
    };
    reader.readAsDataURL(file);
  });

  function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    event.target.classList.add('active');
    document.getElementById(tabId).classList.add('active');
  }

  function updateFilters() {
    brightness = document.getElementById('brightness').value;
    contrast = document.getElementById('contrast').value;
    saturation = document.getElementById('saturation').value;

    document.getElementById('val-brightness').innerText = brightness + '%';
    document.getElementById('val-contrast').innerText = contrast + '%';
    document.getElementById('val-saturation').innerText = saturation + '%';

    render();
  }

  function resetAdjustments() {
    brightness = 100;
    contrast = 100;
    saturation = 100;
    grayscale = 0;
    sepia = 0;
    invert = 0;
    rotation = 0;
    flipH = 1;
    flipV = 1;

    document.getElementById('brightness').value = 100;
    document.getElementById('contrast').value = 100;
    document.getElementById('saturation').value = 100;

    document.getElementById('val-brightness').innerText = '100%';
    document.getElementById('val-contrast').innerText = '100%';
    document.getElementById('val-saturation').innerText = '100%';

    render();
  }

  function applyPreset(preset) {
    resetAdjustments();
    if (preset === 'bw') {
      grayscale = 100;
    } else if (preset === 'sepia') {
      sepia = 100;
    } else if (preset === 'vintage') {
      sepia = 50;
      contrast = 120;
      brightness = 110;
    } else if (preset === 'invert') {
      invert = 100;
    } else if (preset === 'warm') {
      saturation = 130;
      brightness = 105;
    }
    render();
  }

  function rotateImage(deg) {
    rotation = (rotation + deg) % 360;
    render();
  }

  function flipImage(dir) {
    if (dir === 'h') flipH *= -1;
    if (dir === 'v') flipV *= -1;
    render();
  }

  function addTextOverlay() {
    const text = document.getElementById('textInput').value.trim();
    if (!text) return;

    const color = document.getElementById('textColor').value;
    const size = parseInt(document.getElementById('textSize').value, 10);

    overlays.push({
      type: 'text',
      text: text,
      color: color,
      size: size,
      x: canvas.width / 2,
      y: canvas.height / 2
    });

    document.getElementById('textInput').value = '';
    render();
  }

  function addSticker(emoji) {
    overlays.push({
      type: 'text',
      text: emoji,
      color: '#ffffff',
      size: 64,
      x: canvas.width / 2,
      y: canvas.height / 2
    });
    render();
  }

  function clearOverlays() {
    overlays = [];
    render();
  }

  function render() {
    if (!image.src) return;

    const isRotatedVertical = Math.abs(rotation % 180) === 90;
    const targetW = isRotatedVertical ? image.height : image.width;
    const targetH = isRotatedVertical ? image.width : image.height;

    canvas.width = targetW;
    canvas.height = targetH;

    ctx.save();
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Apply Transformations
    ctx.translate(canvas.width / 2, canvas.height / 2);
    ctx.rotate((rotation * Math.PI) / 180);
    ctx.scale(flipH, flipV);

    // Apply Canvas Filters
    ctx.filter = `brightness(${brightness}%) contrast(${contrast}%) saturate(${saturation}%) grayscale(${grayscale}%) sepia(${sepia}%) invert(${invert}%)`;

    ctx.drawImage(image, -image.width / 2, -image.height / 2);
    ctx.restore();

    // Draw Overlays (Text / Stickers)
    overlays.forEach((item) => {
      ctx.save();
      ctx.font = `${item.size}px sans-serif`;
      ctx.fillStyle = item.color;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      
      // Shadow for text readability
      ctx.shadowColor = 'rgba(0,0,0,0.6)';
      ctx.shadowBlur = 6;
      ctx.shadowOffsetX = 2;
      ctx.shadowOffsetY = 2;

      ctx.fillText(item.text, item.x, item.y);
      ctx.restore();
    });
  }

  // Interacción de Arrastrar y Soltar Elementos sobre el Canvas
  function getCanvasCoords(e) {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const clientY = e.touches ? e.touches[0].clientY : e.clientY;
    return {
      x: (clientX - rect.left) * scaleX,
      y: (clientY - rect.top) * scaleY
    };
  }

  canvas.addEventListener('mousedown', startDrag);
  canvas.addEventListener('touchstart', startDrag);

  function startDrag(e) {
    const pos = getCanvasCoords(e);
    // Verificar si se hizo clic cerca de un overlay
    for (let i = overlays.length - 1; i >= 0; i--) {
      const item = overlays[i];
      const dist = Math.hypot(item.x - pos.x, item.y - pos.y);
      if (dist < item.size * 1.2) {
        selectedOverlay = item;
        isDragging = true;
        startX = pos.x - item.x;
        startY = pos.y - item.y;
        break;
      }
    }
  }

  window.addEventListener('mousemove', drag);
  window.addEventListener('touchmove', drag);

  function drag(e) {
    if (!isDragging || !selectedOverlay) return;
    const pos = getCanvasCoords(e);
    selectedOverlay.x = pos.x - startX;
    selectedOverlay.y = pos.y - startY;
    render();
  }

  window.addEventListener('mouseup', endDrag);
  window.addEventListener('touchend', endDrag);

  function endDrag() {
    isDragging = false;
    selectedOverlay = null;
  }

  function downloadImage() {
    if (!image.src) {
      alert("Por favor, carga una foto primero.");
      return;
    }
    const format = document.getElementById('exportFormat').value;
    const ext = format === 'image/jpeg' ? 'jpg' : 'png';
    const link = document.createElement('a');
    link.download = `foto_editada.${ext}`;
    link.href = canvas.toDataURL(format, 0.95);
    link.click();
  }
</script>
</body>
</html>
"""

# Renderizado de la aplicación HTML/JS
st.components.v1.html(html_editor_code, height=720)
