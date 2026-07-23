# Em Busca da Cifra Perfeita 🎼✨

Este diretório é o laboratório e santuário harmônico do nosso projeto. Aqui nos dedicamos à pesquisa, curadoria, revisão teórica e diagramação de **Cifras de Alta Fidelidade (Songbook Grade)** para a música brasileira.

## 🎯 Filosofia e Missão

Diferente de catálogos gerados por *scraping* automatizado na web ou transcrições rasas que simplificam ou poluem as progressões, **"Em Busca da Cifra Perfeita"** adota os seguintes mandamentos:

1. **Rigor Teórico e Songbook-Grade:**
   - Respeito absoluto às tonalidades originais e à concepção harmônica dos compositores (como nos songbooks canônicos de Almir Chediak e nas partituras de referência).
   - Nomenclatura limpa, precisa e padronizada (ex: distinguir com clareza acordes com 9ª, 13ª menor, 6/9, diminutos reais `º` vs meio-diminutos `ø`, e inversões de baixo significativas).

2. **Alinhamento Silábico Milimétrico:**
   - O acorde é posicionado na linha exatamente acima da sílaba/tempo rítmico onde ocorre a mudança harmônica na melodia.

3. **Pronta para o Nosso Ecossistema Interativo:**
   - As cifras criadas e revisadas aqui em formato de texto limpo (`.txt`) são processadas pelo nosso gerador automático (`tools/gerar_musica.py`), convertendo-se em dados estruturados (`data/songs/*.js`) para alimentar:
     - 🎸 **Violão Visualizer:** Desenho exato dos shapes e pestanas.
     - 🪕 **Cavaquinho Visualizer:** Formatos tradicionais das rodas de samba e choro.
     - 🎹 **Teclado / Piano Visualizer:** Voice leading e aberturas harmônicas.
     - 🔊 **ChordSynth:** Áudio real sintetizado com dedilhado humanizado e timbres imersivos.

---

## 📁 Estrutura de Curadoria

Coloque nesta pasta os arquivos de texto rascunhados ou curados (`NomeDoArtista_NomeDaMusica.txt`).  
Para compilar uma cifra perfeita para o catálogo principal, basta executar no terminal:

```powershell
python tools/gerar_musica.py "em_busca_da_cifra_perfeita/NomeDoArtista_NomeDaMusica.txt"
```
