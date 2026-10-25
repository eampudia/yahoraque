import json

# Definimos el código HTML/CSS/JS completo para la Calculadora Kawaii Pastel
html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculadora Kawaii Pastel</title>
    <style>
        :root {
            --pastel-pink: #ffb7b2;
            --pastel-peach: #ffdac1;
            --pastel-yellow: #e2f0cb;
            --pastel-green: #b5ead7;
            --pastel-blue: #c7ceea;
            --pastel-purple: #e8dff5;
            --pastel-bg: #fff5f7;
            --text-color: #6d6875;
        }

        body {
            background-color: var(--pastel-bg);
            font-family: system-ui, -apple-system, sans-serif;
            color: var(--text-color);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 1rem;
        }

        .kawaii-container {
            background: white;
            border-radius: 30px;
            box-shadow: 0 10px 25px rgba(255, 183, 178, 0.3);
            padding: 25px;
            width: 100%;
            max-width: 360px;
            border: 4px solid var(--pastel-pink);
            box-sizing: border-box;
            position: relative;
            overflow: hidden;
        }

        /* Decoración kawaii flotante de fondo */
        .kawaii-decor {
            position: absolute;
            font-size: 1.2rem;
            opacity: 0.4;
            pointer-events: none;
            animation: float 3s ease-in-out infinite;
        }
        .dec-1 { top: 10px; left: 15px; animation-delay: 0s; }
        .dec-2 { top: 15px; right: 20px; animation-delay: 1s; }
        .dec-3 { bottom: 15px; left: 20px; animation-delay: 1.5s; }

        @keyframes float {
            0%, 100% { transform: translateY(0) rotate(0deg); }
            50% { transform: translateY(-5px) rotate(5deg); }
        }

        .header-title {
            text-align: center;
            color: #b5838d;
            margin-top: 5px;
            margin-bottom: 10px;
            font-size: 1.4rem;
            font-weight: bold;
        }

        /* Pantalla de la calculadora */
        .screen {
            background-color: #fcf6bd;
            border-radius: 20px;
            padding: 15px;
            margin-bottom: 15px;
            border: 3px dashed var(--pastel-pink);
            text-align: right;
            box-sizing: border-box;
            word-break: break-all;
        }

        .operation-history {
            font-size: 0.85rem;
            color: #a5a58d;
            min-height: 1.2rem;
            margin-bottom: 3px;
        }

        .current-result {
            font-size: 2rem;
            color: #6d6875;
            font-weight: bold;
        }

        /* Mensajito tierno */
        .cute-message {
            text-align: center;
            font-size: 0.85rem;
            color: #e5989b;
            margin-bottom: 15px;
            font-weight: 500;
            min-height: 1.2rem;
        }

        /* Teclado */
        .keypad {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
        }

        button.k-btn {
            background-color: var(--pastel-purple);
            border: none;
            border-radius: 18px;
            padding: 14px 0;
            font-size: 1.1rem;
            font-weight: bold;
            color: #6d6875;
            cursor: pointer;
            transition: all 0.1s ease;
            box-shadow: 0 4px 0 #d7c5e3;
        }

        button.k-btn:active {
            transform: translateY(4px);
            box-shadow: 0 0 0 #d7c5e3;
        }

        /* Variaciones de color para botones */
        button.btn-number {
            background-color: white;
            border: 2px solid var(--pastel-purple);
            box-shadow: 0 4px 0 var(--pastel-purple);
        }
        button.btn-number:active {
            box-shadow: 0 0 0 var(--pastel-purple);
        }

        button.btn-operator {
            background-color: var(--pastel-peach);
            box-shadow: 0 4px 0 #f5cac3;
        }
        button.btn-operator:active {
            box-shadow: 0 0 0 #f5cac3;
        }

        button.btn-action {
            background-color: var(--pastel-pink);
            box-shadow: 0 4px 0 #e5989b;
            color: white;
        }
        button.btn-action:active {
            box-shadow: 0 0 0 #e5989b;
        }

        button.btn-equal {
            background-color: var(--pastel-green);
            box-shadow: 0 4px 0 #84dcc6;
            grid-column: span 2;
        }
        button.btn-equal:active {
            box-shadow: 0 0 0 #84dcc6;
        }
    </style>
