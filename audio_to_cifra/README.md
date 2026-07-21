# 🎧 Audio to Cifra (Extração de Cifras por Áudio e MIR)

Esta pasta é o **maquinário dedicado** ao processamento de áudio, detecção harmônica e transcrição automática de letras para geração de cifras alinhadas.

---

## 📁 Estrutura da Pasta

```
audio_to_cifra/
├── 📄 extrair_cifra.py           # Script principal (CLI) para iniciar a extração (MIR + Whisper + Gemini Híbrido)
├── 📄 mir_chord_detector.py      # Módulo de análise harmônica acústica (Librosa CQT Chromagram + HPSS + templates)
├── 📄 asr_lyrics_transcriber.py  # Módulo de transcrição de voz com timestamps palavra-a-palavra (Faster-Whisper)
├── 📄 pipeline_alinhador.py      # Módulo de alinhamento temporal e gramática musical (Opção 1 determinística + Opção 2 Gemini Híbrida)
├── 📄 plano_cifra_por_audio.md   # Documentação arquitetural detalhada e plano original do projeto
├── 📁 audios/                    # Armazena os arquivos de áudio baixados do YouTube ou fornecidos pelo usuário (.mp3, .m4a, .webm)
└── 📁 transcricoes/              # Armazena os resultados gerados em fase de teste (.txt com a cifra e _dados_temporais.json)
```

---

## 🚀 Como Executar o Pipeline

### 1. Extração Opção 1 (MIR + Whisper com Alinhamento Determinístico)
Analisa as notas físicas da orquestra/violão e posiciona os acordes exatamente sobre as sílabas transcritas:
```powershell
python audio_to_cifra/extrair_cifra.py "https://youtu.be/SEU_LINK_AQUI"
```

### 2. Extração Opção 2 (Híbrida com Inteligência Artificial Gemini)
Envia os dados acústicos brutos (`_dados_temporais.json`) para o Gemini atuar como arranjador e aplicar a teoria e harmonia da Bossa Nova / MPB:
```powershell
python audio_to_cifra/extrair_cifra.py "audio_to_cifra/audios/SuaMusica.m4a" --hibrido
```

---

## 🔒 Isolamento do Catálogo
Todos os testes, áudios e transcrições geradas aqui ficam **100% isolados** em `audio_to_cifra/audios/` e `audio_to_cifra/transcricoes/`.
Nada entra no catálogo oficial (`index.html` ou `data/songs/`) a não ser que o usuário decida validar e incorporar o arquivo manualmente via ferramenta de catalogação.
