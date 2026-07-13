# Documentação e Estratégia do Projeto "Musica" (Visualizador de Cifras para Piano)

## Objetivo Principal
Criar uma plataforma de leitura de cifras (com ênfase no Piano) super amigável, livre de distrações, responsiva e focada na usabilidade do músico enquanto toca, resolvendo os problemas de lentidão, complexidade excessiva e bugs de interface dos sites tradicionais.

## Arquitetura do Projeto
O projeto não utiliza nenhum framework pesado (React/Vue/Angular). Ele é focado em puro HTML/CSS/Vanilla JS (SSG - Static Site Generation local). 
Toda vez que queremos adicionar uma música nova, rodamos um script Python automatizado que busca os dados, aplica teoria musical, cria a página pronta e a interliga no nosso hub.

### 1. Componentes Principais
* **`index.html` (Hub Principal)**: Página inicial listando todas as músicas geradas, funcionando como o "Cardápio" do pianista.
* **`_TemplateApp/`**: O coração do frontend. Contém a base (HTML, CSS e layout de pianos) limpa e pronta para ser duplicada. Nunca editamos músicas manualmente; melhoramos o template e deixamos o Python replicá-lo.
* **`modules/`**: Componentes JavaScript que podem ser compartilhados entre as músicas (ex: `NextChordVisualizer.js` para prever a próxima nota).
* **`tools/gerar_musica.py`**: O Web Scraper que faz a mágica acontecer. Baixa a música do CifraClub, formata, extrai os acordes, cria a pasta do App injetando o conteúdo, e avisa o Hub que a música chegou.
* **`tools/chord_parser.py` (Motor de Teoria Musical)**: O "Cérebro" que pega qualquer string de acorde absurdo (ex: `Eb7M(9)`, `D/F#`) e o decompõe matematicamente usando intervalos de semitons para encontrar:
  - Tônica, Tríade (Maior/menor/aug/dim), Sétimas, Tensões (9, 11, 13) e Baixos Invertidos.
  - Ele lida com restrições do teclado virtual, como deslocar (shift) todo o acorde uma oitava para cima se o baixo cair abaixo de `C3`, garantindo que toda nota seja visível no piano de 2 oitavas da tela.

### 2. Padrões de Interface (UI/UX)
* **Glassmorphism e Dark Mode**: A interface é construída sobre um tema noturno limpo, focada em não cansar os olhos do músico.
* **Piano Responsivo Fixado (Sticky)**: O painel com as teclas do piano fica fixo na direita (no Desktop) ou no topo (no Celular). Ele nunca tampa o texto da música.
* **Acompanhamento Tátil**: 
  - Hover ou Click num acorde no texto da música faz o piano renderizar o acorde instantaneamente.
  - **Auto-scroll Automático**: Um botão de play desce a tela na velocidade escolhida.
  - O sistema visual avisa qual é a nota atual tocada (verde) e prevê ativamente o *Próximo Acorde* (laranja/amarelo) e seu pedaço de letra correspondente.

### 3. Soluções e Descobertas Críticas do Histórico de Desenvolvimento
* **Scroll Trap no Desktop**: Nunca usar `overflow-y: auto` no painel fixado (`.piano-panel`) para telas grandes, senão o scroll do mouse não rola a letra da música quando o cursor estiver do lado direito. A altura do piano deve ser baseada em `vh` (Viewport Height).
* **Sobreposição de Cabeçalho**: O `<header>` não é fixado no topo para economizar valioso espaço vertical (120px) na leitura.
* **Sharps vs Flats (Sustenidos vs Bemóis)**: O `chord_parser.py` precisa saber usar Bemóis apenas para *exibir* (Display), mas precisa gerar a nota MIDI (para o DOM HTML ler via `data-note`) *obrigatoriamente* usando sustenidos (ex: `Bb` visual -> `A#` interno no DOM), pois o HTML do teclado não mapeia bemóis.
* **Slash Chords (Acordes Invertidos)**: Para evitar que o baixo de um `C/E` fique em `E2` (invisível em um piano `C3-B4`), o motor sempre verifica o acorde gerado: se a nota mais baixa cair antes de `C3`, **tudo** sobe uma oitava.

## Próximos Passos e Melhorias Planejadas
* **Refinamento do Auto-scroll**: Melhorar a detecção das linhas tocadas atualmente durante o auto-scroll (highlight ativo na letra).
* **Teclas Atalho (Keybinds)**: Otimizar o uso de setas do teclado (Esquerda/Direita) para avançar/voltar o cursor de forma mais precisa, baseada na métrica real da música (BPM e compasso).
* **Cache Busting Constante**: Sempre que melhorarmos o CSS do `_TemplateApp`, lembrar de atualizar a versão (ex: `?v=9` -> `?v=10`) no HTML para os usuários (e nosso próprio PC) não lerem CSS antigo cacheado.

---
*Documentação gerada para guiar as sessões futuras com o assistente IA (Antigravity).*
