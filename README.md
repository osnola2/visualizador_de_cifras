# 🎵 Visualizador de Cifras & Acervo Harmônico

[![pt-br](https://img.shields.io/badge/Language-Portugu%C3%AAs-green.svg)](README.md) [![en](https://img.shields.io/badge/Language-English-blue.svg)](README_en.md)
*Leia em / Read in:* 🇧🇷 **Português** | 🇺🇸 [English](README_en.md)

Um ecossistema interativo e automatizado para visualização, análise harmônica, transposição instantânea e catalogação de cifras musicais para **Violão**, **Cavaquinho** e **Piano/Teclado**.

---

## ✨ Funcionalidades Principais

- **Hub Interativo (`index.html`):** Catálogo unificado com busca em tempo real por título, artista ou compositor, filtros rápidos por nível de dificuldade e agrupamentos dinâmicos (A-Z, por artista ou quantidade de acordes).
- **Transposição Instantânea:** Mudança de tom de qualquer música com recalculo automático dos intervalos e digitações em tempo real.
- **Visualizadores Multi-Instrumento:**
  - **Violão (`viewer.html` / `viewer-violao.html`):** Diagramas harmônicos e transposição.
  - **Cavaquinho (`viewer-cavaquinho.html`):** Digitações e diagramas específicos para cavaquinho em afinação padrão (D-G-B-D).
  - **Piano / Teclado (`viewer-piano.html`):** Teclado virtual que destaca visualmente as notas que compõem cada acorde na transposição ativa.
- **Scroll por Demanda (Sincronização MIDI):** Integração com a API Web MIDI. Ao conectar um teclado controlador, o visualizador acompanha o seu ritmo, avançando a letra e destacando o próximo acorde apenas quando você toca a harmonia exata no instrumento.
- **Análise Harmônica (`chord_parser.py`):** Motor de cálculo capaz de decompor acordes complexos, identificar tônicas, qualidades e extensões de notas.
- **Pipeline Automatizado CLI (`tools/gerar_musica.py`):** Importação direta via terminal a partir de portais como Cifra Club e Ultimate Guitar, convertendo o HTML/Markdown em arquivos estruturados (`.json` / `.js`) e regerando o índice automaticamente.

---

## 📂 Estrutura do Projeto

```text
visualizador_de_cifras/
├── index.html                  # Catálogo / Hub principal interativo
├── viewer.html                 # Transpositor e visualizador de Violão
├── viewer-cavaquinho.html      # Visualizador dedicado para Cavaquinho
├── viewer-piano.html           # Visualizador dedicado para Piano/Teclado
├── assets/
│   ├── css/style.css           # Estilos globais da aplicação (Dark Mode/UI)
│   └── js/                     # Scripts de renderização e controle dos visualizadores
├── data/
│   ├── catalog.js / .json      # Catálogo centralizado (188+ músicas cadastradas)
│   └── songs/                  # Base estruturada das músicas em .json e .js
├── tools/
│   ├── gerar_musica.py         # CLI para importação de URLs de cifras
│   ├── generate_catalog.py     # Gerador do índice alfabético unificado
│   └── chord_parser.py         # Motor de análise e decomposição de acordes
└── audio_to_cifra/             # Módulo experimental de transcrição acústica de áudio
```

---

## 🚀 Pipeline de Importação de Músicas (`tools/gerar_musica.py`)

Para incluir uma ou mais músicas no catálogo a partir de uma URL (ex: Cifra Club ou Ultimate Guitar), basta executar o comando abaixo no terminal a partir da raiz do projeto:

```powershell
python tools/gerar_musica.py "https://www.cifraclub.com.br/artista/nome-da-musica/#tabs=false"
```

### O que o script faz automaticamente:
1. **Download & Limpeza:** Baixa o conteúdo da página, extrai a letra e remove anotações irrelevantes.
2. **Identificação de Acordes:** Envolve cada acorde detectado em tags interativas `<span class="chord" data-chord="...">`.
3. **Harmonia & Estrutura:** Decompõe cada acorde através do analisador harmônico `chord_parser.py`, registrando intervalos e notas.
4. **Geração de Arquivos:** Cria `data/songs/NomeDaMusica.json` e `.js` com todos os metadados prontos para o front-end.
5. **Atualização do Catálogo:** Executa o `generate_catalog.py`, reorganizando `data/catalog.js` em ordem alfabética e mantendo o `index.html` e os filtros sincronizados.

Para regerar manualmente o índice unificado (caso arquivos em `data/songs/` tenham sido editados à mão):
```powershell
python tools/generate_catalog.py
```

---

## 💻 Como Rodar o Projeto Localmente

Como o projeto é construído em HTML5, CSS3 Vanilla e JavaScript puro, não é necessário compilar o front-end. 

1. **Abra diretamente:** Você pode abrir o arquivo `index.html` em qualquer navegador web.
2. **Servidor Local (Recomendado):** Para evitar restrições de CORS ao testar certas interações, suba um servidor web simples na pasta raiz do projeto:
   ```powershell
   python -m http.server 8000
   ```
   E acesse `http://localhost:8000` em seu navegador.

---

## 🎸 Acervo Atual

Atualmente, o repositório conta com **188 cifras** estruturadas de grandes artistas da MPB, Samba, Rock e Blues (como Cartola, Ismael Silva, David Bowie, Tom Jobim, Luiz Tatit, Adoniran Barbosa, Muddy Waters, entre outros).

---
*Projeto mantido para estudo, análise harmônica e prática instrumental.*
