import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
if sys.platform == 'win32' and hasattr(os, 'add_dll_directory'):
    _pyroot = os.path.dirname(sys.executable)
    _sp = os.path.join(_pyroot, 'Lib', 'site-packages')
    for _sub in [_pyroot, os.path.join(_sp, 'sklearn', '.libs'), os.path.join(_sp, 'ctranslate2'), os.path.join(_sp, 'scipy', '.libs'), os.path.join(_sp, 'z3', 'lib')]:
        if os.path.exists(_sub):
            try:
                os.add_dll_directory(_sub)
            except Exception:
                pass
import time
import argparse
from pathlib import Path

# Adiciona a pasta raiz e tools ao path para podermos usar os geradores do catálogo
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "tools"))

try:
    from google import genai
    from google.genai import types
except ImportError:
    print("❌ Erro: Biblioteca 'google-genai' não instalada. Execute: pip install google-genai")
    sys.exit(1)

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

from tools.gerar_musica import parse_plaintext_tab, update_hub, remove_accents, generate_file_name
from tools.generate_catalog import generate_catalog

try:
    from audio_to_cifra.mir_chord_detector import detectar_acordes_com_timestamps
    from audio_to_cifra.asr_lyrics_transcriber import transcrever_letra_com_timestamps
    from audio_to_cifra.pipeline_alinhador import formatar_cifra_final
except ImportError as e_imp:
    print(f"⚠️ Aviso ao importar módulos locais Opção 1: {e_imp}")

def gerar_prompt_cifra(titulo, artista):
    contexto = f'Música: "{titulo}"\nArtista/Compositor: "{artista}"' if titulo and artista else ''
    return f"""
Você é um arranjador e transcritor profissional de música brasileira (estilo Almir Chediak / Songbooks MPB/Samba / Cancioneiro Tom Jobim).
{contexto}

Ouça o áudio com extrema precisão do início ao fim e realize a transcrição em 2 ETAPAS OBRIGATÓRIAS:

ETAPA 1 (Escreva dentro da tag <analise_cot>):
- Verificação Poética e Fonética: Revise a letra ouvida no contexto poético e literário da MPB/Samba brasileiro (por exemplo, se for Gilberto Gil ou Mariene de Castro, garanta que termos sofisticados e poéticos não sejam distorcidos para palavras alucinadas, anacronismos ou marcas modernas como "Uber").
- Mapeamento e Concepção Harmônica (Estilo Cancioneiro / Songbook Oficial): Identifique a tonalidade e a estrutura harmônica essencial da composição. PRIORIZE a elegância, clareza e fidelidade à concepção original do compositor (ex: em Tom Jobim ou MPB, valorize progressões modais/quartais limpas como G#m7 | G#4(add9), Am7 | D7(9), 6/9, 7M). EVITE poluir a cifra com micro-inversões de baixo transitórias ou nomenclaturas excessivamente rebuscadas (ex: evite transformar um vamp ou groove limpo em Em7(b5)/A# ou G#m9/B apenas por causa do movimento passageiro do contrabaixo).
- Estratégia Songbook (Anti-Poluição e Anti-Loop): Se houver um groove modal contínuo (ex: G7M(9) | C7M(9)) com refrão repetido no final da estrofe ("Quem avisa anjo é"), não entulhe o mesmo par de acordes mecanicamente linha por linha a cada repetição vocal idêntica. Organize a cifra de forma limpa, elegante e prática como nos Songbooks oficiais.

ETAPA 2 (Escreva dentro da tag <cifra>):
Escreva a cifra final tradicional pronta para tocar.
- Os acordes DEVEM estar posicionados na linha imediatamente SUPERIOR ao verso da letra, alinhados exatamente em cima da sílaba onde acontece a mudança no áudio.
- Indique claramente as partes com [Intro], [Primeira Parte], [Refrão], [Ponte], [Solo], [Final].
- Dentro da tag <cifra>, retorne APENAS o texto da cifra musical pura, sem comentários adicionais.
"""


