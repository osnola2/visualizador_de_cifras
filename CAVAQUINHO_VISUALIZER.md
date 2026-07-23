# 🪕 Módulo Visualizador de Cavaquinho (`CavaquinhoChordVisualizer.js`)

O **`CavaquinhoChordVisualizer.js`** (`assets/modules/CavaquinhoChordVisualizer.js`) é o módulo front-end autônomo responsável por gerar diagramas vetoriais (`SVG`) interativos para o braço do cavaquinho. Ele opera na afinação tradicional brasileira **D-G-B-D (Ré - Sol - Si - Ré)** da 4ª para a 1ª corda, sendo a peça central de renderização do visualizador `viewer-cavaquinho.html`.

---

## 🏗️ Arquitetura e Afinação Tradicional

Diferente de violões ou ukuleles, o cavaquinho possui 4 cordas com afinação reentrante/aberta (`D4 - G4 - B4 - D5`). O módulo estrutura seus dados especificamente para essa afinação:
- **Corda 4 (Mais grave / Esquerda):** Ré (`D4`)
- **Corda 3:** Sol (`G4`)
- **Corda 2:** Si (`B4`)
- **Corda 1 (Mais aguda / Direita):** Ré (`D5`)

### 1. Dicionário Principal (`CHORD_SHAPES`)
Mapeia as posições padrão para mais de 150 acordes maiores, menores, sétimas, diminutos e aumentados:
```javascript
'C':  { frets: [2, 0, 1, 2], baseFret: 1 },
'G':  { frets: [5, 4, 3, 5], baseFret: 3 },
'Bb': { frets: [3, 3, 3, 3], baseFret: 3, barre: 3 }
```
- **`frets` (Array de 4 elementos):** Posição de casa pisada em cada uma das 4 cordas (`[Corda4, Corda3, Corda2, Corda1]`).
  - `-1`: Corda muta/abafada (`X`).
  - `0`: Corda solta (`O`).
  - `1..14`: Número da casa onde o dedo pressiona.

---

## 🔄 Sistema de Inversões e Posições Alternativas (`ALT_SHAPES`)

O grande diferencial harmônico do módulo de Cavaquinho é o suporte nativo a **múltiplas variações de digitação, tríades e inversões no braço** através da estrutura `ALT_SHAPES` e do método `getAlternativeShapes(chordName)`.

### Por que Inversões são Importantes no Cavaquinho?
No cavaquinho (especialmente no samba e choro), o músico frequentemente varia a posição do mesmo acorde subindo e descendo o braço do instrumento (ex: tocar um `D` aberto na 1ª casa ou como tríade na 4ª e 7ª casa) para criar condução melódica de acordes.

O método `getAlternativeShapes` consulta `ALT_SHAPES` e retorna um array com todas as digitações disponíveis para aquele acorde com rótulos descritivos:
```javascript
'G7': [
    { frets: [0, 0, 0, 3], baseFret: 1, label: 'Pos. Aberta (Casa 1)' },
    { frets: [3, 4, 3, 5], baseFret: 3, label: 'Pos. na 3ª Casa' },
    { frets: [5, 7, 6, 7], baseFret: 5, label: 'Pos. na 5ª Casa' }
]
```
Quando o usuário clica no botão **[ 🔄 Variar Posição ]** na interface do `viewer-cavaquinho.html`, o script alterna dinamicamente o índice visualizado entre essas posições.

---

## ⚙️ Principais Métodos Exportados

### `renderCavaquinhoFretboardSVG(chordName, options)`
Gera o código `SVG` contendo as marcações do braço para as 4 cordas.
- Aceita no parâmetro `options` o objeto de shape específico de uma variação (`options.customShape`), permitindo renderizar tanto a posição padrão quanto qualquer digitação alternativa ou tríade selecionada.
- Calcula automaticamente a largura e altura proporcionais, desenhando traste de pestana (`barre`) e numeração lateral da casa inicial (`baseFret`).

### `resolveChordShape(chordName)`
Busca a posição padrão no dicionário, aplicando simplificação harmônica e conversão automática de enarmonias caso uma cifra extremamente complexa seja solicitada na letra da música.

---

## 🔌 Exemplo de Uso Prático

```javascript
// Obtendo todas as posições possíveis de Dm7 no braço
const shapes = window.CavaquinhoChordVisualizer.getAlternativeShapes("Dm7");
console.log(`Encontradas ${shapes.length} digitações para Dm7!`);

// Renderizando a 2ª variação (posição mais alta) em SVG
const svgVariao = window.CavaquinhoChordVisualizer.renderCavaquinhoFretboardSVG("Dm7", {
    customShape: shapes[1],
    width: 130,
    height: 120
});
document.getElementById("cavaquinho-container").innerHTML = svgVariao;
```
