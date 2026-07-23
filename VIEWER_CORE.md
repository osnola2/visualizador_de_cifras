# 🧭 Módulo de Motores de Navegação e Rolagem (`assets/js/`)

Os scripts localizados em `assets/js/` representam o **núcleo funcional de front-end (Controladores)** do projeto. Eles interligam a interface de usuário (DOM dos arquivos `.html`), os dados da música selecionada (`window.SONG_DATA`) e os módulos visuais/sonoros (`GuitarChordVisualizer`, `CavaquinhoChordVisualizer`, `NextChordVisualizer`, `ChordSynth`).

---

## 🏗️ Estrutura de Scripts por Visualizador

```text
assets/js/
├── hub.js                 # Gerenciador da página de catálogo (index.html) e transição para visualizadores
├── script.js              # Controlador principal do Teclado/Piano (viewer.html)
├── script-violao.js       # Controlador principal do Violão (viewer-violao.html)
└── script-cavaquinho.js   # Controlador principal do Cavaquinho (viewer-cavaquinho.html)
```

---

## ⚙️ Funcionalidades Centrais e Mecânicas de Rolagem

Apesar de cada visualizador possuir marcações e botões específicos para o seu instrumento, todos compartilham uma arquitetura robusta de rolagem e sincronização harmônica em tempo real.

### 1. Mapeamento Espacial de Acordes (`allChords`)
Logo após o carregamento da página, o script varre o contêiner de letra e identifica todas as tags `<span class="chord">`. Ele calcula o `getBoundingClientRect()` e a posição absoluta em pixels na página:
- Agrupa acordes por linha (`lineKey`).
- Calcula uma coordenada vertical de acionamento otimizada (`effectiveY`) para que a mudança harmônica aconteça exatamente no momento em que a linha entra na área de leitura do músico.

### 2. Motor de Auto-scroll Contínuo (`autoScrollStep`)
O Auto-scroll não utiliza timers simples de `setInterval` que causam engasgos (`stuttering`); ele opera em alta fluidez com **`requestAnimationFrame`**:
- **Cálculo por BPM e Velocidade (`scrollAccumulator`):** Combina o BPM base da música com o multiplicador do controle deslizante (`speedMultiplier` de `0.5x` a `2.0x`). A cada quadro do monitor, acumula frações de pixel e executa `window.scrollBy({ top: pixels, behavior: 'instant' })` de forma contínua e suave.
- **Sincronização Ativa (`activeChordData`):** À medida que a página rola, o script monitora se a linha de leitura cruzou o `effectiveY` do próximo acorde. Ao detectar a mudança (`activeChordData.element !== currentPlayingChordEl`):
  1. Atualiza o painel superior/lateral chamando `showChord()`.
  2. Adiciona a classe `.active-chord` à cifra na letra da música.
  3. Aciona a síntese sonora em `window.chordSynth.triggerChord()`.

### 3. Navegação por Teclado e Interatividade (`ArrowDown` / `ArrowUp`)
Para músicos que praticam no computador ou com pedais de virada de página Bluetooth, os scripts interceptam eventos de teclado (`keydown`):
- **Setas para Baixo/Direita (`ArrowDown` / `ArrowRight`):** Rola a tela exatamente para a coordenada vertical (`effectiveY - 320px`) do próximo acorde da música.
- **Setas para Cima/Esquerda (`ArrowUp` / `ArrowLeft`):** Volta instantaneamente para o acorde anterior.
- **Clique Direto nas Cifras (`click`):** Permite clicar em qualquer cifra na letra para estudar sua posição no braço/teclado sem precisar rolar a página até ela.

---

## 🎸 Específicos por Instrumento

### `script.js` (Teclado / Piano)
- Controla o painel retrátil de teclado expansível no rodapé (`togglePianoBtn`).
- Conecta-se diretamente à instância do `NextChordVisualizer` para acender teclas e mostrar notas em comum (`common-note`).

### `script-violao.js` (Violão)
- Gerencia a exibição paralela de dois diagramas no cabeçalho: o **Acorde Atual** (`#guitar-current-view`) e o **Próximo Acorde** (`#guitar-next-view`).
- Ajusta dinamicamente a proporção dos SVGs para telas de celular (`isMobile`).

### `script-cavaquinho.js` (Cavaquinho)
- Além dos dois diagramas paralelemos de braço, integra o botão de **[ 🔄 Variar Posição ]** (`#btn-vary-cavaquinho-pos`).
- Ao clicar, consulta as digitações no `CavaquinhoChordVisualizer.getAlternativeShapes()` e alterna o índice visualizado entre posições abertas, tríades no meio do braço e pestanas altas.

---

## 🌐 `hub.js` (O Orquestrador da Home)
O `hub.js` roda na página inicial `index.html`.
- Carrega o array global compilado `window.ALL_SONGS`.
- Gera dinamicamente os cards de música com barra de pesquisa interativa instantânea por título ou artista.
- Disponibiliza botões de atalho para abrir cada música diretamente no visualizador do instrumento desejado (`Teclado`, `Violão` ou `Cavaquinho`).
