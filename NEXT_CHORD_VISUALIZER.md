# 🎹 Módulo Visualizador de Teclado e Próximo Acorde (`NextChordVisualizer.js`)

O **`NextChordVisualizer.js`** (`assets/modules/NextChordVisualizer.js`) é o módulo front-end responsável por gerenciar a exibição visual de acordes em teclados de piano interativos na interface principal (`viewer.html`). Ele controla tanto o painel de teclado expandido na lateral/fundo quanto os mini-teclados do painel superior flutuante que mostram o **Acorde Atual** e a **Antecipação do Próximo Acorde**.

---

## 🏗️ Arquitetura e Teclado de 2 Oitavas

Para representar adequadamente acordes com inversões, baixo trocado e extensões (como nonas, décimas primeiras e décimas terceiras), o módulo utiliza um modelo de teclado com **24 teclas cromáticas (`C3` a `B4`)**:
```javascript
const PIANO_KEYS_TEMPLATE = [
    // Oitava 3 (Grave / Esquerda)
    { note: 'C3', type: 'white' },
    { note: 'C#3', type: 'black', left: '4.8%' },
    // ... até B3 ...
    // Oitava 4 (Aguda / Direita)
    { note: 'C4', type: 'white' },
    { note: 'C#4', type: 'black', left: '54.8%' },
    // ... até B4 ...
];
```
- **Teclas Brancas (`type: 'white'`):** Renderizadas em camada base flexível.
- **Teclas Pretas (`type: 'black'`):** Renderizadas com posicionamento absoluto em porcentagem (`left: X%`) sobrepostas entre as teclas brancas correspondentes.

---

## 💡 Iluminação Harmônica e Análise de Notas em Comum

Um dos recursos pedagógicos mais poderosos deste módulo é a capacidade de destacar visualmente a **condução de vozes e notas em comum** na transição entre o acorde que está tocando e o próximo acorde da música.

### Classes e Identificação de Cores no Teclado
Quando `renderChord(currentChordId, nextChordId)` é acionado, o módulo analisa os arrays `notes` e `displayNotes` do objeto da música e aplica classes CSS específicas aos elementos das teclas (`div.piano-key`):
1. **`active-note` / `bass-note` (Cor Destaque Principal):** Ilumina as teclas que formam o acorde atual. Se a nota for o baixo (`noteTypes[i] === 'bass'` ou a primeira nota de um acorde `/`), a tecla recebe um tratamento visual destacado (borda/brilho diferenciado para indicar o baixo).
2. **`common-note` (Destaque Dourado/Verde):** Se um `nextChordId` for fornecido (próximo acorde a ser cantado), o módulo realiza uma intersecção de conjuntos entre as notas do acorde atual e as do próximo. As notas compartilhadas por ambos recebem a classe `common-note`, mostrando visualmente ao tecladista quais dedos **não precisam se mover** na mudança de acorde!

---

## ⚙️ Principais Métodos da Classe `NextChordVisualizer`

### `constructor(options)`
Inicializa a instância vinculando os IDs dos elementos HTML do DOM (`containerId`, `pianoId`, `titleId`, `notesContainerId`).

### `renderKeyboard()`
Constrói e injeta dinamicamente o HTML limpo das 24 teclas no contêiner do piano, gerando os atributos `data-note` para identificação rápida por seletores CSS e JavaScript.

### `renderChord(chordId, nextChordId, idx, nextLyric)`
Método principal chamado a cada evento de rolagem ou clique:
1. Limpa todas as iluminações anteriores do teclado.
2. Consulta o objeto global `chordData[chordId]`.
3. Ilumina as teclas corretas com seus nomes musicais gravados sobre a tecla (`C#`, `F#`, etc.).
4. Atualiza o texto do cabeçalho mostrando o nome do acorde em fonte grande e o trecho da próxima linha lírica (`nextLyric`) para antecipação de leitura.

---

## 🔌 Exemplo de Uso Prático

```javascript
// Instanciando o visualizador para o painel principal do teclado
const mainPianoVisualizer = new NextChordVisualizer({
    containerId: 'main-piano-container',
    pianoId: 'piano-keyboard-view',
    titleId: 'current-chord-title',
    notesContainerId: 'next-lyric-preview'
});

// Renderizando a transição entre Am7 e D7(9)
mainPianoVisualizer.renderChord('Am7', 'D7(9)', 0, 'olha que coisa mais linda');
```