def testar_chave_e_modelos(api_key):
    print("🔍 [MODO DIAGNÓSTICO] Testando sua chave de API e descobrindo modelos ativos...")
    client = genai.Client(api_key=api_key)
    
    try:
        modelos_disponiveis = []
        for m in client.models.list():
            nome_limpo = m.name.replace('models/', '')
            if 'gemini' in nome_limpo.lower() and 'vision' not in nome_limpo.lower():
                modelos_disponiveis.append(nome_limpo)
        print(f"📋 Modelos encontrados na conta: {modelos_disponiveis[:10]}")
    except Exception as e:
        print(f"❌ Erro ao listar modelos: {e}")
        modelos_disponiveis = ['gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro']

    print("\n🧠 Enviando um teste rápido de texto ('Oi') para encontrar qual modelo está 100% livre na sua chave...")
    modelos_funcionando = []
    for modelo in sorted(modelos_disponiveis, key=lambda x: (0 if '2.0-flash' in x else 1 if '1.5-flash' in x else 2)):
        try:
            print(f"  ⏳ Testando {modelo} ... ", end="", flush=True)
            res = client.models.generate_content(
                model=modelo,
                contents=["Oi, responda apenas 'OK' se estiver funcionando."]
            )
            print(f"✅ FUNCIONOU! (Resposta: {res.text.strip()})")
            modelos_funcionando.append(modelo)
            if len(modelos_funcionando) >= 2:
                break
        except Exception as e_test:
            msg = str(e_test)
            if "429" in msg or "EXHAUSTED" in msg or "limit: 0" in msg:
                print("⚠️  Sem cota gratuita ativa (Limit: 0 / 429)")
            elif "404" in msg:
                print("⚠️  Não encontrado (404)")
            else:
                print(f"⚠️  Falhou ({msg[:60]}...)")
            continue

    if modelos_funcionando:
        print(f"\n🎉 Diagnóstico concluído! O modelo ideal para você usar é: {modelos_funcionando[0]}")
    else:
        print("\n❌ Nenhum modelo respondeu no teste rápido. Verifique se a cota gratuita (Free Tier) está habilitada na sua região ou no Google AI Studio.")
    return True

def baixar_audio_youtube(url, pasta_destino):
    if not yt_dlp:
        print("❌ Erro: Biblioteca 'yt-dlp' não instalada. Execute: pip install yt-dlp")
        return None, None, None

    print(f"📥 Baixando áudio do YouTube (priorizando formato M4A/AAC que a IA decodifica perfeitamente): {url} ...")
    pasta_destino.mkdir(exist_ok=True, parents=True)
    
    # Priorizar formato m4a (140) ou aac, pois arquivos webm brutos sem ffmpeg às vezes causam estado FAILED no Gemini
    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio[ext=aac]/bestaudio/best',
        'outtmpl': str(pasta_destino / '%(title)s.%(ext)s'),
        'quiet': False,
        'no_warnings': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            titulo_yt = info_dict.get('title', 'Musica YouTube')
            artista_yt = info_dict.get('uploader', info_dict.get('channel', 'Artista Desconhecido'))
            
            # Sanitizar para ASCII puro para evitar falhas no cabeçalho HTTP de upload (ascii codec can't encode)
            file_path = Path(filename)
            safe_name = remove_accents(file_path.name)
            if safe_name != file_path.name and file_path.exists():
                safe_path = file_path.with_name(safe_name)
                file_path.rename(safe_path)
                filename = str(safe_path)
                
            return filename, titulo_yt, artista_yt
    except Exception as e:
        print(f"❌ Erro ao baixar do YouTube: {e}")
        return None, None, None

