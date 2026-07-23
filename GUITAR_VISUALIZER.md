# 🎸 Módulo Visualizador de Violão (`GuitarChordVisualizer.js`)

O **`GuitarChordVisualizer.js`** (`assets/modules/GuitarChordVisualizer.js`) é um módulo front-end autônomo e sem dependências externas responsável por renderizar dinamicamente diagramas vetoriais (`SVG`) do braço do violão (fretboard) com as posições dos acordes. Ele é utilizado principalmente no visualizador dedicado `viewer-violao.html`.

---

## 🏗️ Arquitetura e Estrutura de Dados

O módulo adota o padrão UMD (Universal Module Definition), permitindo sua importação tanto em ambientes Node/ESM quanto a inclusão direta via tag `<script>` no navegador (`window.GuitarChordVisualizer`).

### 1. Dicionário de Formatos (`CHORD_SHAPES`)
O coração do módulo é o objeto `CHORD_SHAPES`, que mapeia as cifras para as posições físicas dos dedos nas 6 cordas da afinação padrão do violão (**E6 - A5 - D4 - G3 - B2 - E1**):
```javascript
'C':  { frets: [-1, 3, 2, 0, 1, 0], baseFret: 1 },
'F':  { frets: [1, 3, 3, 2, 1, 1], baseFret: 1, barre: 1 },
'Bm': { frets: [-1, 2, 4, 4, 3, 2], baseFret: 2, barre: 2 }
```
- **`frets` (Array de 6 elementos):** Representa a casa pisada em cada corda da mais grave (`E6`) para a mais aguda (`E1`).
  - `-1`: Corda abafada/muta (cruz vermelha ou cinza `X` no diagrama).
  - `0`: Corda solta/aberta (círculo `O` no topo do nut).
  - `1..14`: Número da casa onde o dedo pressiona a corda.
- **`baseFret` (Número):** Indica a casa inicial mostrada no topo do diagrama (ex: `1` para acordes abertos, `2` para Bm na 2ª casa).
- **`barre` (Número, opcional):** Identifica a casa onde é executada a pestana (barra atravessando as cordas).

---

## ⚙️ Principais Métodos e Funcionalidades

### `resolveChordShape(chordName)`
Algoritmo inteligente de busca e simplificação de cifras complexas. Se uma cifra exata (como `D7M(9)`) não estiver no dicionário direto, o método:
1. Identifica a raiz (`root`) e testa enarmonias automáticas (ex: `Db` $\rightarrow$ `C#`).
2. Tenta simplificar as tensões e extensões por grau de similaridade harmônica:
   - Acordes diminutos ou meio-diminutos (`m7b5`, `m7(5-)`, `°`) $\rightarrow$ busca variações diminutas.
   - Acordes com sétima maior (`7M`, `maj7`) $\rightarrow$ busca a tríade maior ou sétima base.
   - Acordes suspensos (`sus4`, `4/7`) $\rightarrow$ busca o acorde dominante básico.

### `renderGuitarFretboardSVG(chordName, options)`
Gera e retorna a string de código vetorial `SVG` contendo o desenho completo do braço do violão.
- **Desenho do Braço:** Desenha o capotraste (*nut*) grosso quando `baseFret === 1`, ou exibe o número da casa lateralmente (ex: `2ª`) para marcações em casas mais altas.
- **Pestana Vetorial:** Desenha um retângulo arredondado de preenchimento (`<rect>`) conectando a primeira até a última corda pisada na casa da pestana.
- **Bolinhas e Marcadores (`<circle>`):** Desenha círculos preenchidos para os dedos com numeração ou marcação limpa de contraste.
- **Cordas Soltas e Abafadas:** Adiciona ícones `O` (corda solta) e `X` (corda não tocada) no topo do diagrama.

---

## 🔌 Como Integrar e Usar

No JavaScript da aplicação (`script-violao.js`), o módulo é chamado passando o nome do acorde atual e as dimensões desejadas para o contêiner:
```javascript
const svgHtml = window.GuitarChordVisualizer.renderGuitarFretboardSVG("F#m7", {
    width: 120,
    height: 115
});
document.getElementById("guitar-diagram-container").innerHTML = svgHtml;
```
O SVG gerado é totalmente responsivo, leve e escalável, garantindo nitidez visual em telas retina de smartphones até monitores ultra-wide sem perda de qualidade ou necessidade de imagens estáticas.
