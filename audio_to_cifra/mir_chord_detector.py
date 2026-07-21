#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo MIR (Music Information Retrieval) para extração harmônica e identificação
de acordes (incluindo extensões típicas de MPB/Samba como 7M, m7, 6/9, m7b5 e °)
com marcação temporal (timestamps) a partir de arquivos de áudio.
"""

import os
import sys
from pathlib import Path
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
import numpy as np
import librosa
from scipy.ndimage import median_filter, uniform_filter1d

# Nomes das 12 notas cromáticas
NOTAS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Dicionário ampliado de templates de acordes (intervalos em semitons)
# 0=Tônica, 1=2m/9b, 2=2/9, 3=3m, 4=3M, 5=4, 6=4+/5b, 7=5J, 8=5+/6m, 9=6M/13, 10=7m, 11=7M
TEMPLATES_BASE = {
    '':        [0, 4, 7],           # Maior
    'm':       [0, 3, 7],           # Menor
    '7M':      [0, 4, 7, 11],       # Maior com 7M
    '7':       [0, 4, 7, 10],       # Dominante com 7
    'm7':      [0, 3, 7, 10],       # Menor com 7
    '6/9':     [0, 2, 4, 7, 9],     # 6/9 (Clássico Samba/MPB)
    '4(add9)': [0, 2, 5, 7],        # sus4 com nona (ex: G#4(add9) quartal Cancioneiro)
    'm7(b5)':  [0, 3, 6, 10],       # Meio diminuto
    '°':       [0, 3, 6, 9],        # Diminuto
    '9':       [0, 2, 4, 7, 10],    # Dominante com 9 (ex: Bb9)
    'm9':      [0, 2, 3, 7, 10],    # Menor com 9 (ex: Am9)
    '7M(9)':   [0, 2, 4, 7, 11],    # Maior com 7M e 9
    '6':       [0, 4, 7, 9],        # Maior com 6
    'm6':      [0, 3, 7, 9],        # Menor com 6M
    'm6-':     [0, 3, 7, 8],        # Menor com 6m/b6 (ex: Am6- do Clube da Esquina)
    '4':       [0, 5, 7],           # sus4 (ex: E4)
    '7(4)':    [0, 5, 7, 10],       # 7sus4
}

def construir_dicionario_acordes():
    """Constrói matriz de templates (192 acordes x 12 notas) normalizada."""
    nomes_acordes = []
    matriz_templates = []
    
    for i_root, nota_root in enumerate(NOTAS):
        for suf_nome, intervalos in TEMPLATES_BASE.items():
            nome_cifra = f"{nota_root}{suf_nome}"
            vetor = np.zeros(12)
            for intervalo in intervalos:
                vetor[(i_root + intervalo) % 12] = 1.0
            
            # Normalizar para cosseno
            vetor_norm = vetor / np.linalg.norm(vetor)
            nomes_acordes.append(nome_cifra)
            matriz_templates.append(vetor_norm)
            
    return nomes_acordes, np.array(matriz_templates)

NOMES_ACORDES, MATRIZ_TEMPLATES = construir_dicionario_acordes()

def carregar_audio_universal(caminho_audio, sr=22050):
    """
    Carrega áudio em mono utilizando PyAV (av) com reamostragem,
    ou soundfile/librosa como fallback, dispensando ffmpeg externo.
    """
    try:
        import av
        container = av.open(caminho_audio)
        stream = container.streams.audio[0]
        resampler = av.AudioResampler(format='flt', layout='mono', rate=sr)
        
        frames = []
        for frame in container.decode(stream):
            for resampled_frame in resampler.resample(frame):
                frames.append(resampled_frame.to_ndarray().flatten())
        for resampled_frame in resampler.resample(None):
            frames.append(resampled_frame.to_ndarray().flatten())
            
        y = np.concatenate(frames, axis=0) if frames else np.zeros(0, dtype=np.float32)
        return y, sr
    except Exception as e_av:
        return librosa.load(caminho_audio, sr=sr, mono=True)

def detectar_acordes_com_timestamps(caminho_audio, hop_length=1024, min_duracao_seg=0.35):
    """
    Analisa o áudio com Constant-Q Transform (Chromagrama CQT) e correlaciona com o
    dicionário de acordes. Retorna lista de intervalos harmônicos estáveis:
    [
        {"start": 0.0, "end": 3.2, "chord": "G6/9"},
        {"start": 3.2, "end": 6.5, "chord": "C7M"},
        ...
    ]
    """
    if not os.path.exists(caminho_audio):
        print(f"❌ Erro [MIR]: Arquivo de áudio não encontrado -> {caminho_audio}")
        return []

    print(f"🎼 [MIR] Carregando áudio e calculando Chromagrama CQT para: {Path(caminho_audio).name} ...")
    try:
        y, sr = carregar_audio_universal(caminho_audio, sr=22050)
    except Exception as e_load:
        print(f"❌ Erro [MIR] ao ler áudio com librosa/av: {e_load}")
        return []

    # Separar componente harmônica da percussiva (HPSS) para o Chromagrama não sofrer com bateria/ritmo
    print("🥁 [MIR] Separando frequências harmônicas da percussão (HPSS)...")
    y_harm, _ = librosa.effects.hpss(y)

    # Estimar afinação (tuning) para compensar desvios em rotação de vinil/fita de gravações analógicas (1970s)
    print("🎯 [MIR] Estimando e compensando afinação da gravação (A4=440Hz +/- cents)...")
    tuning_estimado = librosa.estimate_tuning(y=y_harm, sr=sr)

    # Calcular Chromagrama Constant-Q compensado pela afinação
    chroma = librosa.feature.chroma_cqt(y=y_harm, sr=sr, hop_length=hop_length, bins_per_octave=36, tuning=tuning_estimado)
    
    # Normalizar chromagrama por frame
    chroma_norm = librosa.util.normalize(chroma, norm=2, axis=0)
    
    # Calcular similaridade de cosseno (produto matricial) entre templates (192x12) e frames (12xN)
    print("🎹 [MIR] Correlacionando com dicionário harmônico ampliado (192 templates com 9ª, sus4, m6-)...")
    similitudes = np.dot(MATRIZ_TEMPLATES, chroma_norm) # Formato (192, n_frames)
    
    # Extração de graves (C1 a C4 = 32 Hz a 261 Hz) para identificar com precisão a nota do baixo
    print("🎸 [MIR] Analisando frequências graves (C1-C4) para detecção de baixos invertidos (slash chords)...")
    cqt_baixo = np.abs(librosa.cqt(y=y_harm, sr=sr, hop_length=hop_length, fmin=librosa.note_to_hz('C1'), n_bins=36, bins_per_octave=12, tuning=tuning_estimado))
    chroma_baixo = cqt_baixo[0:12] + cqt_baixo[12:24] + cqt_baixo[24:36]
    chroma_baixo_norm = librosa.util.normalize(chroma_baixo, norm=2, axis=0)
    
    # Suavização temporal contínua da matriz de similaridade e do baixo (~0.4s) antes do argmax
    frames_por_seg = sr / hop_length
    janela_suavizacao = max(3, int(0.4 * frames_por_seg))
    similitudes_suavizadas = uniform_filter1d(similitudes, size=janela_suavizacao, axis=1)
    chroma_baixo_suavizado = uniform_filter1d(chroma_baixo_norm, size=janela_suavizacao, axis=1)
    indices_baixo = np.argmax(chroma_baixo_suavizado, axis=0)
    
    # Favorecer acordes cuja harmonia contém a nota do baixo fundamental (evita falsos positivos como G4 quando é Am/G)
    # E favorecer templates canônicos e limpos de songbook (ex: m7, 4(add9), 6/9, 7M) para evitar poluição de acordes complexos transitórios
    similitudes_ponderadas = np.copy(similitudes_suavizadas)
    n_templates_por_root = len(TEMPLATES_BASE)
    
    # Índices dos templates mais limpos/canônicos da MPB e Tom Jobim no dicionário TEMPLATES_BASE
    chaves_base = list(TEMPLATES_BASE.keys())
    canonic_indices = [chaves_base.index(k) for k in ['', 'm', 'm7', '7M', '6/9', '4(add9)', '7', '7(4)'] if k in chaves_base]
    
    for t in range(similitudes_suavizadas.shape[1]):
        b_idx = indices_baixo[t]
        for k in range(len(NOMES_ACORDES)):
            idx_suf = k % n_templates_por_root
            if MATRIZ_TEMPLATES[k, b_idx] > 0.0:
                similitudes_ponderadas[k, t] += 0.15 * chroma_baixo_suavizado[b_idx, t]
            if idx_suf in canonic_indices:
                similitudes_ponderadas[k, t] += 0.04  # Pequeno bônus de estabilidade para notações limpas do Cancioneiro
                
    # Índice do melhor acorde por frame
    melhores_indices = np.argmax(similitudes_ponderadas, axis=0)
    
    # Pequeno filtro de mediana para remover micro-saltos de 1 ou 2 frames (~0.25s)
    janela_mediana = max(3, int(0.25 * frames_por_seg))
    if janela_mediana % 2 == 0:
        janela_mediana += 1
    indices_suavizados = median_filter(melhores_indices, size=janela_mediana)
    
    # Construir nomes dos acordes com suas respectivas inversões de baixo (/X) apenas quando for uma inversão real e estável
    acordes_nomes_com_inversao = []
    for i in range(len(indices_suavizados)):
        idx_ac = indices_suavizados[i]
        idx_rt = idx_ac // n_templates_por_root
        idx_bx = indices_baixo[i]
        nome_base = NOMES_ACORDES[idx_ac]
        
        # Só anota inversão /X se a nota do baixo for diferente da tônica E tiver energia substancialmente superior à tônica no grave
        if idx_bx != idx_rt and MATRIZ_TEMPLATES[idx_ac, idx_bx] > 0.0 and (chroma_baixo_suavizado[idx_bx, i] - chroma_baixo_suavizado[idx_rt, i] > 0.22):
            acordes_nomes_com_inversao.append(f"{nome_base}/{NOTAS[idx_bx]}")
        else:
            acordes_nomes_com_inversao.append(nome_base)
            
    # Converter sequência de frames em blocos com timestamps iniciais e finais
    acordes_detectados = []
    acorde_atual = acordes_nomes_com_inversao[0]
    frame_inicio = 0
    n_frames = len(acordes_nomes_com_inversao)
    
    for i in range(1, n_frames):
        acorde_i = acordes_nomes_com_inversao[i]
        if acorde_i != acorde_atual:
            tempo_inicio = librosa.frames_to_time(frame_inicio, sr=sr, hop_length=hop_length)
            tempo_fim = librosa.frames_to_time(i, sr=sr, hop_length=hop_length)
            duracao = tempo_fim - tempo_inicio
            
            if duracao >= min_duracao_seg or not acordes_detectados:
                acordes_detectados.append({
                    "chord": acorde_atual,
                    "start": round(float(tempo_inicio), 2),
                    "end": round(float(tempo_fim), 2),
                    "duration": round(float(duracao), 2)
                })
            else:
                # Se for muito curto, funde com o acorde anterior se houver
                if acordes_detectados:
                    acordes_detectados[-1]["end"] = round(float(tempo_fim), 2)
                    acordes_detectados[-1]["duration"] = round(acordes_detectados[-1]["end"] - acordes_detectados[-1]["start"], 2)
            
            acorde_atual = acorde_i
            frame_inicio = i
            
    # Adicionar último bloco
    tempo_inicio = librosa.frames_to_time(frame_inicio, sr=sr, hop_length=hop_length)
    tempo_fim = librosa.frames_to_time(n_frames, sr=sr, hop_length=hop_length)
    duracao = tempo_fim - tempo_inicio
    if duracao >= min_duracao_seg or not acordes_detectados:
        acordes_detectados.append({
            "chord": acorde_atual,
            "start": round(float(tempo_inicio), 2),
            "end": round(float(tempo_fim), 2),
            "duration": round(float(duracao), 2)
        })
    elif acordes_detectados:
        acordes_detectados[-1]["end"] = round(float(tempo_fim), 2)
        acordes_detectados[-1]["duration"] = round(acordes_detectados[-1]["end"] - acordes_detectados[-1]["start"], 2)

    # Mesclar blocos consecutivos que terminaram com o mesmo nome de acorde
    acordes_mesclados = []
    for ac in acordes_detectados:
        if acordes_mesclados and acordes_mesclados[-1]["chord"] == ac["chord"]:
            acordes_mesclados[-1]["end"] = ac["end"]
            acordes_mesclados[-1]["duration"] = round(acordes_mesclados[-1]["end"] - acordes_mesclados[-1]["start"], 2)
        else:
            acordes_mesclados.append(ac)
    acordes_detectados = acordes_mesclados

    print(f"✅ [MIR] Extração harmônica concluída: {len(acordes_detectados)} blocos de acordes identificados.")
    return acordes_detectados

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        res = detectar_acordes_com_timestamps(sys.argv[1])
        for item in res[:15]:
            print(f"[{item['start']:6.2f}s -> {item['end']:6.2f}s] {item['chord']}")
