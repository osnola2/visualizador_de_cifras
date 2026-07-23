# 🐍 Módulo Pipeline Python de Catálogo (`tools/`)

O ecossistema de ferramentas em Python localizado no diretório `tools/` é o **back-end e motor de automação do catálogo** do Visualizador de Cifras. Ele é responsável por extrair, processar, analisar harmonicamente, transpor e converter cifras brutas (texto de sites como CifraClub ou arquivos locais) em estruturas de dados otimizadas (`JavaScript / JSON`) para os visualizadores front-end.

---

## 🏗️ Estrutura e Ferramentas do Pipeline

```text
tools/
├── gerar_musica.py       # Gerador principal: extração web/local, formatação e saída .js
├── chord_parser.py       # Motor analítico: decodifica cifras teóricas em notas, intervalos e MIDI
├── transpor_cifra.py     # Transpositor harmônico: altera tom de músicas e recalcula acidentes
├── generate_catalog.py   # Orquestrador global: varre data/songs/ e compila o hub.js e index.html
└── fix_antonico.py       # Utilitários de higienização e correção pontual de repertório
```

---

## ⚙️ Detalhamento por Ferramenta

### 1. `gerar_musica.py` (O Gerador de Cifras)
É o ponto de entrada para adicionar novas músicas ao repertório.
- **Captura Multi-Fonte:** Aceita tanto URLs diretas (`https://www.cifraclub.com.br/...`) executando *scraping* inteligente quanto arquivos de texto locais (`.txt`).
- **Detecção e Anotação HTML:** Separa automaticamente cabeçalhos (`[intro]`, `[refrão]`), linhas de letra (`<span class="lyric-line">`) e cifras (`<span class="chord" data-chord="X">`).
- **Integração com `chord_parser`:** Para cada cifra encontrada na música, consulta o `chord_parser.py` para montar o dicionário `chordData` completo com as notas, oitavas e funções de cada grau.
- **Geração de Arquivo (`data/songs/NomeDaMusica.js`):** Exporta um arquivo JS limpo atribuindo os dados à variável global `window.SONG_DATA`.

#### Exemplo de Comando via Terminal:
```powershell
# Gerar a partir de URL do CifraClub
python tools/gerar_musica.py "https://www.cifraclub.com.br/artista/musica/"

# Gerar a partir de arquivo de texto local
python tools/gerar_musica.py "caminho/para/letra.txt" --title "Nome" --artist "Artista"
```

---

### 2. `chord_parser.py` (Analisador Teórico Harmônico)
Módulo de teoria musical algorítmica puro, utilizado por `gerar_musica.py` e `transpor_cifra.py`.
- **Regras Teóricas e Escalas:** Constrói escalas maiores, menores e cromáticas para determinar intervalos exatos a partir da tônica (`C`, `C#`, `Db`... `B`).
- **Decodificação de Sufixos Complexos:** Interpreta com precisão acordes de jazz e MPB com tensões acumuladas (`7M(9/13)`, `m7(b5)`, `dim7`, `/F#`, `4/7`).
- **Classificação Funcional (`noteTypes`):** Identifica e rotula cada nota como `bass` (quando há baixo invertido), `root` (tônica), `triad` (terça e quinta), `seventh` (sétima) ou `tension` (nonas, décimas primeiras e décimas terceiras).
- **Atribuição de Oitavas MIDI:** Organiza as notas dentro de uma tessitura de 2 oitavas (`Oitava 3 e 4`), garantindo que a reprodução no `ChordSynth.js` e a exibição no `NextChordVisualizer.js` sigam uma condução de vozes realista.

---

### 3. `transpor_cifra.py` (Transpositor Harmônico Automático)
Permite mudar o tom de uma música já catalogada (ou de um arquivo bruto) com correção enarmônica inteligente.
- **Transposição por Semitons:** Altera o tom em `+N` ou `-N` semitons.
- **Tratamento de Baixo Invertido:** Se a cifra for `D/F#` e for transposta `+2` semitons, converte corretamente tanto a tônica quanto o baixo para `E/G#`.
- **Preservação de Layout:** Mantém toda a estrutura de tags HTML, alinhamento visual da letra e reconstrói o objeto `chordData` com as novas alturas transpostas.

#### Exemplo de Comando:
```powershell
# Subir 2 semitons (+1 tom) na música e atualizar seu arquivo em data/songs/
python tools/transpor_cifra.py data/songs/HotelCoracaoPartido.js --semitones +2
```

---

### 4. `generate_catalog.py` (Compilador de Índice e Hub)
Após adicionar ou remover músicas da pasta `data/songs/`, este script orquestrador atualiza o ecossistema do site:
1. Varre todos os arquivos `.js` dentro de `data/songs/`.
2. Lê os metadados (`title`, `artist`, `composer`) de cada música.
3. Gera/Atualiza a lista global no `assets/js/hub.js` e compila os cards de navegação na página principal `index.html`.

#### Exemplo de Comando:
```powershell
# Atualizar catálogo e índice principal
python tools/generate_catalog.py
```
