NOMBRE: Pastelcalc

html_code = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Calculadora Kawaii Pastel</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Quicksand', 'Nunito', 'Segoe UI', sans-serif;
        }

        body {
            background: linear-gradient(135deg, #fce4ec 0%, #f3e5f5 50%, #e8f5e9 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }

        .calculator-container {
            background: #ffffff;
            padding: 25px;
            border-radius: 35px;
            box-shadow: 0 15px 35px rgba(255, 182, 193, 0.3);
            width: 100%;
            max-width: 360px;
            border: 4px solid #fff0f5;
            position: relative;
            overflow: hidden;
        }

        /* Detalles alegres kawaii */
        .calculator-container::before {
            content: "✨ 🌸 💖 🌸 ✨";
            display: block;
            text-align: center;
            font-size: 14px;
            margin-bottom: 12px;
            letter-spacing: 4px;
        }

        .screen {
            background: #fdf6f9;
            border: 3px solid #ffccd5;
            border-radius: 20px;
            padding: 15px;
            text-align: right;
            margin-bottom: 20px;
            box-shadow: inset 0 3px 6px rgba(0, 0, 0, 0.02);
        }

        .previous-operand {
            color: #b5838d;
            font-size: 14px;
            min-height: 18px;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .current-operand {
            color: #6d6875;
            font-size: 32px;
            font-weight: bold;
            min-height: 40px;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .buttons-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
        }

        button {
            cursor: pointer;
            font-size: 20px;
            font-weight: bold;
            border: none;
            border-radius: 18px;
            height: 60px;
            display: flex;
            justify-content: center;
            align-items: center;
            transition: all 0.15s ease;
            box-shadow: 0 5px 0 rgba(0,0,0,0.05);
        }

        button:active {
            transform: translateY(3px);
            box-shadow: 0 2px 0 rgba(0,0,0,0.05);
        }

        /* Colores pastel kawaii */
        .btn-number {
            background-color: #fff;
            color: #6d6875;
            border: 2px solid #f8bbd0;
        }

        .btn-number:hover {
            background-color: #fff0f3;
        }

        .btn-operator {
            background-color: #e1bee7;
            color: #4a148c;
            border: 2px solid #ce93d8;
        }

        .btn-operator:hover {
            background-color: #d1c4e9;
        }

        .btn-clear {
            background-color: #ffccbc;
            color: #d84315;
            border: 2px solid #ffab91;
            grid-column: span 2;
        }

        .btn-clear:hover {
            background-color: #ffab91;
        }

        .btn-equals {
            background-color: #c8e6c9;
            color: #1b5e20;
            border: 2px solid #a5d6a7;
            grid-column: span 2;
        }

        .btn-equals:hover {
            background-color: #b9f6ca;
        }

        .footer-kawaii {
            text-align: center;
            margin-top: 15px;
            font-size: 11px;
            color: #b5838d;
        }
    </style>
</head>
<body>

    <div class="calculator-container">
        <div class="screen">
            <div id="previous" class="previous-operand"></div>
            <div id="current" class="current-operand">0</div>
        </div>
        
        <div class="buttons-grid">
            <button class="btn-clear" onclick="clearAll()">AC 🌸</button>
            <button class="btn-operator" onclick="appendOperation('/')">÷</button>
            <button class="btn-operator" onclick="appendOperation('*')">×</button>
            
            <button class="btn-number" onclick="appendNumber('7')">7</button>
            <button class="btn-number" onclick="appendNumber('8')">8</button>
            <button class="btn-number" onclick="appendNumber('9')">9</button>
            <button class="btn-operator" onclick="appendOperation('-')">-</button>
            
            <button class="btn-number" onclick="appendNumber('4')">4</button>
            <button class="btn-number" onclick="appendNumber('5')">5</button>
            <button class="btn-number" onclick="appendNumber('6')">6</button>
            <button class="btn-operator" onclick="appendOperation('+')">+</button>
            
            <button class="btn-number" onclick="appendNumber('1')">1</button>
            <button class="btn-number" onclick="appendNumber('2')">2</button>
            <button class="btn-number" onclick="appendNumber('3')">3</button>
            <button class="btn-equals" onclick="compute()">= 💖</button>
            
            <button class="btn-number" onclick="appendNumber('0')" style="grid-column: span 2;">0</button>
            <button class="btn-number" onclick="appendNumber('.')">.</button>
        </div>
        
        <div class="footer-kawaii">Hecho con amor ✨</div>
    </div>

    <script>
        let currentOperand = '0';
        let previousOperand = '';
        let operation = null;
        let resetScreenNext = false;

        const currentScreen = document.getElementById('current');
        const previousScreen = document.getElementById('previous');

        function updateDisplay() {
            currentScreen.innerText = currentOperand;
            if (operation != null) {
                previousScreen.innerText = `${previousOperand} ${operation}`;
            } else {
                previousScreen.innerText = '';
            }
        }

        function appendNumber(number) {
            if (currentOperand === '0' || resetScreenNext) {
                currentOperand = number;
                resetScreenNext = false;
            } else {
                if (number === '.' && currentOperand.includes('.')) return;
                currentOperand += number;
            }
            updateDisplay();
        }

        function appendOperation(op) {
            if (operation !== null) compute();
            previousOperand = currentOperand;
            operation = op;
            resetScreenNext = true;
            updateDisplay();
        }

        function compute() {
            let computation;
            const prev = parseFloat(previousOperand);
            const current = parseFloat(currentOperand);
            
            if (isNaN(prev) || isNaN(current)) return;

            switch (operation) {
                case '+':
                    computation = prev + current;
                    break;
                case '-':
                    computation = prev - current;
                    break;
                case '*':
                    computation = prev * current;
                    break;
                case '/':
                    if (current === 0) {
                        alert("¡No se puede dividir entre cero, amiguito! 🥺");
                        clearAll();
                        return;
                    }
                    computation = prev / current;
                    break;
                default:
                    return;
            }

            // Redondear para evitar problemas de precisión flotante absurdos
            currentOperand = Math.round(computation * 100000000) / 100000000;
            currentOperand = currentOperand.toString();
            operation = null;
            previousOperand = '';
            resetScreenNext = true;
            updateDisplay();
        }

        function clearAll() {
            currentOperand = '0';
            previousOperand = '';
            operation = null;
            updateDisplay();
        }
    </script>
</body>
</html>
"""

st.components.v1.html(html_code, height=620)
