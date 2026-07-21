#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de Alinhamento Temporal e Formatação para cruzar acordes (MIR) e letras (ASR Whisper)
e gerar a cifra musical tradicional no padrão Songbook / Almir Chediak.
"""

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pathlib import Path

def alinhar_deterministico(acordes, versos):
    """
    Cruza as marcações de tempo de acordes e palavras para gerar a cifra formatada em texto.
    """
    if not versos:
        # Se for uma música sem letra instrumental, formata apenas a progressão
        cifra_out = "[Solo / Instrumental]\n"
        linha_acordes = []
        for ac in acordes:
            linha_acordes.append(ac['chord'])
            if len(linha_acordes) >= 4:
                cifra_out += "  ".join(linha_acordes) + "\n"
                linha_acordes = []
        if linha_acordes:
            cifra_out += "  ".join(linha_acordes) + "\n"
        return cifra_out

    cifra_linhas = []
    
    # 1. Identificar Acordes da Intro (que ocorrem antes do primeiro verso vocal com margem de 1s)
    inicio_voz = versos[0]['start']
    acordes_intro = [ac['chord'] for ac in acordes if ac['end'] <= inicio_voz + 0.5]
    
    if acordes_intro:
        cifra_linhas.append("[Intro]")
        # Agrupar de 4 em 4 para ficar legível
        for i in range(0, len(acordes_intro), 4):
            grupo = acordes_intro[i:i+4]
            cifra_linhas.append("  ".join(grupo))
        cifra_linhas.append("")
    
    # Índice do acorde atual sendo processado
    ultimo_acorde_usado = -1
    
    for i_v, verso in enumerate(versos):
        v_start = verso['start']
        v_end = verso['end']
        texto_verso = verso['text']
        palavras = verso.get('words', [])
        
        # Encontrar acordes que iniciam durante este verso (ou logo antes se for a primeira palavra)
        acordes_do_verso = []
        for i_ac, ac in enumerate(acordes):
            # Se o acorde começa entre o início do verso - 0.6s e o fim do verso
            if v_start - 0.6 <= ac['start'] <= v_end + 0.3:
                if i_ac > ultimo_acorde_usado:
                    acordes_do_verso.append(ac)
                    ultimo_acorde_usado = i_ac

        # Se não há novo acorde no verso ou se o primeiro novo acorde só entra depois de 0.5s do início do verso,
        # verificamos o acorde ativo vigente para posicioná-lo no começo da frase (coluna 0)
        acordes_ativos = [ac for ac in acordes if ac['start'] <= v_start < ac['end']]
        ac_vigente = acordes_ativos[-1] if acordes_ativos else None

        if not acordes_do_verso:
            # Verso sem mudança nova: exibir o acorde vigente no início para nunca deixar a linha sem cifra
            if ac_vigente:
                cifra_linhas.append(ac_vigente['chord'])
            cifra_linhas.append(texto_verso)
        else:
            # Se o primeiro acorde novo só entra no meio/fim do verso (e não na primeira palavra), prefixa o acorde vigente
            if ac_vigente and acordes_do_verso[0]['start'] > v_start + 0.5 and ac_vigente['chord'] != acordes_do_verso[0]['chord']:
                ac_copia = dict(ac_vigente)
                ac_copia['start'] = v_start # Para alinhar na primeira palavra
                acordes_do_verso.insert(0, ac_copia)
            # Construir a linha superior com os acordes posicionados no índice de coluna da palavra correspondente
            if not palavras:
                # Se não temos palavras separadas por algum motivo, coloca os acordes no início
                linha_sup = "  ".join([ac['chord'] for ac in acordes_do_verso])
                cifra_linhas.append(linha_sup)
                cifra_linhas.append(texto_verso)
            else:
                linha_acorde = [" "] * (len(texto_verso) + 30)
                
                # Mapear posições de caractere para cada palavra do verso
                posicoes_palavras = []
                idx_atual = 0
                for w in palavras:
                    pal = w['word']
                    idx_find = texto_verso.find(pal, idx_atual)
                    if idx_find != -1:
                        posicoes_palavras.append((idx_find, w['start'], w['end'], pal))
                        idx_atual = idx_find + len(pal)
                    else:
                        posicoes_palavras.append((idx_atual, w['start'], w['end'], pal))

                # Alocar cada acorde sobre a palavra com timestamp mais próximo
                ultima_col_escrita = -2
                ultimo_nome_escrito = None
                for ac in acordes_do_verso:
                    nome_ac = ac['chord']
                    if nome_ac == ultimo_nome_escrito:
                        continue # Evitar repetir o mesmo acorde na mesma linha de verso

                    ac_tempo = ac['start']
                    melhor_pos = 0
                    menor_dist = 999.0
                    
                    for pos_char, w_start, w_end, w_texto in posicoes_palavras:
                        dist = abs(ac_tempo - w_start)
                        if dist < menor_dist:
                            menor_dist = dist
                            melhor_pos = pos_char
                    
                    # Garantir que não sobreponha acorde anterior (mínimo 2 espaços limpos)
                    pos_escrita = max(melhor_pos, ultima_col_escrita + 2)
                    
                    if pos_escrita + len(nome_ac) >= len(linha_acorde):
                        linha_acorde.extend([" "] * (len(nome_ac) + 30))
                        
                    for k, char in enumerate(nome_ac):
                        linha_acorde[pos_escrita + k] = char
                        
                    ultima_col_escrita = pos_escrita + len(nome_ac)
                    ultimo_nome_escrito = nome_ac
                
                linha_acorde_str = "".join(linha_acorde).rstrip()
                if linha_acorde_str.strip():
                    cifra_linhas.append(linha_acorde_str)
                cifra_linhas.append(texto_verso)
        
        # Verificar se há um solo/interlúdio longo entre este verso e o próximo
        if i_v < len(versos) - 1:
            proximo_inicio = versos[i_v + 1]['start']
            gap = proximo_inicio - v_end
            if gap >= 4.0:
                acordes_gap = [ac['chord'] for i_ac, ac in enumerate(acordes) if i_ac > ultimo_acorde_usado and v_end + 0.3 < ac['start'] < proximo_inicio - 0.4]
                if acordes_gap:
                    cifra_linhas.append("\n[Interlúdio / Solo]")
                    for j in range(0, len(acordes_gap), 4):
                        cifra_linhas.append("  ".join(acordes_gap[j:j+4]))
                    cifra_linhas.append("")

    return "\n".join(cifra_linhas)

def alinhar_hibrido_com_gemini(acordes, versos, titulo, artista, client, modelo):
    """
    Usa o Gemini como arranjador final/revisor para formatar a cifra com acabamento Songbook,
    alimentado pelos timestamps matemáticos de acordes (MIR) e palavras (Whisper).
    """
    from google.genai import types
    
    resumo_acordes = "\n".join([f"[{ac['start']}s - {ac['end']}s]: {ac['chord']}" for ac in acordes])
    resumo_versos = "\n".join([f"[{v['start']}s - {v['end']}s]: {v['text']}" for v in versos])
    
    prompt = f"""
