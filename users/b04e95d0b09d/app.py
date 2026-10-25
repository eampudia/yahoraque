import json

# Definición de la aplicación web completa en HTML, CSS y JS con Alpine.js y Chart.js
html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Editor Hama Beads 8-bit</title>
    <!-- Alpine.js -->
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.14.1/dist/cdn.min.js"></script>
    <!-- Confetti -->
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.9.3/dist/confetti.browser.min.js"></script>
    <style>
        :root {
            --bead-size: 16px;
        }
        body {
            background-color: transparent;
            color: inherit;
            font-family: inherit;
        }
        .app-container {
            display: grid;
            grid-template-columns: 280px 1fr;
            gap: 20px;
            align-items: start;
        }
        @media (max-width: 900px) {
            .app-container {
                grid-template-columns: 1fr;
            }
        }
        .palette-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 6px;
            margin-bottom: 15px;
        }
        .color-btn {
            width: 100%;
            aspect-ratio: 1;
            border-radius: 6px;
            border: 2px solid transparent;
            cursor: pointer;
            transition: transform 0.1s, border-color 0.1s;
            position: relative;
        }
        .color-btn:hover {
            transform: scale(1.08);
        }
        .color-btn.active {
            border-color: var(--yq-blue, #0066cc);
            transform: scale(1.1);
            box-shadow: 0 0 6px rgba(0,0,0,0.3);
        }
        .canvas-scroll-container {
            overflow: auto;
            max-height: 650px;
            background: #f8f9fa;
            border: 2px dashed #cbd5e1;
            border-radius: 12px;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }
        .pixel-grid {
            display: grid;
            gap: 1px;
            background-color: #cbd5e1;
            border: 1px solid #94a3b8;
            user-select: none;
        }
        .pixel {
            background-color: #ffffff;
            width: var(--bead-size);
            height: var(--bead-size);
            cursor: pointer;
            transition: background-color 0.05s;
        }
        .pixel.round {
            border-radius: 50%;
            box-shadow: inset 1px 1px 2px rgba(255,255,255,0.6), inset -1px -1px 2px rgba(0,0,0,0.2);
        }
        .tool-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            width: 100%;
            margin-bottom: 8px;
        }
        .stats-badge {
            background: rgba(0,0,0,0.04);
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 0.9rem;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
        }
        .color-edit-row {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px;
        }
        .color-edit-row input[type="color"] {
            border: none;
            width: 36px;
            height: 36px;
            border-radius: 6px;
            cursor: pointer;
            background: none;
        }
    </style>
</head>
<body>

