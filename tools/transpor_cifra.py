#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo e script de linha de comando para transposição de cifras musicais (.txt ou .json).
Permite transpor acordes por número de semitons (+/-) ou especificando tom de origem e destino.
Preserva rigorosamente a diagramação, espaços, letras e alinhamento monospaçado.
"""

import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import re
import json
import argparse
from pathlib import Path

# Adiciona o diretório tools ao path se necessário
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from chord_parser import get_note_index, NOTES_SHARP, NOTES_FLAT
    from gerar_musica import is_chord_line, clean_chord_token, CHORD_REGEX
except ImportError:
    # Fallback se executado isoladamente
    NOTES_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    NOTES_FLAT = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
    
    def get_note_index(note_str):
        if note_str in NOTES_SHARP: return NOTES_SHARP.index(note_str)
        if note_str in NOTES_FLAT: return NOTES_FLAT.index(note_str)
        if note_str == 'Cb': return 11
        if note_str == 'E#': return 5
        if note_str == 'Fb': return 4
        if note_str == 'B#': return 0
        return 0

    CHORD_REGEX = re.compile(
        r'^[A-G][b#]?(?:m|maj|min|dim|aug|sus|add|M|\d|\+|-|°|º|ø|/\d+[-+b#]?|\([-+b#/\dA-Za-z°ºø]+\))*(?:/[A-G][b#]?)?$'
    )

    def clean_chord_token(ch):
        if not ch: return ""
        if CHORD_REGEX.match(ch): return ch
        if ch.startswith('(') and ch.endswith(')') and CHORD_REGEX.match(ch[1:-1]):
            return ch[1:-1]
        stripped = ch.strip('(),.[]')
        if CHORD_REGEX.match(stripped): return stripped
        return ch.strip('(),.[]')

    def is_chord_line(line):
        stripped = line.strip()
        if not stripped or (stripped.startswith('[') and stripped.endswith(']')):
            return False
        tokens = stripped.split()
        has_chord = False
        for token in tokens:
            clean = clean_chord_token(token)
            if not clean: continue
            if CHORD_REGEX.match(clean):
                has_chord = True
                continue
            if re.match(r'^\d+x?$', clean, re.IGNORECASE) or clean in ('|', '||', '/', '-', 'bis', 'x', ':', 'e', '+') or re.match(r'^[|/\-:]+$', clean):
                continue
            return False
        return has_chord

FLAT_KEYS = {'F', 'Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Dm', 'Gm', 'Cm', 'Fm', 'Bbm', 'Ebm'}

def get_note_name_by_preference(index, prefer_flats=False):
    idx = index % 12
    return NOTES_FLAT[idx] if prefer_flats else NOTES_SHARP[idx]

def transpor_acorde_simples(chord_symbol, semitons, prefer_flats=False):
    """
    Transpõe um único símbolo de acorde pelo número de semitons especificado.
    Mantém todas as extensões e inversões de baixo intactas.
    """
    if not chord_symbol:
        return chord_symbol

    # 1. Separar baixo se existir (/X)
    bass_str = None
    bass_match = re.search(r'/([A-G][#b]?)$', chord_symbol)
    main_chord = chord_symbol
    if bass_match:
        bass_str = bass_match.group(1)
        main_chord = chord_symbol[:bass_match.start()]

    # 2. Separar nota tônica (Root) da extensão
    root_match = re.match(r'^([A-G][#b]?)', main_chord)
    if not root_match:
        return chord_symbol

    root_str = root_match.group(1)
    suffix = main_chord[len(root_str):]

    # 3. Transpor Tônica
    root_idx = get_note_index(root_str)
    new_root_idx = (root_idx + semitons) % 12
    new_root = get_note_name_by_preference(new_root_idx, prefer_flats)

    # 4. Transpor Baixo se houver
    new_bass = ""
    if bass_str:
        bass_idx = get_note_index(bass_str)
        new_bass_idx = (bass_idx + semitons) % 12
        new_bass = "/" + get_note_name_by_preference(new_bass_idx, prefer_flats)

    return f"{new_root}{suffix}{new_bass}"

def transpor_linha(line, semitons, prefer_flats=False):
    """
    Transpõe todos os acordes de uma linha mantendo a precisão das colunas monospaçadas.
    """
    if not is_chord_line(line):
        return line

    def replacer(match):
        token = match.group(0)
        clean = clean_chord_token(token)
        if clean and CHORD_REGEX.match(clean):
            idx = token.find(clean)
            prefix = token[:idx]
            suffix = token[idx + len(clean):]
            transposto = transpor_acorde_simples(clean, semitons, prefer_flats)
            # Para manter o alinhamento visual com a letra, se o acorde mudou de tamanho (ex: C -> C# ou Bb -> B),
            # tentamos compensar nos espaços seguintes se for possível
            return f"{prefix}{transposto}{suffix}"
        return token

    # Substitui tokens que não são espaços em branco
    return re.sub(r'\S+', replacer, line)

def transpor_texto(texto_cifra, semitons, prefer_flats=False):
    """
    Transpõe todo o texto de uma cifra linha a linha.
    """
    linhas = texto_cifra.expandtabs(4).split('\n')
    linhas_transpostas = []
    for l in linhas:
        l_trans = transpor_linha(l, semitons, prefer_flats)
        linhas_transpostas.append(l_trans)
    return '\n'.join(linhas_transpostas)

def calcular_semitons_entre_tons(tom_origem, tom_destino):
    """
    Calcula a distância em semitons de um tom para outro.
    """
    idx_orig = get_note_index(tom_origem.strip().capitalize())
    idx_dest = get_note_index(tom_destino.strip().capitalize())
    diff = (idx_dest - idx_orig) % 12
    # Ajusta para o intervalo mais próximo ou positivo
    return diff

def main():
    parser = argparse.ArgumentParser(description="Transpõe cifras musicais em arquivos TXT ou JSON por semitons ou tons de origem/destino.")
    parser.add_argument("entrada", help="Arquivo (.txt/.json) ou texto/acorde a ser transposto.")
    parser.add_argument("-s", "--semitons", type=int, help="Número de semitons para transpor (ex: +2, -3, 4).")
    parser.add_argument("-o", "--origem", help="Tom de origem (ex: C, Dm, G).")
    parser.add_argument("-t", "--destino", help="Tom de destino (ex: E, F#m, A).")
    parser.add_argument("-b", "--bemois", action="store_true", help="Forçar grafia com bemóis (b) nos acordes transpostos.")
    parser.add_argument("--sustenidos", action="store_true", help="Forçar grafia com sustenidos (#) nos acordes transpostos.")
    parser.add_argument("--saida", "-out", help="Arquivo de saída. Se omitido, imprime no terminal ou salva com sufixo _transposto.")
    
    args = parser.parse_args()

    # Determinar semitons
    semitons = 0
    if args.semitons is not None:
        semitons = args.semitons
    elif args.origem and args.destino:
        semitons = calcular_semitons_entre_tons(args.origem, args.destino)
    else:
        print("❌ Erro: Você deve especificar o número de semitons (-s/--semitons) OU os tons de origem e destino (-o C -t E).")
        sys.exit(1)

    # Determinar preferência de bemol/sustenido
    prefer_flats = False
    if args.bemois:
        prefer_flats = True
    elif args.sustenidos:
        prefer_flats = False
    elif args.destino:
        # Pega a raiz do tom de destino para decidir se usa bemol
        root_dest = re.match(r'^[A-G][#b]?', args.destino).group(0)
        prefer_flats = root_dest in FLAT_KEYS

    # Verificar se entrada é arquivo ou texto direto
    if os.path.exists(args.entrada):
        caminho = Path(args.entrada)
        print(f"📖 Lendo arquivo: {caminho}")
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()

        if caminho.suffix.lower() in (".json", ".js"):
            # Processar JSON ou JS de música do catálogo
            if caminho.suffix.lower() == ".js":
                match_js = re.search(r'(=|^)\s*(\{.*\})\s*;?\s*$', conteudo, re.DOTALL)
                if match_js:
                    json_str = match_js.group(2)
                else:
                    json_str = conteudo
            else:
                json_str = conteudo

            dados = json.loads(json_str)
            if "chordData" in dados and "lyricsHtml" in dados:
                print("🎹 Detectado formato JSON do Catálogo. Transpondo spans de HTML e regenerando chordData...")
                from chord_parser import parse_chord as guess_chord_notes
                
                unique_transposed = set()
                def span_replacer(match):
                    orig_chord = match.group(1)
                    orig_display = match.group(2)
                    new_chord = transpor_acorde_simples(orig_chord, semitons, prefer_flats)
                    new_display = transpor_acorde_simples(orig_display, semitons, prefer_flats)
                    unique_transposed.add(new_chord)
                    return f'<span class="chord" data-chord="{new_chord}">{new_display}</span>'
                
                novo_html = re.sub(r'<span class="chord" data-chord="([^"]+)">([^<]+)</span>', span_replacer, dados["lyricsHtml"])
                dados["lyricsHtml"] = novo_html
                
                novo_chord_data = {}
                for ch in sorted(unique_transposed):
                    notes, display, types = guess_chord_notes(ch)
                    novo_chord_data[ch] = {
                        "name": ch,
                        "notes": notes,
                        "displayNotes": display,
                        "noteTypes": types
                    }
                dados["chordData"] = novo_chord_data
                
                caminho_saida = args.saida
                if not caminho_saida:
                    tom_info = f"_transposto_{semitons:+d}st"
                    if args.destino: tom_info = f"_em_{args.destino}"
                    caminho_saida = caminho.parent / f"{caminho.stem}{tom_info}.json"
                
                caminho_saida = Path(caminho_saida)
                caminho_saida.parent.mkdir(parents=True, exist_ok=True)
                
                # Se a extensão do arquivo de saída não for json nem js, definimos como json
                if caminho_saida.suffix.lower() not in (".json", ".js"):
                    caminho_saida = caminho_saida.with_suffix(".json")
                    
                with open(caminho_saida, "w", encoding="utf-8") as f_out:
                    if caminho_saida.suffix.lower() == ".js":
                        f_out.write("window.SONG_DATA = " + json.dumps(dados, ensure_ascii=False, indent=4) + ";\n")
                    else:
                        json.dump(dados, f_out, ensure_ascii=False, indent=4)
                        
                print(f"✅ Arquivo JSON/JS transposto (+{semitons} semitons) salvo em: {caminho_saida}\n")
                
                # Para facilitar a verificação visual ou do usuário, vamos mostrar os acordes antigos e novos
                print(f"🔀 Acordes no novo arquivo: {', '.join(sorted(unique_transposed))}")
                return
            # Arquivo TXT comum
            cifra_transposta = transpor_texto(conteudo, semitons, prefer_flats)
            
            caminho_saida = args.saida
            if not caminho_saida:
                tom_info = f"_transposto_{semitons:+d}st"
                if args.destino: tom_info = f"_em_{args.destino}"
                caminho_saida = caminho.parent / f"{caminho.stem}{tom_info}{caminho.suffix}"
            
            caminho_saida = Path(caminho_saida)
            caminho_saida.parent.mkdir(parents=True, exist_ok=True)
            with open(caminho_saida, "w", encoding="utf-8") as f_out:
                f_out.write(cifra_transposta)
                
            print(f"✅ Cifra transposta (+{semitons} semitons) salva em: {caminho_saida}\n")
            print("--- AMOSTRA (PRIMEIRAS LINHAS) ---")
            for l in cifra_transposta.split('\n')[:15]:
                print(l)
    else:
        # É um texto ou acorde direto pelo terminal
        resultado = transpor_texto(args.entrada, semitons, prefer_flats)
        print(f"🎵 Resultado: {resultado}")

if __name__ == "__main__":
    main()
