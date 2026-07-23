# 🎵 Sintetizador Harmônico Web Audio (`ChordSynth.js`)

O **ChordSynth** é o motor de áudio polifônico nativo desenvolvido para o **Visualizador de Cifras**. Ele permite que os acordes das músicas sejam reproduzidos em tempo real durante o **Auto-scroll** ou quando o usuário clica interativamente em qualquer cifra na letra da música, proporcionando um feedback sonoro preciso para o estudo de acordes no Violão, Teclado e Cavaquinho.

---

## 🌟 Principais Destaques e Diferenciais

- **100% Nativo (Web Audio API):** Não utiliza nenhuma biblioteca de terceiros (como Tone.js) nem arquivos de áudio externos (`.mp3`, `.wav` ou SoundFonts pesados). Todo o som é sintetizado matematicamente em tempo real no navegador do usuário.
- **Polifonia Harmônica Real:** Cada nota do acorde é gerada em sua frequência exata em Hertz (Hz) a partir da notação científica de oitavas (Midi Pitch).
- **Acústica Orgânica e Reverb de Sala:** Possui um barramento mestre com `ConvolverNode` gerado algoritmicamente, simulando a ressonância da caixa de madeira de um violão ou o corpo de um piano acústico.
- **Dedilhado Humanizado (`Strumming Effect`):** As notas não entram secas ao mesmo tempo; são arpejadas com um micro-atraso de ~38 milissegundos entre si, reproduzindo com fidelidade o movimento físico de uma palheta ou dos dedos dedilhando as cordas do grave para o agudo.

---

## 🐞 O Problema Histórico e a Solução Crítica (`notes` vs `displayNotes`)

Durante o desenvolvimento, identificou-se que todos os acordes tocavam com o **mesmo som agudo e estático (440 Hz / Nota A4)**. A análise da arquitetura revelou uma peculiaridade no fluxo de dados exportado pelo pipeline Python (`chord_parser.py` e `gerar_musica.py`):

### Estrutura de um Acorde Gerado (`chordData`)
Ao converter uma cifra como **A7** ou **D7M**, o sistema gera um objeto no arquivo `.js` da música contendo dois arrays distintos:
```json
"A7": {
    "name": "A7",
    "notes": ["A3", "C#4", "E4", "G4"],
    "displayNotes": ["A", "C#", "E", "G"],
    "noteTypes": ["root", "triad", "triad", "seventh"]
}
```

- **`notes`**: Contém as alturas musicais exatas com o número da oitava (`A3`, `C#4`, etc.), essenciais para calcular a frequência midi e o som em Hertz.
- **`displayNotes`**: Contém apenas o nome visual da nota sem a oitava (`A`, `C#`, etc.), utilizado exclusivamente para renderizar o diagrama visual de notas na tela.

### O Conflito e a Correção
Na implementação original, a ordem de leitura do sintetizador estava priorizando `displayNotes` sobre `notes`:
```javascript
// ❌ IMPLEMENTAÇÃO ANTIGA (Incorreta)
noteList = notes.displayNotes || notes.notes || [];
```
Como as strings em `displayNotes` não possuem o número da oitava (`"A"`, `"C#"`), a expressão regular (`RegExp`) de conversão de nota para frequência falhava ao tentar extrair a oitava. O código caía no bloco de segurança (*fallback*) de programação, retornando **440 Hz para todas as notas do acorde**. O resultado era um som estático, onde 4 ou 5 notas tocavam exatamente na mesma frequência.

A correção reestruturou o motor de áudio para **priorizar estritamente as alturas harmônicas de `notes.notes`**, além de incluir inteligência autônoma para inferir oitavas de baixo e agudo caso notas sem oitava sejam fornecidas:
```javascript
// ✅ IMPLEMENTAÇÃO CORRETA E ROBUSTA
noteList = notes.notes || notes.displayNotes || [];
```

---

## ⚙️ Arquitetura do Sintetizador (`assets/modules/ChordSynth.js`)

### 1. Conversão de Notas para Frequência (`noteToFreq`)
A função converte qualquer notação musical científica (`C3`, `F#4`, `Bb2`) em frequência exata utilizando a fórmula de temperamento igual a partir de A4 = 440 Hz:

$$\text{Freq (Hz)} = 440 \times 2^{\frac{\text{MIDI} - 69}{12}}$$

Se a oitava for omitida, o algoritmo identifica a posição da nota no acorde: atribui a **oitava 3** para a primeira nota (Raiz/Baixo) e a **oitava 4** para o restante da harmonia.

### 2. Síntese de Voz e Timbres (`playVoice`)
Cada nota do acorde é processada por uma célula de voz que combina **dois osciladores simultâneos (`OscillatorNode`)** e um **filtro dinâmico (`BiquadFilterNode`)**:
- **Desafinação Estéreo (+1.8 cents):** O segundo oscilador toca com uma frequência ligeiramente superior (`freq * 1.0018`), criando um efeito de *chorus* natural que encorpa o som de cordas.
- **Filtro Passa-Baixa Dinâmico:** Simula o brilho inicial do ataque da palheta ou martelo que rapidamente se suaviza.
- **Tratamento de Baixo (`isBass`):** A nota fundamental de cada acorde recebe maior energia no filtro passa-baixa (`1800 Hz -> 300 Hz`) e um ganho 15% superior para dar sustentação e peso ao acorde.