</head>
<body>

    <div class="kawaii-container">
        <!-- Decoraciones -->
        <div class="kawaii-decor dec-1">💖</div>
        <div class="kawaii-decor dec-2">⭐</div>
        <div class="kawaii-decor dec-3">🌸</div>

        <div class="header-title">✨ Kawaii Calc ✨</div>
        
        <!-- Pantalla -->
        <div class="screen">
            <div id="history" class="operation-history"></div>
            <div id="result" class="current-result">0</div>
        </div>

        <!-- Mensajito tierno dinámico -->
        <div id="cute-msg" class="cute-message">¡Hoy será un día genial! 🌟</div>

        <!-- Botones -->
        <div class="keypad">
            <button class="k-btn btn-action" onclick="clearAll()">AC</button>
            <button class="k-btn btn-action" onclick="deleteChar()">⌫</button>
            <button class="k-btn btn-operator" onclick="appendOperator('%')">%</button>
            <button class="k-btn btn-operator" onclick="appendOperator('/')">÷</button>

            <button class="k-btn btn-number" onclick="appendNumber('7')">7</button>
            <button class="k-btn btn-number" onclick="appendNumber('8')">8</button>
            <button class="k-btn btn-number" onclick="appendNumber('9')">9</button>
            <button class="k-btn btn-operator" onclick="appendOperator('*')">×</button>

            <button class="k-btn btn-number" onclick="appendNumber('4')">4</button>
            <button class="k-btn btn-number" onclick="appendNumber('5')">5</button>
            <button class="k-btn btn-number" onclick="appendNumber('6')">6</button>
            <button class="k-btn btn-operator" onclick="appendOperator('-')">-</button>

            <button class="k-btn btn-number" onclick="appendNumber('1')">1</button>
            <button class="k-btn btn-number" onclick="appendNumber('2')">2</button>
            <button class="k-btn btn-number" onclick="appendNumber('3')">3</button>
            <button class="k-btn btn-operator" onclick="appendOperator('+')">+</button>

            <button class="k-btn btn-number" onclick="appendNumber('0')" style="grid-column: span 2;">0</button>
            <button class="k-btn btn-number" onclick="appendDot()">.</button>
            <button class="k-btn btn-equal" onclick="calculate()">=</button>
        </div>
    </div>

    <!-- Librería de confeti opcional para cuando den al igual -->
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"></script>

    <script>
        let currentInput = "0";
        let historyInput = "";
        let resetScreen = false;

        const messages = [
            "¡Tú puedes con todo! 🌸",
            "¡Qué números tan bonitos! ✨",
            "¡Haciendo cuentas con amor! 💕",
            "¡Eres súper inteligente! 🌟",
            "¡Un pasito más hacia la meta! 🍡",
            "¡Sonríe mientras calculas! 🐾",
            "¡Brillas más que una estrella! ⭐"
        ];

        function showRandomMessage() {
            const randomIndex = Math.floor(Math.random() * messages.length);
            document.getElementById("cute-msg").innerText = messages[randomIndex];
        }

        function updateDisplay() {
            document.getElementById("result").innerText = currentInput;
            document.getElementById("history").innerText = historyInput;
        }

        function appendNumber(num) {
            if (currentInput === "0" || resetScreen) {
                currentInput = num;
                resetScreen = false;
            } else {
                currentInput += num;
            }
            showRandomMessage();
            updateDisplay();
        }

        function appendDot() {
            if (resetScreen) {
                currentInput = "0.";
                resetScreen = false;
                updateDisplay();
                return;
            }
            if (!currentInput.includes(".")) {
                currentInput += ".";
                updateDisplay();
            }
        }

        function appendOperator(op) {
            if (historyInput !== "" && !resetScreen) {
                calculate();
            }
            historyInput = currentInput + " " + op;
            resetScreen = true;
            showRandomMessage();
            updateDisplay();
        }

        function clearAll() {
            currentInput = "0";
            historyInput = "";
            resetScreen = false;
            document.getElementById("cute-msg").innerText = "¡Todo limpio y listo! 🧼✨";
            updateDisplay();
        }

        function deleteChar() {
            if (resetScreen) return;
            if (currentInput.length > 1) {
                currentInput = currentInput.slice(0, -1);
            } else {
                currentInput = "0";
            }
            updateDisplay();
        }

        function calculate() {
            if (historyInput === "") return;

            let fullExpr = historyInput + " " + currentInput;
            let evalExpr = fullExpr.replace(/÷/g, '/').replace(/×/g, '*');

            try {
                let res = eval(evalExpr);
                
                if (!Number.isInteger(res)) {
                    res = parseFloat(res.toFixed(6));
                }

                historyInput = fullExpr + " =";
                currentInput = res.toString();
                resetScreen = true;

                document.getElementById("cute-msg").innerText = "¡Resultado kawaii obtenido! 🎉💖";
                
                if (typeof confetti === 'function') {
                    confetti({
                        particleCount: 25,
                        spread: 60,
                        origin: { y: 0.7 },
                        colors: ['#ffb7b2', '#ffdac1', '#e2f0cb', '#b5ead7', '#c7ceea', '#e8dff5']
                    });
                }

            } catch (error) {
                currentInput = "Error 🥺";
                resetScreen = true;
                document.getElementById("cute-msg").innerText = "¡Ups! Algo salió mal. Inténtalo otra vez 💕";
            }

            updateDisplay();
        }
    </script>
</body>
</html>
"""

# Mostramos el componente usando st.components.v1.html correctamente
components.html(html_content, height=620)