def processar_audio(caminho_ou_url, titulo_musica=None, artista_musica=None, test_key=False):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("\n⚠️  ATENÇÃO: Variável de ambiente 'GEMINI_API_KEY' não encontrada.")
        print("Para que a IA possa transcrever o áudio, defina sua chave de API no terminal antes de rodar:")
        print("  [PowerShell]: $env:GEMINI_API_KEY=\"sua_chave_aqui\"")
        print("  [CMD]:        set GEMINI_API_KEY=sua_chave_aqui")
        return False

    if test_key:
        return testar_chave_e_modelos(api_key)

    caminho_audio = caminho_ou_url
    titulo_final = titulo_musica
    artista_final = artista_musica

    # Se for um link do YouTube ou web, baixa o áudio primeiro
    if caminho_ou_url.startswith("http://") or caminho_ou_url.startswith("https://") or "youtube.com" in caminho_ou_url or "youtu.be" in caminho_ou_url:
        pasta_audios = BASE_DIR / "audio_to_cifra" / "audios"
        arquivo_baixado, tit_yt, art_yt = baixar_audio_youtube(caminho_ou_url, pasta_audios)
        if not arquivo_baixado:
            return False
        caminho_audio = arquivo_baixado
        if not titulo_final:
            titulo_final = tit_yt
        if not artista_final:
            artista_final = art_yt

    if not os.path.exists(caminho_audio):
        print(f"❌ Erro: Arquivo de áudio não encontrado -> {caminho_audio}")
        return False

    # Sanitizar qualquer arquivo local com acento (ex: Sabiá.m4a -> Sabia.m4a) antes de enviar por HTTP para a API
    caminho_audio_path = Path(caminho_audio)
    nome_seguro_ascii = remove_accents(caminho_audio_path.name)
    if nome_seguro_ascii != caminho_audio_path.name or not all(ord(c) < 128 for c in caminho_audio_path.name):
        novo_caminho = caminho_audio_path.with_name(nome_seguro_ascii)
        try:
            if caminho_audio_path.exists() and not novo_caminho.exists():
                caminho_audio_path.rename(novo_caminho)
            caminho_audio = str(novo_caminho)
            print(f"📁 Nome de arquivo ajustado para ASCII seguro: {caminho_audio}")
        except Exception as e_rename:
            print(f"⚠️ Aviso ao renomear arquivo para ASCII: {e_rename}")

    print(f"🚀 Conectando ao Google GenAI e enviando áudio: {caminho_audio} ...")
    client = genai.Client(api_key=api_key)

    try:
        audio_file = client.files.upload(file=caminho_audio)
        print(f"✅ Áudio enviado para a nuvem (ID: {audio_file.name}). Aguardando processamento e ativação...")

        # Aguardar o arquivo ficar ACTIVE no servidor do Google
        while getattr(audio_file, 'state', None) and getattr(audio_file.state, 'name', '') == "PROCESSING":
            print("⏳ Aguardando decodificação do áudio nos servidores do Gemini...")
            time.sleep(5)
            audio_file = client.files.get(name=audio_file.name)

        if getattr(audio_file, 'state', None) and getattr(audio_file.state, 'name', '') == "FAILED":
            print("❌ Erro: O servidor do Google falhou ao processar o formato deste arquivo de áudio.")
            print("💡 Dica: O arquivo .webm atual pode estar corrompido para o Gemini. Exclua a pasta 'audio_to_cifra/audios' e rode novamente para que ele baixe no formato M4A compatível.")
            return False

        if getattr(audio_file, 'state', None) and getattr(audio_file.state, 'name', '') != "ACTIVE":
            print(f"⚠️  Aviso: Estado do arquivo é {getattr(audio_file.state, 'name', 'Desconhecido')}. Tentando prosseguir...")

        # Lista limpa de modelos prioritários e com cota grátis verificada no diagnóstico
        modelos_para_tentar = ['gemini-3-flash-preview', 'gemini-flash-lite-latest', 'gemini-2.0-flash']
        print(f"📋 Modelos que serão tentados: {modelos_para_tentar}")

        # Gerar o prompt especialista contextualizado e com CoT (2 Etapas)
        prompt_especialista = gerar_prompt_cifra(titulo_final, artista_final)

        response = None
        for modelo in modelos_para_tentar:
            tentativas = 0
            while tentativas < 2:
                try:
                    print(f"🧠 Tentando modelo: {modelo} (Tentativa {tentativas+1}) ...")
                    response = client.models.generate_content(
                        model=modelo,
                        contents=[audio_file, prompt_especialista],
                        config=types.GenerateContentConfig(
                            temperature=0.1, # Baixíssima temperatura para evitar alucinação e repetição em loop
                            top_p=0.8,
                        )
                    )
                    break
                except Exception as e_mod:
                    msg_erro = str(e_mod)
                    print(f"⚠️  Modelo {modelo} falhou: {msg_erro[:150]}...")
                    if '429' in msg_erro or 'EXHAUSTED' in msg_erro or 'Quota' in msg_erro or 'retry in' in msg_erro:
                        print("⏳ Limite de requisições temporário (429/Quota). Aguardando 20 segundos antes de tentar novamente...")
                        time.sleep(20)
                        tentativas += 1
                        continue
                    break
            if response:
                print(f"✨ Transcrição gerada com sucesso pelo modelo: {modelo}")
                break

        if not response:
            print("❌ Erro: Todos os modelos tentados falharam. Rode 'python audio_to_cifra/extrair_cifra.py --test-key' para diagnosticar quais modelos estão liberados na sua chave.")
            return False

        texto_bruto = response.text

        # Extrair etapa 1 (análise CoT) e etapa 2 (cifra limpa)
        analise_cot = ""
        cifra_texto = texto_bruto
        if "<analise_cot>" in texto_bruto and "</analise_cot>" in texto_bruto:
            analise_cot = texto_bruto.split("<analise_cot>")[1].split("</analise_cot>")[0].strip()
            print("\n🧐 ANÁLISE POÉTICA E HARMÔNICA DA IA (Chain of Thought - Etapa 1):")
            print("------------------------------------------------------------------")
            print(analise_cot)
            print("------------------------------------------------------------------\n")

        if "<cifra>" in texto_bruto and "</cifra>" in texto_bruto:
            cifra_texto = texto_bruto.split("<cifra>")[1].split("</cifra>")[0].strip()
        elif "</analise_cot>" in texto_bruto:
            cifra_texto = texto_bruto.split("</analise_cot>")[1].strip()
            if cifra_texto.startswith("<cifra>"):
                cifra_texto = cifra_texto[7:].strip()
            if cifra_texto.endswith("</cifra>"):
                cifra_texto = cifra_texto[:-8].strip()

        print("\n================ CIFRA FINAL GERADA (Etapa 2) ================")
        print(f"Modelo utilizado: {modelo}")
        print(cifra_texto)
        print("============================================================\n")

        nome_base = Path(caminho_audio).stem
        if not titulo_final:
            titulo_final = nome_base.replace("_", " ").title()
        if not artista_final:
            artista_final = "Artista Desconhecido"

        pasta_transcricoes = BASE_DIR / "audio_to_cifra" / "transcricoes"
        pasta_transcricoes.mkdir(exist_ok=True, parents=True)
        caminho_txt = pasta_transcricoes / f"{nome_base}.txt"

        with open(caminho_txt, "w", encoding="utf-8") as f:
            f.write(cifra_texto)
        print(f"💾 Cifra em texto salva em: {caminho_txt}")

        if salvar_catalogo:
            print("⚙️  Convertendo para o formato do Visualizador e atualizando catálogo...")
            file_name_clean = generate_file_name(titulo_final)
            
            parse_plaintext_tab(cifra_texto, titulo_final, artista_final)
            update_hub(titulo_final, artista_final, file_name_clean, composer="")
            generate_catalog()
            print(f"\n🎉 Sucesso! A cifra de '{titulo_final}' foi adicionada ao seu catálogo visualizador!")
        else:
            print(f"\n🛑 Modo rascunho: A cifra está salva em .txt ({caminho_txt}), mas NÃO foi enviada ao catálogo (index.html intacto). Use --salvar-catalogo quando estiver satisfeito.")
        return True

    except Exception as e:
        print(f"❌ Erro durante a comunicação com a API do Gemini: {e}")
        return False