Você é um arranjador e revisor musical profissional (Estilo Songbook MPB/Samba / Cancioneiro Tom Jobim).
Música: "{titulo or 'Desconhecido'}"
Artista: "{artista or 'Desconhecido'}"

Abaixo estão os dados exatos extraídos algorítmicamente por processamento de sinal:
1. ACORDES DETECTADOS POR CHROMA CQT (com timestamps):
{resumo_acordes}

2. LETRA E VERSOS TRANSCRITOS POR WHISPER (com timestamps):
{resumo_versos}

SUA MISSÃO:
Cruze os tempos das duas tabelas e monte a CIFRA MUSICAL TRADICIONAL perfeita e limpa no Estilo Cancioneiro.
- Coloque cada acorde na linha imediatamente SUPERIOR, exatamente acima da sílaba/palavra onde ocorre a mudança temporal.
- Concepção Harmônica Limpa (Songbook Oficial): Ao harmonizar os dados do MIR com a letra, priorize a harmonia modal/diatônica limpa da composição (ex: em Tom Jobim ou MPB, valorize progressões como G#m7 | G#4(add9), Am7 | D7(9), 6/9). LIMPE ruídos, micro-inversões transitórias ou acordes excessivamente rebuscados do detector automático (ex: se o MIR gerou Em7(b5)/A# ou G#m9/B por causa de notas passageiras do baixo sobre um vamp G#m7 | G#4(add9), simplifique para a notação consagradamente limpa do Cancioneiro).
- Respeite fielmente as palavras do Whisper. Se perceber repetições ou grooves modais constantes, estruture com elegância sem poluição visual.
- Indique [Intro], [Primeira Parte], [Refrão], [Solo], [Final].
- Retorne EXCLUSIVAMENTE o texto da cifra musical dentro da tag <cifra>...</cifra>.
"""

    try:
        print(f"✨ [Alinhador Híbrido] Solicitando diagramação elegante ao {modelo}...")
        resp = client.models.generate_content(
            model=modelo,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.1, top_p=0.8)
        )
        texto = resp.text
        if "<cifra>" in texto and "</cifra>" in texto:
            return texto.split("<cifra>")[1].split("</cifra>")[0].strip()
        return texto.strip()
    except Exception as e_gem:
        print(f"⚠️ Erro ao diagramar com Gemini ({e_gem}). Usando alinhamento determinístico em Python como fallback...")
        return alinhar_deterministico(acordes, versos)

def formatar_cifra_final(acordes, versos, titulo=None, artista=None, hibrido=False, client=None, modelo="gemini-3-flash-preview"):
    """
    Ponto de entrada do módulo. Seleciona entre alinhamento determinístico e híbrido.
    """
    if hibrido and client:
        return alinhar_hibrido_com_gemini(acordes, versos, titulo, artista, client, modelo)
    return alinhar_deterministico(acordes, versos)
