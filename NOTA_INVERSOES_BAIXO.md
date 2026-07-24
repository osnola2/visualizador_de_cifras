# Tolerância a Inversões e Baixos no Sincronizador MIDI

## O Problema do Baixo Invertido
Na notação musical, acordes com baixo invertido (ex: `Bm/A`) ocorrem quando uma nota diferente da tônica é tocada na região mais grave (o baixo). No caso de `Bm/A` (Si menor com baixo em Lá), as notas são **Si, Ré, Fá#** e **Lá**.

Para um motor de detecção MIDI matemático (`MidiDetector.js`), essas quatro notas (Lá, Si, Ré, Fá#) formam perfeitamente o acorde de **Si menor com sétima** (cuja 7ª menor é o Lá). Como o Lá é a nota mais grave, o detector interpreta o acorde exatamente como `Bm7/A`.

No entanto, quem transcreve cifras na internet frequentemente simplifica a notação. É muito comum encontrar a notação `Bm/A` em vez do tecnicamente correto `Bm7/A`. Isso criava um impasse no Scroll por Demanda: o usuário tocava as notas exatas da cifra, o detector lia o acorde completo (`Bm7/A`), e ele não dava "match" com o simplificado da tela (`Bm/A`), travando a música.

## A Solução: Simplificação Tolerante no `getEquivalents`
Para resolver isso, injetamos uma camada de "tolerância harmônica" no `script.js`.

Quando um acorde com baixo alterado é tocado no piano, o sistema agora gera variações removendo as extensões (como 7ª, 6ª ou 7ª Maior) da base do acorde. 

Os novos aliases criados foram:
- **`m7/` -> `m/`** (Ex: `Bm7/A` também é lido como `Bm/A`)
- **`m6/` -> `m/`** (Ex: `Am6/F#` também é lido como `Am/F#`)
- **`maj7/` e `7M/` -> `/`** (Ex: `Cmaj7/B` também é lido como `C/B`)
- **`7/` -> `/`** (Ex: `G7/F` também é lido como `G/F`)
- **`6/` -> `/`** (Ex: `C6/A` também é lido como `C/A`)

## Por que essa abordagem funciona tão bem?
1. **É bidirecional:** Como a lógica de aliases no código verifica se o caractere A gera o B e vice-versa, isso cobre tanto o caso em que o detector acha que é `Bm7/A` e a tela diz `Bm/A`, quanto o oposto!
2. **Preserva a estrutura rítmica:** O usuário não é punido por adicionar a 7ª que, harmonicamente, já estava implícita na nota do baixo.
3. **Fluidez:** O Scroll por Demanda continua restrito o suficiente para não pular a música sem querer, mas amigável o bastante para entender "dialetos" e simplificações comuns na notação de cifras.