def processar_audio_op1(caminho_ou_url, titulo_musica=None, artista_musica=None, hibrido=False, test_key=False, salvar_catalogo=False):
    """
    Executa o Pipeline Algorítmico (Opção 1):
    1. MIR (Librosa Chromagram CQT) para acordes.
    2. ASR (Faster-Whisper) para letra com timestamps.
    3. Alinhamento Temporal Determinístico ou Híbrido (Gemini).
    """
    if test_key:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("\n⚠️  ATENÇÃO: Variável de ambiente 'GEMINI_API_KEY' não encontrada para teste.")
            return False
        return testar_chave_e_modelos(api_key)

    caminho_audio = caminho_ou_url
    titulo_final = titulo_musica
    artista_final = artista_musica

    # Se for link do YouTube, baixa primeiro
    if caminho_ou_url.startswith("http://") or caminho_ou_url.startswith("https://") or "youtube.com" in caminho_ou_url or "youtu.be" in caminho_ou_url:
        pasta_audios = BASE_DIR / "audio_to_cifra" / "audios"
        arquivo_baixado, tit_yt, art_yt = baixar_audio_youtube(caminho_ou_url, pasta_audios)
        if not arquivo_baixado:
            return False
        caminho_audio = arquivo_baixado
        if not titulo_final:
            titulo_final = tit_yt
        if not artista_final:
            artista_final = art_yt

    if not os.path.exists(caminho_audio):
        print(f"❌ Erro: Arquivo de áudio não encontrado -> {caminho_audio}")
        return False

    nome_base = Path(caminho_audio).stem
    if not titulo_final:
        titulo_final = nome_base.replace("_", " ").title()
    if not artista_final:
        artista_final = "Artista Desconhecido"

    print(f"\n========================================================")
    print(f"🎸 EXECUTANDO OPÇÃO 1: Pipeline Algorítmico (MIR + ASR)")
    print(f"Música: {titulo_final} | Artista: {artista_final}")
    print(f"========================================================\n")

    # 1. MIR: Detecção Harmônica
    acordes_detectados = detectar_acordes_com_timestamps(caminho_audio)
    
    # 2. ASR: Transcrição e Timestamps por palavra
    versos_transcritos = transcrever_letra_com_timestamps(caminho_audio)
    
    # Salvar dados temporais brutos em JSON para permitir que a IA da sessão atue diretamente no acabamento híbrido
    import json
    pasta_transcricoes = BASE_DIR / "audio_to_cifra" / "transcricoes"
    pasta_transcricoes.mkdir(exist_ok=True, parents=True)
    caminho_dados_json = pasta_transcricoes / f"{nome_base}_dados_temporais.json"
    try:
        with open(caminho_dados_json, "w", encoding="utf-8") as f_json:
            json.dump({
                "titulo": titulo_final,
                "artista": artista_final,
                "acordes": acordes_detectados,
                "versos": versos_transcritos
            }, f_json, ensure_ascii=False, indent=2)
        print(f"📦 Dados temporais brutos (MIR + ASR) salvos para revisão híbrida em: {caminho_dados_json}")
    except Exception as e_json:
        print(f"⚠️ Aviso ao salvar JSON temporal: {e_json}")

    # 3. Alinhamento e Formatação
    client = None
    if hibrido:
        api_key = os.environ.get("GEMINI_API_KEY")
        if api_key:
            client = genai.Client(api_key=api_key)
        else:
            print("⚠️ Chave GEMINI_API_KEY não definida. Realizando alinhamento determinístico Python...")
            hibrido = False

    cifra_texto = formatar_cifra_final(
        acordes=acordes_detectados,
        versos=versos_transcritos,
        titulo=titulo_final,
        artista=artista_final,
        hibrido=hibrido,
        client=client
    )

    print("\n================ CIFRA GERADA PELA OPÇÃO 1 ================")
    print(cifra_texto)
    print("===========================================================\n")

    pasta_transcricoes = BASE_DIR / "audio_to_cifra" / "transcricoes"
    pasta_transcricoes.mkdir(exist_ok=True, parents=True)
    caminho_txt = pasta_transcricoes / f"{nome_base}.txt"

    with open(caminho_txt, "w", encoding="utf-8") as f:
        f.write(cifra_texto)
    print(f"💾 Cifra em texto salva em: {caminho_txt}")

    if salvar_catalogo:
        print("⚙️  Convertendo para o formato do Visualizador e atualizando catálogo...")
        file_name_clean = generate_file_name(titulo_final)
        
        parse_plaintext_tab(cifra_texto, titulo_final, artista_final)
        update_hub(titulo_final, artista_final, file_name_clean, composer="")
        generate_catalog()
        print(f"\n🎉 Sucesso! A cifra de '{titulo_final}' gerada pela Opção 1 foi adicionada ao seu catálogo!")
    else:
        print(f"\n🛑 Modo rascunho: A cifra está salva em .txt ({caminho_txt}), mas NÃO foi enviada ao catálogo (index.html intacto). Use --salvar-catalogo quando estiver satisfeito.")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrai cifra musical a partir de um arquivo de áudio ou link do YouTube (Opção 1 - MIR + Whisper por padrão).")
    parser.add_argument("audio", nargs="?", help="Caminho para o arquivo MP3/WAV/M4A ou LINK DO YOUTUBE.")
    parser.add_argument("--titulo", "-t", help="Título da música.")
    parser.add_argument("--artista", "-a", help="Nome do artista.")
    parser.add_argument("--hibrido", action="store_true", help="Usa o Gemini para o acabamento/diagramação final da cifra a partir dos timestamps da Opção 1.")
    parser.add_argument("--op2", "--gemini", action="store_true", help="Executa o fluxo antigo da Opção 2 (LLM Multimodal direto no áudio).")
    parser.add_argument("--test-key", action="store_true", help="Executa um teste de diagnóstico na sua chave de API do Gemini.")
    parser.add_argument("--salvar-catalogo", action="store_true", help="Atualiza o visualizador web (index.html e catalog.js/json) com a cifra extraída.")

    args = parser.parse_args()
    if args.test_key:
        processar_audio("", test_key=True)
    elif args.audio:
        if args.op2:
            processar_audio(args.audio, args.titulo, args.artista, salvar_catalogo=args.salvar_catalogo)
        else:
            processar_audio_op1(args.audio, args.titulo, args.artista, hibrido=args.hibrido, salvar_catalogo=args.salvar_catalogo)
    else:
        parser.print_help()