<main class="container" x-data="hamaApp()" x-init="initGrid()">
    <header style="margin-bottom: 20px; text-align: center;">
        <h2 style="margin-bottom: 5px;">🎨 Editor Hama Beads 8-bit</h2>
        <p style="color: #64748b; margin-top: 0;">Diseña figuritas pixel a pixel, convierte imágenes y crea tus patrones.</p>
    </header>

    <div class="app-container">
        <!-- Panel de Herramientas y Paleta -->
        <div class="card" style="padding: 16px;">
            <h4 style="margin-top: 0; margin-bottom: 12px; font-size: 1.1rem;">🛠️ Herramientas</h4>
            
            <div style="margin-bottom: 14px;">
                <label style="font-size: 0.85rem; font-weight: bold; display: block; margin-bottom: 4px;">Modo de Acción:</label>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 6px;">
                    <button class="outline" :class="tool === 'draw' ? 'contrast' : ''" @click="tool = 'draw'">✏️ Pintar</button>
                    <button class="outline" :class="tool === 'erase' ? 'contrast' : ''" @click="tool = 'erase'">🧹 Borrar</button>
                </div>
            </div>

            <div style="margin-bottom: 14px;">
                <label style="font-size: 0.85rem; font-weight: bold; display: block; margin-bottom: 4px;">Tamaño Cuadrícula: <span x-text="gridSize + 'x' + gridSize"></span></label>
                <input type="range" min="8" max="64" step="4" x-model.number="gridSize" @change="changeGridSize()" style="margin-bottom: 4px;">
            </div>

            <div style="margin-bottom: 14px;">
                <label style="font-size: 0.85rem; font-weight: bold; display: block; margin-bottom: 4px;">Estilo de Cuentas:</label>
                <fieldset style="display: flex; gap: 15px; border: none; padding: 0; margin: 0;">
                    <label><input type="radio" name="beadStyle" value="round" x-model="beadStyle"> Redondas</label>
                    <label><input type="radio" name="beadStyle" value="square" x-model="beadStyle"> Cuadradas</label>
                </fieldset>
            </div>

            <hr style="margin: 15px 0;">

            <h4 style="margin-top: 0; margin-bottom: 8px; font-size: 1.1rem;">🎨 Paleta (24 Colores)</h4>
            <p style="font-size: 0.8rem; color: #64748b; margin-top: 0;">Haz clic para seleccionar o edita el color abajo.</p>
            
            <div class="palette-grid">
                <template x-for="(color, index) in palette" :key="index">
                    <button class="color-btn" 
                            :class="selectedColorIndex === index && tool === 'draw' ? 'active' : ''" 
                            :style="'background-color: ' + color"
                            @click="selectedColorIndex = index; tool = 'draw'"
                            :title="'Color ' + (index+1)"></button>
                </template>
            </div>

            <details style="margin-bottom: 15px;">
                <summary style="font-size: 0.85rem; font-weight: bold; cursor: pointer;">✏️ Editar Colores de Paleta</summary>
                <div style="max-height: 150px; overflow-y: auto; margin-top: 8px; padding-right: 4px;">
                    <template x-for="(color, index) in palette" :key="'edit-'+index">
                        <div class="color-edit-row">
                            <input type="color" x-model="palette[index]">
                            <span style="font-size: 0.8rem;" x-text="'C' + (index+1)"></span>
                        </div>
                    </template>
                </div>
            </details>

            <hr style="margin: 15px 0;">

            <h4 style="margin-top: 0; margin-bottom: 8px; font-size: 1.1rem;">📷 Imagen a Patrón</h4>
            <input type="file" accept="image/*" @change="loadImageToGrid($event)" style="font-size: 0.85rem; width: 100%; margin-bottom: 8px;">
            <p style="font-size: 0.75rem; color: #64748b; margin: 0;">Carga una foto para pixelarla automáticamente en tu tablero.</p>

            <hr style="margin: 15px 0;">

            <button class="secondary tool-btn" @click="clearGrid()">🗑️ Borrar Tablero Completo</button>
            <button class="tool-btn" style="background-color: var(--yq-green, #10b981); border-color: var(--yq-green, #10b981); color: white;" @click="celebrate()">🎉 ¡Terminado!</button>
        </div>

        <!-- Tablero de Dibujo -->
        <div class="card" style="padding: 16px; display: flex; flex-direction: column; align-items: center;">
            <div style="width: 100%; display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="font-weight: bold; font-size: 0.95rem;">Tablero de Trabajo</span>
                <span class="stats-badge" style="margin: 0; font-size: 0.85rem;">
                    <span>Total cuentas: <strong x-text="totalBeadsCount"></strong></span>
                </span>
            </div>

            <div class="canvas-scroll-container" @mousedown="isMouseDown = true" @mouseup="isMouseDown = false" @mouseleave="isMouseDown = false">
                <div class="pixel-grid" 
                     :style="'grid-template-columns: repeat(' + gridSize + ', var(--bead-size));'"
                     @mouseleave="isMouseDown = false">
                    <template x-for="(row, rIndex) in grid" :key="rIndex">
                        <template x-for="(cellColorIndex, cIndex) in row" :key="cIndex">
                            <div class="pixel"
                                 :class="beadStyle"
                                 :style="cellColorIndex !== null ? 'background-color: ' + palette[cellColorIndex] : 'background-color: #ffffff;'"
                                 @mousedown.prevent="paintPixel(rIndex, cIndex)"
                                 @mouseover="if(isMouseDown) paintPixel(rIndex, cIndex)"
                                 :title="'Fila ' + (rIndex+1) + ', Col ' + (cIndex+1)">
                            </div>
                        </template>
                    </template>
                </div>
            </div>

            <p style="font-size: 0.8rem; color: #64748b; text-align: center; margin-top: 12px;">
                💡 <em>Consejo:</em> Como los diseños no se guardan al cerrar la página, ¡haz una captura de pantalla cuando termines tu obra maestra!
            </p>
        </div>
    </div>
