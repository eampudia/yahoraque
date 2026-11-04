
html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>El Museo de las Cosas que Nunca Existieron</title>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"></script>
    <style>
        :root {
            --bg-deep: #0a0910;
            --card-bg: #13111c;
            --border-glow: #2d2645;
            --text-main: #f0edf6;
            --text-muted: #9e95b0;
        }

        body {
            background-color: var(--bg-deep);
            color: var(--text-main);
            font-family: system-ui, -apple-system, sans-serif;
            margin: 0;
            padding: 0;
            overflow-x: hidden;
            user-select: none;
            -webkit-user-select: none;
        }

        .museum-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 16px;
            box-sizing: border-box;
        }

        header {
            text-align: center;
            margin-bottom: 24px;
        }

        h1 {
            font-size: 1.8rem;
            margin: 0 0 8px 0;
            background: linear-gradient(135deg, #d4bfff, #9d7cff, #5ce1e6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 1px;
        }

        .subtitle {
            color: var(--text-muted);
            font-size: 0.95rem;
            margin: 0;
        }

        /* Navegación por salas */
        .room-nav {
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
            overflow-x: auto;
            padding-bottom: 8px;
        }

        .room-btn {
            background: var(--card-bg);
            border: 1px solid var(--border-glow);
            color: var(--text-muted);
            padding: 10px 16px;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 600;
            font-size: 0.9rem;
            white-space: nowrap;
            transition: all 0.3s ease;
            flex: 1;
            text-align: center;
        }

        .room-btn.active {
            background: linear-gradient(135deg, rgba(157, 124, 255, 0.2), rgba(92, 225, 230, 0.2));
            border-color: #9d7cff;
            color: var(--text-main);
            box-shadow: 0 0 15px rgba(157, 124, 255, 0.3);
        }

        .room-btn.locked {
            opacity: 0.5;
            cursor: not-allowed;
            border-style: dashed;
        }

        /* Contenedor de Sala */
        .room-card {
            background: var(--card-bg);
            border: 1px solid var(--border-glow);
            border-radius: 20px;
            padding: 20px;
            position: relative;
            min-height: 420px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }

        .room-description {
            text-align: center;
            color: var(--text-muted);
            font-size: 0.9rem;
            margin-bottom: 16px;
            max-width: 600px;
        }

        /* Lienzo interactivo común */
        .interactive-canvas-container {
            position: relative;
            width: 100%;
            height: 300px;
            background: #06050a;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.05);
            touch-action: none;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        canvas {
            display: block;
            width: 100%;
            height: 100%;
        }

        /* Controles específicos de sala */
        .controls-panel {
            display: flex;
            gap: 12px;
            margin-top: 16px;
            width: 100%;
            justify-content: center;
            flex-wrap: wrap;
        }

        .action-btn {
            background: #231e33;
            border: 1px solid #4a3f70;
            color: var(--text-main);
            padding: 10px 20px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.2s;
        }

        .action-btn:active {
            transform: scale(0.95);
            background: #322b4a;
        }

        /* Máquina de Recuerdos (Palancas y Ruedas) */
        .machine-panel {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            width: 100%;
            margin-top: 16px;
        }

        .machine-control {
            background: #191526;
            border: 1px solid #362d52;
            border-radius: 12px;
            padding: 12px;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }

        .machine-control label {
            font-size: 0.8rem;
            color: var(--text-muted);
        }

        /* Sliders personalizados */
        input[type=range] {
            width: 100%;
            accent-color: #9d7cff;
        }

        /* Mensaje de secreto */
        .secret-banner {
            background: linear-gradient(90deg, rgba(212,191,255,0.1), rgba(92,225,230,0.1));
            border: 1px solid #5ce1e6;
            color: #5ce1e6;
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 0.85rem;
            text-align: center;
            margin-top: 12px;
            animation: pulse 2s infinite;
            display: none;
        }

        .secret-banner.visible {
            display: block;
        }

        @keyframes pulse {
            0% { opacity: 0.7; }
            50% { opacity: 1; }
            100% { opacity: 0.7; }
        }

        .hidden {
            display: none !important;
        }

        .clue-counter {
            font-size: 0.8rem;
            color: #d4bfff;
            margin-top: 8px;
            text-align: center;
        }
    </style>
</head>
<body>

<div class="museum-container">
    <header>
        <h1>El Museo de las Cosas que Nunca Existieron</h1>
        <p class="subtitle">Toca, arrastra y altera la realidad en este espacio surrealista.</p>
        <div class="clue-counter" id="clueCounter">Secretos descubiertos: 0 / 3</div>
    </header>

    <!-- Barra de Navegación -->
    <nav class="room-nav">
        <button class="room-btn active" onclick="switchRoom('mirrors')">🪞 Gabinete Espejos</button>
        <button class="room-btn" onclick="switchRoom('memories')">⏳ Laboratorio Memorias</button>
        <button class="room-btn locked" id="navGallery" onclick="switchRoom('gallery')">🔒 Galería Oculta</button>
    </nav>

    <!-- SALA 1: GABINETE DE LOS ESPEJOS -->
    <div id="room-mirrors" class="room-card">
        <div>
            <h3 style="margin:0 0 4px 0; text-align:center; color:#d4bfff;">El Espejo Mágico</h3>
            <p class="room-description">Arrastra el dedo o el ratón sobre el espejo para distorsionar el reflejo del tiempo y despertar partículas cuánticas.</p>
        </div>
        
        <div class="interactive-canvas-container" id="mirrorContainer">
            <canvas id="mirrorCanvas"></canvas>
        </div>

        <div class="secret-banner" id="mirrorSecret">
            ✨ ¡Has rasgado el velo del espejo! Se ha revelado un fragmento secreto.
        </div>

        <div class="controls-panel">
            <button class="action-btn" onclick="resetMirror()">Calmar Reflejo</button>
            <button class="action-btn" onclick="changeMirrorMode()">Cambiar Espectro</button>
        </div>
    </div>

    <!-- SALA 2: LABORATORIO DE MEMORIAS -->
    <div id="room-memories" class="room-card hidden">
        <div>
            <h3 style="margin:0 0 4px 0; text-align:center; color:#d4bfff;">La Máquina de Recuerdos</h3>
            <p class="room-description">Manipula las palancas y diales para sintonizar memorias perdidas y alterar el universo dentro de la esfera.</p>
        </div>

        <div class="interactive-canvas-container">
            <canvas id="memoryCanvas"></canvas>
        </div>

        <div class="secret-banner" id="memorySecret">
            🔮 ¡Frecuencia sintonizada! Has capturado un recuerdo errante.
        </div>

        <div class="machine-panel">
            <div class="machine-control">
                <label>Flujo Temporal</label>
                <input type="range" id="sliderTime" min="0" max="100" value="50" oninput="updateMemoryMachine()">
            </div>
            <div class="machine-control">
                <label>Resonancia</label>
                <input type="range" id="sliderResonance" min="0" max="100" value="20" oninput="updateMemoryMachine()">
            </div>
            <div class="machine-control">
                <label>Luz Astral</label>
                <button class="action-btn" id="btnLight" onclick="toggleMemoryLight()" style="padding: 6px 12px; font-size: 0.8rem; width:100%;">Apagado</button>
            </div>
        </div>
    </div>

    <!-- SALA 3: GALERÍA OCULTA -->
    <div id="room-gallery" class="room-card hidden">
        <div>
            <h3 style="margin:0 0 4px 0; text-align:center; color:#5ce1e6;">El Núcleo de la Nada</h3>
            <p class="room-description">El objeto definitivo que combina espejos, tiempo y luz. Interactúa libremente para desatar la energía total del museo.</p>
        </div>

        <div class="interactive-canvas-container">
            <canvas id="galleryCanvas"></canvas>
        </div>

        <div class="controls-panel">
            <button class="action-btn" onclick="triggerCorePulse()">Pulso de Creación</button>
            <button class="action-btn" onclick="changeCoreMode()">Mutar Forma</button>
        </div>
    </div>

</div>

<script>
    // Estado global de secretos
    let secretsFound = {
        mirror: false,
        memory: false,
        gallery: false
    };
    let totalSecrets = 0;
    let galleryUnlocked = false;

    function updateSecretCount(type) {
        if (!secretsFound[type]) {
            secretsFound[type] = true;
            totalSecrets++;
            document.getElementById('clueCounter').innerText = `Secretos descubiertos: ${totalSecrets} / 3`;
            
            if (type === 'mirror') document.getElementById('mirrorSecret').classList.add('visible');
            if (type === 'memory') document.getElementById('memorySecret').classList.add('visible');
            
            confetti({
                particleCount: 40,
                spread: 60,
                origin: { y: 0.6 }
            });

            if (totalSecrets >= 2 && !galleryUnlocked) {
                galleryUnlocked = true;
                const navGal = document.getElementById('navGallery');
                navGal.classList.remove('locked');
                navGal.innerHTML = "✨ Galería Oculta";
                
                // Notificación visual de desbloqueo
                setTimeout(() => {
                    alert("🌟 ¡Has desbloqueado la Galería Oculta! Explora la nueva sala en la barra superior.");
                }, 300);
            }
        }
    }

    // Sistema de Navegación de Salas
    function switchRoom(roomName) {
        if (roomName === 'gallery' && !galleryUnlocked) {
            alert("🔒 Esta sala está sellada. Debes descubrir al menos 2 secretos en las otras salas manipulando los objetos.");
            return;
        }

        document.querySelectorAll('.room-card').forEach(card => card.classList.add('hidden'));
        document.querySelectorAll('.room-btn').forEach(btn => btn.classList.remove('active'));

        document.getElementById(`room-${roomName}`).classList.remove('hidden');
        
        // Encontrar botón activo
        event.currentTarget.classList.add('active');
        
        // Redimensionar canvas activos si es necesario
        window.dispatchEvent(new Event('resize'));
    }

    // ==========================================
    // SALA 1: GABINETE DE LOS ESPEJOS (Canvas)
    // ==========================================
    const mirrorCanvas = document.getElementById('mirrorCanvas');
    const mirrorCtx = mirrorCanvas.getContext('2d');
    let mirrorParticles = [];
    let mirrorMode = 0;
    let isTouchingMirror = false;
    let touchX = 0, touchY = 0;
    let mirrorInteractionCount = 0;

    function initMirrorCanvas() {
        mirrorCanvas.width = mirrorCanvas.parentElement.clientWidth;
        mirrorCanvas.height = mirrorCanvas.parentElement.clientHeight;
    }

    class MirrorParticle {
        constructor(x, y) {
            this.x = x;
            this.y = y;
            this.size = Math.random() * 4 + 1;
            this.speedX = (Math.random() - 0.5) * 4;
            this.speedY = (Math.random() - 0.5) * 4;
            this.color = Math.random() > 0.5 ? '#d4bfff' : '#5ce1e6';
            this.life = 100;
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            this.life -= 1.5;
        }
        draw(ctx) {
            ctx.fillStyle = this.color;
            ctx.globalAlpha = Math.max(this.life / 100, 0);
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fill();
            ctx.globalAlpha = 1.0;
        }
    }

    function setupMirrorEvents() {
        const handleMove = (x, y) => {
            isTouchingMirror = true;
            const rect = mirrorCanvas.getBoundingClientRect();
            touchX = x - rect.left;
            touchY = y - rect.top;
            
            for(let i=0; i<3; i++) {
                mirrorParticles.push(new MirrorParticle(touchX, touchY));
            }

            mirrorInteractionCount++;
            if (mirrorInteractionCount > 50) {
                updateSecretCount('mirror');
            }
        };

        mirrorCanvas.addEventListener('mousemove', (e) => handleMove(e.clientX, e.clientY));
        mirrorCanvas.addEventListener('touchmove', (e) => {
            if(e.touches.length > 0) handleMove(e.touches[0].clientX, e.touches[0].clientY);
            e.preventDefault();
        }, {passive: false});

        mirrorCanvas.addEventListener('mouseup', () => isTouchingMirror = false);
        mirrorCanvas.addEventListener('touchend', () => isTouchingMirror = false);
    }

    function animateMirror() {
        mirrorCtx.fillStyle = 'rgba(10, 9, 16, 0.2)';
        mirrorCtx.fillRect(0, 0, mirrorCanvas.width, mirrorCanvas.height);

        // Dibujar marco de espejo surrealista
        mirrorCtx.strokeStyle = mirrorMode === 0 ? '#9d7cff' : '#5ce1e6';
        mirrorCtx.lineWidth = 2;
        mirrorCtx.beginPath();
        let centerX = mirrorCanvas.width / 2;
        let centerY = mirrorCanvas.height / 2;
        let radius = Math.min(centerX, centerY) * 0.75;
        
        if (mirrorMode === 0) {
            mirrorCtx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        } else {
            // Forma romboidal abstracta
            mirrorCtx.moveTo(centerX, centerY - radius);
            mirrorCtx.lineTo(centerX + radius, centerY);
            mirrorCtx.lineTo(centerX, centerY + radius);
            mirrorCtx.lineTo(centerX - radius, centerY);
            mirrorCtx.closePath();
        }
        mirrorCtx.stroke();

        // Ondas internas del espejo
        let time = Date.now() * 0.002;
        mirrorCtx.strokeStyle = 'rgba(157, 124, 255, 0.15)';
        for(let r = 20; r < radius; r += 30) {
            mirrorCtx.beginPath();
            mirrorCtx.arc(centerX, centerY, r + Math.sin(time + r)*5, 0, Math.PI * 2);
            mirrorCtx.stroke();
        }

        // Partículas
        mirrorParticles.forEach((p, index) => {
            p.update();
            p.draw(mirrorCtx);
            if (p.life <= 0) mirrorParticles.splice(index, 1);
        });

        requestAnimationFrame(animateMirror);
    }

    function resetMirror() {
        mirrorParticles = [];
        mirrorInteractionCount = 0;
    }

    function changeMirrorMode() {
        mirrorMode = mirrorMode === 0 ? 1 : 0;
    }


    // ==========================================
    // SALA 2: LABORATORIO DE MEMORIAS (Canvas)
    // ==========================================
    const memoryCanvas = document.getElementById('memoryCanvas');
    const memoryCtx = memoryCanvas.getContext('2d');
    let memoryLightOn = false;
    let memoryAngle = 0;

    function initMemoryCanvas() {
        memoryCanvas.width = memoryCanvas.parentElement.clientWidth;
        memoryCanvas.height = memoryCanvas.parentElement.clientHeight;
    }

    function toggleMemoryLight() {
        memoryLightOn = !memoryLightOn;
        const btn = document.getElementById('btnLight');
        if (memoryLightOn) {
            btn.innerText = "Encendido (Astral)";
            btn.style.background = "#5ce1e6";
            btn.style.color = "#0a0910";
            updateSecretCount('memory');
        } else {
            btn.innerText = "Apagado";
            btn.style.background = "#231e33";
            btn.style.color = "#f0edf6";
        }
    }

    function updateMemoryMachine() {
        // Al interactuar con los sliders se avanza también sutilmente
        if(Math.random() < 0.1) {
            updateSecretCount('memory');
        }
    }

    function animateMemory() {
        memoryCtx.fillStyle = '#06050a';
        memoryCtx.fillRect(0, 0, memoryCanvas.width, memoryCanvas.height);

        let cx = memoryCanvas.width / 2;
        let cy = memoryCanvas.height / 2;
        let timeVal = document.getElementById('sliderTime').value / 100;
        let resVal = document.getElementById('sliderResonance').value / 100;

        memoryAngle += 0.01 + (timeVal * 0.03);

        // Dibujar Esfera central (Bola de Cristal)
        let gradient = memoryCtx.createRadialGradient(cx - 20, cy - 20, 10, cx, cy, 100);
        gradient.addColorStop(0, memoryLightOn ? '#5ce1e6' : '#d4bfff');
        gradient.addColorStop(0.5, memoryLightOn ? '#9d7cff' : '#322b4a');
        gradient.addColorStop(1, '#0a0910');

        memoryCtx.fillStyle = gradient;
        memoryCtx.beginPath();
        memoryCtx.arc(cx, cy, 90, 0, Math.PI * 2);
        memoryCtx.fill();

        // Anillos orbitantes dentro de la esfera
        memoryCtx.save();
        memoryCtx.translate(cx, cy);
        memoryCtx.rotate(memoryAngle);

        memoryCtx.strokeStyle = 'rgba(255,255,255,0.3)';
        memoryCtx.lineWidth = 1.5;
        
        let orbitCount = 3 + Math.floor(resVal * 5);
        for(let i=0; i<orbitCount; i++) {
            memoryCtx.rotate(Math.PI / orbitCount);
            memoryCtx.beginPath();
            memoryCtx.ellipse(0, 0, 70, 20 + (i * 10), 0, 0, Math.PI * 2);
            memoryCtx.stroke();
        }
        memoryCtx.restore();

        // Partículas flotantes alrededor de la esfera si hay luz
        if (memoryLightOn) {
            for(let i=0; i<5; i++) {
                let angle = Math.random() * Math.PI * 2;
                let dist = 100 + Math.random() * 40;
                let px = cx + Math.cos(angle + memoryAngle) * dist;
                let py = cy + Math.sin(angle + memoryAngle) * dist;
                memoryCtx.fillStyle = '#5ce1e6';
                memoryCtx.fillRect(px, py, 2, 2);
            }
        }

        requestAnimationFrame(animateMemory);
    }


    // ==========================================
    // SALA 3: GALERÍA OCULTA (Canvas)
    // ==========================================
    const galleryCanvas = document.getElementById('galleryCanvas');
    const galleryCtx = galleryCanvas.getContext('2d');
    let coreMode = 0;
    let corePulseSize = 0;
    let coreAngle = 0;

    function initGalleryCanvas() {
        galleryCanvas.width = galleryCanvas.parentElement.clientWidth;
        galleryCanvas.height = galleryCanvas.parentElement.clientHeight;
    }

    function triggerCorePulse() {
        corePulseSize = 50;
        confetti({
            particleCount: 80,
            spread: 100,
            origin: { y: 0.5 },
            colors: ['#5ce1e6', '#9d7cff', '#d4bfff']
        });
    }

    function changeCoreMode() {
        coreMode = (coreMode + 1) % 3;
    }

    function animateGallery() {
        galleryCtx.fillStyle = '#06050a';
        galleryCtx.fillRect(0, 0, galleryCanvas.width, galleryCanvas.height);

        let cx = galleryCanvas.width / 2;
        let cy = galleryCanvas.height / 2;
        coreAngle += 0.02;
        if (corePulseSize > 0) corePulseSize -= 1;

        galleryCtx.save();
        galleryCtx.translate(cx, cy);

        // Objeto central surrealista mutante
        if (coreMode === 0) {
            // Monolito Geométrico Giratorio
            galleryCtx.rotate(coreAngle);
            galleryCtx.strokeStyle = '#5ce1e6';
            galleryCtx.lineWidth = 2;
            galleryCtx.fillStyle = 'rgba(92, 225, 230, 0.1)';
            
            let size = 80 + corePulseSize;
            galleryCtx.beginPath();
            galleryCtx.rect(-size/2, -size/2, size, size);
            galleryCtx.fill();
            galleryCtx.stroke();

            galleryCtx.rotate(-coreAngle * 2);
            galleryCtx.strokeStyle = '#9d7cff';
            let size2 = 50 + corePulseSize/2;
            galleryCtx.beginPath();
            galleryCtx.rect(-size2/2, -size2/2, size2, size2);
            galleryCtx.stroke();

        } else if (coreMode === 1) {
            // Flor Cuántica
            galleryCtx.rotate(coreAngle);
            let petals = 8;
            for(let i=0; i<petals; i++) {
                galleryCtx.rotate((Math.PI * 2) / petals);
                galleryCtx.fillStyle = i % 2 === 0 ? 'rgba(157,124,255,0.3)' : 'rgba(92,225,230,0.3)';
                galleryCtx.beginPath();
                galleryCtx.ellipse(40, 0, 50 + corePulseSize, 20, 0, 0, Math.PI * 2);
                galleryCtx.fill();
                galleryCtx.stroke();
            }
        } else {
            // Ojo del Vacío
            galleryCtx.strokeStyle = '#d4bfff';
            galleryCtx.lineWidth = 3;
            galleryCtx.beginPath();
            galleryCtx.arc(0, 0, 70 + corePulseSize/2, 0, Math.PI * 2);
            galleryCtx.stroke();

            galleryCtx.fillStyle = '#5ce1e6';
            galleryCtx.beginPath();
            galleryCtx.arc(0, 0, 20 + Math.sin(coreAngle * 5) * 5, 0, Math.PI * 2);
            galleryCtx.fill();
        }

        galleryCtx.restore();
        requestAnimationFrame(animateGallery);
    }

    // Inicialización general
    window.addEventListener('load', () => {
        initMirrorCanvas();
        initMemoryCanvas();
        initGalleryCanvas();

        setupMirrorEvents();

        animateMirror();
        animateMemory();
        animateGallery();
    });

    window.addEventListener('resize', () => {
        initMirrorCanvas();
        initMemoryCanvas();
        initGalleryCanvas();
    });
</script>

</body>
</html>
"""

components.v1.html(html_content, height=720)
