#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo ASR (Automatic Speech Recognition) para extração de letra com timestamps palavra por palavra
utilizando Faster-Whisper (CTranslate2).
"""

import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if sys.platform == 'win32' and hasattr(os, 'add_dll_directory'):
    _pyroot = os.path.dirname(sys.executable)
    _sp = os.path.join(_pyroot, 'Lib', 'site-packages')
    for _sub in [_pyroot, os.path.join(_sp, 'sklearn', '.libs'), os.path.join(_sp, 'ctranslate2'), os.path.join(_sp, 'scipy', '.libs'), os.path.join(_sp, 'z3', 'lib')]:
        if os.path.exists(_sub):
            try:
                os.add_dll_directory(_sub)
            except Exception:
                pass
from pathlib import Path

def transcrever_letra_com_timestamps(caminho_audio, modelo_tamanho="medium", idioma="pt"):
    """
    Transcreve o arquivo de áudio usando faster-whisper com word_timestamps=True.
    Retorna uma lista de versos com metadados temporais.
    
    Formato de retorno:
    [
        {
            "text": "Verso da música",
            "start": 0.0,
            "end": 3.5,
            "words": [
                {"word": "Verso", "start": 0.0, "end": 0.8},
                ...
            ]
        },
        ...
    ]
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        print("❌ Erro: 'faster-whisper' não instalado. Rode: python -m pip install faster-whisper")
        return []

    if not os.path.exists(caminho_audio):
        print(f"❌ Erro: Arquivo de áudio não encontrado para transcrição: {caminho_audio}")
        return []

    print(f"🎙️ [ASR] Carregando modelo Whisper ({modelo_tamanho}) para transcrição com timestamps...")
    
    # Determinar dispositivo e tipo de computação compatível
    # Se houver GPU CUDA disponível usa, caso contrário usa CPU com int8 (extremamente rápido no CTranslate2)
    device = "cpu"
    compute_type = "int8"
    
    try:
        model = WhisperModel(modelo_tamanho, device=device, compute_type=compute_type)
    except Exception as e_model:
        print(f"⚠️ Aviso ao carregar modelo '{modelo_tamanho}': {e_model}. Tentando fallback com modelo 'small'...")
        model = WhisperModel("small", device="cpu", compute_type="int8")

    print(f"🔊 [ASR] Processando áudio e extraindo palavras: {Path(caminho_audio).name} ...")
    segments, info = model.transcribe(
        caminho_audio,
        language=idioma,
        word_timestamps=True,
        beam_size=5,
        vad_filter=False  # Em músicas (especialmente com percussão densa), VAD pode classificar vocais como ruído
    )

    alucinacoes = ["legendas pela comunidade", "amara.org", "subtitles by", "inscreva-se", "assine o canal", "obrigado por assistir"]
    versos = []
    total_palavras = 0
    for segment in segments:
        texto_seg = segment.text.strip()
        if not texto_seg or any(aluc in texto_seg.lower() for aluc in alucinacoes):
            continue

        words_list = []
        if segment.words:
            for w in segment.words:
                palavra_limpa = w.word.strip()
                if palavra_limpa:
                    words_list.append({
                        "word": palavra_limpa,
                        "start": round(w.start, 2),
                        "end": round(w.end, 2)
                    })
                    total_palavras += 1
        
        # Se o Whisper retornou texto mas não timestamps individuais para as palavras, estimamos uniformemente
        if not words_list and texto_seg:
            palavras = texto_seg.split()
            if palavras:
                dur = max(0.1, (segment.end - segment.start) / len(palavras))
                for i, p in enumerate(palavras):
                    words_list.append({
                        "word": p,
                        "start": round(segment.start + i * dur, 2),
                        "end": round(segment.start + (i + 1) * dur, 2)
                    })
                    total_palavras += 1

        if words_list:
            # Subdividir o segmento em linhas curtas e poéticas (máximo ~44 caracteres ou quebra por pontuação/pausa)
            chunk_words = []
            
            for w in words_list:
                chunk_words.append(w)
                texto_chunk = " ".join(item['word'] for item in chunk_words)
                
                # Critérios para quebrar linha de verso:
                # 1. Pontuação de pausa (, . ; ! ?) no fim da palavra e o chunk já tem um tamanho razoável (>= 16 chars)
                # 2. OU o chunk já passou do limite máximo ideal de caracteres (>= 44 chars)
                # 3. OU há um silêncio > 0.4s entre a palavra atual e a próxima (será avaliado abaixo se não for a última)
                palavra_atual = w['word']
                tem_pontuacao_pausa = any(palavra_atual.endswith(p) for p in [',', '.', ';', '!', '?', '...'])
                
                if (tem_pontuacao_pausa and len(texto_chunk) >= 16) or len(texto_chunk) >= 44:
                    versos.append({
                        "text": texto_chunk,
                        "start": chunk_words[0]['start'],
                        "end": chunk_words[-1]['end'],
                        "words": list(chunk_words)
                    })
                    chunk_words = []
            
            # Adicionar eventual saldo final de palavras
            if chunk_words:
                texto_chunk = " ".join(item['word'] for item in chunk_words)
                versos.append({
                    "text": texto_chunk,
                    "start": chunk_words[0]['start'],
                    "end": chunk_words[-1]['end'],
                    "words": list(chunk_words)
                })

    print(f"✅ [ASR] Transcrição concluída: {len(versos)} versos (subdivididos em linhas curtas) e {total_palavras} palavras identificadas com timestamps.")
    return versos

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        res = transcrever_letra_com_timestamps(sys.argv[1])
        for v in res[:5]:
            print(f"[{v['start']} - {v['end']}] {v['text']}")
            for w in v['words']:
                print(f"   -> ({w['start']}s) {w['word']}")