</main>

<script>
function hamaApp() {
    return {
        gridSize: 24,
        tool: 'draw',
        selectedColorIndex: 0,
        beadStyle: 'round',
        isMouseDown: false,
        palette: [
            '#000000', '#ffffff', '#7f7f7f', '#c3c3c3', 
            '#880015', '#b97a57', '#ed1c24', '#ffaec9', 
            '#ff7f27', '#ffc90e', '#fff200', '#efe4b0', 
            '#22b14c', '#b5e61d', '#00a2e8', '#99d9ea', 
            '#3f48cc', '#7092be', '#a349a4', '#c8bfe7', 
            '#800000', '#008000', '#000080', '#808000'
        ],
        grid: [],

        initGrid() {
            let newGrid = [];
            for (let r = 0; r < this.gridSize; r++) {
                let row = [];
                for (let c = 0; c < this.gridSize; c++) {
                    row.push(null);
                }
                newGrid.push(row);
            }
            this.grid = newGrid;
        },

        changeGridSize() {
            let oldGrid = this.grid;
            let newGrid = [];
            for (let r = 0; r < this.gridSize; r++) {
                let row = [];
                for (let c = 0; c < this.gridSize; c++) {
                    if (oldGrid[r] && oldGrid[r][c] !== undefined) {
                        row.push(oldGrid[r][c]);
                    } else {
                        row.push(null);
                    }
                }
                newGrid.push(row);
            }
            this.grid = newGrid;
        },

        paintPixel(r, c) {
            if (this.tool === 'draw') {
                this.grid[r][c] = this.selectedColorIndex;
            } else if (this.tool === 'erase') {
                this.grid[r][c] = null;
            }
        },

        clearGrid() {
            if (confirm('¿Seguro que quieres borrar todo el tablero?')) {
                this.initGrid();
            }
        },

        get totalBeadsCount() {
            let count = 0;
            for (let r = 0; r < this.grid.length; r++) {
                for (let c = 0; c < this.grid[r].length; c++) {
                    if (this.grid[r][c] !== null) count++;
                }
            }
            return count;
        },

        celebrate() {
            confetti({
                particleCount: 120,
                spread: 70,
                origin: { y: 0.6 }
            });
        },

        loadImageToGrid(event) {
            const file = event.target.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (e) => {
                const img = new Image();
                img.onload = () => {
                    const canvas = document.createElement('canvas');
                    canvas.width = this.gridSize;
                    canvas.height = this.gridSize;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, this.gridSize, this.gridSize);
                    const imgData = ctx.getImageData(0, 0, this.gridSize, this.gridSize).data;

                    let newGrid = [];
                    for (let r = 0; r < this.gridSize; r++) {
                        let row = [];
                        for (let c = 0; c < this.gridSize; c++) {
                            const index = (r * this.gridSize + c) * 4;
                            const red = imgData[index];
                            const green = imgData[index + 1];
                            const blue = imgData[index + 2];
                            const alpha = imgData[index + 3];

                            if (alpha < 128) {
                                row.push(null);
                            } else {
                                // Encontrar color más cercano en la paleta actual
                                let closestIdx = 0;
                                let minDist = 999999;
                                for (let p = 0; p < this.palette.length; p++) {
                                    let hex = this.palette[p];
                                    let pr = parseInt(hex.slice(1,3), 16);
                                    let pg = parseInt(hex.slice(3,5), 16);
                                    let pb = parseInt(hex.slice(5,7), 16);

                                    let dist = Math.pow(red - pr, 2) + Math.pow(green - pg, 2) + Math.pow(blue - pb, 2);
                                    if (dist < minDist) {
                                        minDist = dist;
                                        closestIdx = p;
                                    }
                                }
                                row.push(closestIdx);
                            }
                        }
                        newGrid.push(row);
                    }
                    this.grid = newGrid;
                    this.celebrate();
                };
                img.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    }
}
</script>

</body>
</html>
"""

st.components.v1.html(html_content, height=800)