#### Timbres Disponíveis (`currentTimbre`):
| Timbre | Instrumentos Alvo | Osciladores (`Osc1 + Osc2`) | Filtro Passa-Baixa |
| :--- | :--- | :--- | :--- |
| **`acoustic`** | Violão e Cavaquinho | `triangle` + `sawtooth` | `3400 Hz -> 450 Hz` (rápido decaimento madeira) |
| **`piano`** | Teclado / Piano | `triangle` + `sine` | `2800 Hz -> 450 Hz` + Harmônico dobro (`2x freq`) |
| **`pad`** | Texturas / Synth | `sawtooth` + `triangle` | `600 Hz -> 1600 Hz` (ataque lento em rampa) |

### 3. Barramento Mestre e Reverb (`setupMasterBus`)
Para evitar que os acordes soem secos, o `ChordSynth` constrói na inicialização um `ConvolverNode` carregado com uma resposta ao impulso (Impulse Response) gerada matematicamente com decaimento exponencial de 1.8 segundos. O sinal de cada nota é dividido:
- **78% Sinal Direto (`Dry`)** -> Para clareza das notas.
- **22% Sinal Reverberado (`Wet`)** -> Para profundidade espacial e ressonância.

### 4. Proteção Anti-Saturação e Acúmulo no Scroll Rápido
Quando o usuário rola a tela muito rápido ou arrasta a barra de rolagem bruscamente, dezenas de acordes poderiam ser acionados em fração de segundos, empilhando centenas de osciladores simultâneos e estourando o volume (`clipping / distorção > 0dBFS`). Para garantir som limpo e proteger os alto-falantes, foram implementadas 3 camadas de proteção:
1. **Limiter Brickwall (`DynamicsCompressorNode`):** Conectado logo antes do destino final de saída (`ctx.destination`). Configurado com `ratio: 20.0`, `threshold: -4.0 dB` e `attack: 1ms`, atua como uma barreira física que impede matematicamente o áudio de ultrapassar o limite máximo sem distorcer.
2. **Voice Stealing (Corte Suave de Acordes Anteriores):** Antes de iniciar um novo acorde, o método `stopActiveVoices(0.06)` aplica um rápido *fade-out* exponencial de 60 milissegundos nas notas que ainda estão soando e desliga seus osciladores. Isso mantém a clareza harmônica do acorde atual sem acúmulo infinito de sons.
3. **Controle Anti-Rajada (`Throttle`):** Se a roletagem da tela disparar acordes com intervalo inferior a 85 milissegundos (`now - lastChordTime < 0.085`), o sintetizador ignora os disparos intermediários, evitando o efeito "metralhadora".

---

## 🎮 Como Funciona na Interface (UI e Scripts)

O módulo é instanciado globalmente como `window.chordSynth` e está integrado diretamente aos três visualizadores do projeto:
- `viewer.html` (Teclado) $\rightarrow$ Timbre configurado como `piano`.
- `viewer-violao.html` (Violão) $\rightarrow$ Timbre configurado como `acoustic`.
- `viewer-cavaquinho.html` (Cavaquinho) $\rightarrow$ Timbre configurado como `acoustic`.

### 🎛️ Botão de Controle no Cabeçalho
Localizado ao lado do botão de rolagem automática:
- **`[ 🔇 Áudio: OFF ]` (Padrão):** O `AudioContext` permanece suspenso/inativo para economizar processamento e não interromper o silêncio do usuário.
- **`[ 🔊 Áudio: ON ]` (Ativado):** Ao clicar, o navegador libera o `AudioContext` e o botão muda de cor para indicar que a síntese está ativa.

### 🔄 Acionamento no Auto-scroll (`autoScrollStep`)
Durante o **Auto-scroll** ou navegação pelo teclado (`Seta para Baixo ⬇` / `Seta para Cima ⬆`), os scripts monitoram a posição vertical das linhas. Assim que a rolagem entra na zona de um novo acorde ativo (`activeChordData.element !== currentPlayingChordEl`), o sintetizador é acionado automaticamente:
```javascript
if (window.chordSynth && window.chordSynth.isAudioEnabled && chordData[activeChordData.chordName]) {
    window.chordSynth.triggerChord(chordData[activeChordData.chordName]);
}
```

### 👆 Acionamento Interativo ao Clicar na Cifra (`click`)
Para facilitar o estudo e conferência de acordes, cada tag `<span class="chord">` na letra da música possui um listener de clique. Se o áudio estiver ativado, clicar sobre qualquer cifra reproduz instantaneamente o som daquele acorde:
```javascript
el.addEventListener('click', () => {
    // ... lógica de exibir diagrama do acorde ...
    if (window.chordSynth && window.chordSynth.isAudioEnabled && chordData[cId]) {
        window.chordSynth.triggerChord(chordData[cId]);
    }
});
```

---

## 📁 Estrutura de Arquivos Modificados
- `assets/modules/ChordSynth.js` *(Novo)* - Módulo principal do sintetizador Web Audio.
- `assets/js/script.js` - Conexão do áudio com o visualizador de Teclado.
- `assets/js/script-violao.js` - Conexão do áudio com o visualizador de Violão.
- `assets/js/script-cavaquinho.js` - Conexão do áudio com o visualizador de Cavaquinho.
- `viewer.html`, `viewer-violao.html`, `viewer-cavaquinho.html` - Inclusão do botão de áudio no painel flutuante de navegação e carregamento do script do módulo.
