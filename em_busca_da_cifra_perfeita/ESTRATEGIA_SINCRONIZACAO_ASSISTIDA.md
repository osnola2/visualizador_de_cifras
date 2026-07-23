# Estratégia de Sincronização Harmônico-Silábica Assistida por Áudio 🎙️🎼

> **Status:** Em Estudo / Laboratório Experimental (`em_busca_da_cifra_perfeita/`)  
> **Objetivo:** Explorar o uso de ferramentas de transcrição temporal (ASR + MIR) como *apoio à sincronização* de cifras curadas, reconhecendo as limitações dos nossos testes anteriores e sem comprometer a integridade do catálogo principal.

---

## 1. Diagnóstico e Premissas de Realidade

Até o momento, nossos testes com extração 100% automática (`audio_to_cifra/extrair_cifra.py`) demonstraram que:
1. **Limitações do MIR (Music Information Retrieval):** Algoritmos automáticos de detecção de acordes (ex: *Chroma Features* via Librosa) geram muito ruído em músicas brasileiras (bossa nova, samba, choro), confundindo extensões (`9ª`, `13ª`, `#11`), ignorando inversões de baixo fundamentais (`A7/C#`, `Fm6/Ab`) e alucinando mudanças em notas de passagem.
2. **Desalinhamento Rítmico:** O canto muitas vezes é síncopado, antecipado ou atrasado em relação à batida harmônica do violão/teclado ("balanço brasileiro").
3. **A Cifra Canônica é Humana:** A verdadeira fidelidade de um Songbook só é atingida pela curadoria teórica humana.

Portanto, **abandonamos a ideia do áudio substituir o curador**. A nova estratégia reposiciona a inteligência artificial (Whisper + Demucs + Librosa) exclusivamente como **Copiloto de Sincronização Temporal (Time-Ruler)**.

---

## 2. A Estratégia do "Copiloto Temporal"

Em vez de pedir ao sistema para adivinhar *quais* são os acordes e *qual* é a letra, nós fornecemos a **Cifra de Texto Canônica** (já validada pelo curador) e pedimos ao áudio apenas para **ancorar os carimbos de tempo (timestamps)**.

```mermaid
flowchart TD
    A[Cifra Canônica em Texto .txt<br/>Acorde sobre a Sílaba Exata] --> C[Mapeamento Estrutural<br/>Acorde X associado à Palavra Y]
    B[Áudio de Referência .wav] --> D[Demucs Separação de Stems<br/>vocals.wav | bass.wav | other.wav]
    D -->|vocals.wav| E[Faster-Whisper ASR<br/>Timestamps exatos de cada Palavra Y]
    D -->|bass + other.wav| F[Librosa Onset Detection<br/>Picos exatos das batidas harmônicas]
    C --> G[Motor de Sincronização Híbrida]
    E -->|Tempo da Voz t_asr| G
    F -->|Batida do Instrumento t_onset| G
    G --> H[Snap-to-Grid Harmônico<br/>Acorde X fixado no milissegundo exato]
    H --> I[Revisão Interativa do Curador]
```

### Passo a Passo do Pipeline Híbrido Proposto:

#### Fase 1: Ancoragem Silábica (Voz Isolada)
- O **Faster-Whisper** (`word_timestamps=True`) roda exclusivamente sobre o stem de voz isolada (`vocals.wav` gerado pelo Demucs).
- Como o nosso arquivo `.txt` já define que o acorde `Bm7` está sobre a palavra *"Lua"* (`Lua azul...`), pegamos o timestamp de início da palavra *"Lua"* (`t_asr = 70.19s`).

#### Fase 2: Ajuste Fino / Snap Harmônico (Instrumentos Isolados)
- Como o cantor pode atrasar ou antecipar a voz em relação à batida do violão, olhamos para os stems `bass.wav` (baixo) e `other.wav` (violão/teclado).
- No intervalo de janela curta `[t_asr - 0.4s, t_asr + 0.4s]`, rodamos um detector de transiente (`librosa.onset.onset_detect`).
- O sistema faz o **"Snap" (encaixe automático)** do acorde `Bm7` no exato milissegundo em que as cordas do violão/baixo foram atacadas (ex: `t_final = 70.15s`).

#### Fase 3: Validação no Visualizador
- O curador visualiza a música rodando em tempo real com o áudio. Se um acorde estiver 100ms fora, ele pode fazer um ajuste pontual (nudging) no arquivo de configuração, em vez de transcrever na mão do zero.

---

## 3. Benefícios Práticos para o Nosso Catálogo

1. **Catálogo `gerar_musica.py` Intocado:** O formato atual que converte `.txt` para `.js`/`.json` continua sendo o pilar estável.
2. **Suporte Evolutivo:** Se no futuro quisermos que o visualizador não apenas mostre o desenho do acorde, mas **ilumine o acorde exatamente no milissegundo em que ele toca na música original**, essa estratégia nos dará a tabela de tempos (`chords_timeline.json`) sem esforço manual titânico.
3. **Fase de Testes Controlados:** Todos os experimentos dessa estratégia ficarão contidos na pasta `em_busca_da_cifra_perfeita/`, servindo como laboratório de P&D (Pesquisa e Desenvolvimento) antes de qualquer aplicação em escala.
