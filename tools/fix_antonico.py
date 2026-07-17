import sys
import os
import json

# Add tools to path for chord_parser
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
from chord_parser import parse_chord as guess_chord_notes

song_data = {
    "title": "Antonico",
    "artist": "Ismael Silva",
    "composer": "Ismael Silva",
    # Cifra reconstruída manualmente a partir do texto + acordes originais
    # Fonte: CifraClub / domínio público
    "lyricsHtml": r"""
<span class="chord" data-chord="Am">Am</span>                                                  <span class="chord" data-chord="Dm">Dm</span>
<span class="lyric-line">Ôh Antonico, vou lhe pedir um favor</span>
<span class="chord" data-chord="Bm7/5-">Bm7/5-</span>          <span class="chord" data-chord="E7">E7</span>          <span class="chord" data-chord="Am">Am</span>     <span class="chord" data-chord="E7">E7</span>
<span class="lyric-line">Que só depende da sua boa vontade</span>
<span class="chord" data-chord="Am">Am</span>                      <span class="chord" data-chord="F#m7/5-">F#m7/5-</span>    <span class="chord" data-chord="Em">Em</span>
<span class="lyric-line">É necessário uma viração pro Nestor</span>
<span class="chord" data-chord="F#">F#</span>                                    <span class="chord" data-chord="F7">F7</span> <span class="chord" data-chord="E7">E7</span>
<span class="lyric-line">Que está vivendo em grande dificuldade</span>
<span class="chord" data-chord="Am">Am</span>                                           <span class="chord" data-chord="Dm">Dm</span>
<span class="lyric-line">Ele está mesmo dançando na corda bamba</span>
<span class="chord" data-chord="Bm7/5-">Bm7/5-</span>           <span class="chord" data-chord="E7">E7</span>        <span class="chord" data-chord="Em7/5-">Em7/5-</span> <span class="chord" data-chord="A7">A7</span>
<span class="lyric-line">Ele é aquele que na escola de samba</span>
<span class="chord" data-chord="Dm">Dm</span>                                     <span class="chord" data-chord="Am">Am</span>
<span class="lyric-line">Toca cuíca, toca surdo e tamborim</span>
<span class="chord" data-chord="Bm7/5-">Bm7/5-</span>          <span class="chord" data-chord="E7">E7</span>             <span class="chord" data-chord="Am">Am</span>
<span class="lyric-line">Faça por ele como se fosse por mim</span>

<span class="chord" data-chord="Am">Am</span>                                    <span class="chord" data-chord="Dm">Dm</span>
<span class="lyric-line">Até muamba já fizeram pro rapaz</span>
<span class="chord" data-chord="E7">E7</span>                                                <span class="chord" data-chord="Am">Am</span>   <span class="chord" data-chord="E7">E7</span>
<span class="lyric-line">Porque no samba ninguém faz o que ele faz</span>
<span class="chord" data-chord="Am">Am</span>                <span class="chord" data-chord="F#7/5-">F#7/5-</span>                   <span class="chord" data-chord="Em">Em</span>
<span class="lyric-line">Mas hei de vê-lo muito bem, se Deus quiser</span>
<span class="chord" data-chord="B7">B7</span>                                 <span class="chord" data-chord="E7">E7</span>
<span class="lyric-line">E agradeço pelo que você fizer</span>
"""
}

# Parse all chords from lyricsHtml
import re
chord_names = list(dict.fromkeys(re.findall(r'data-chord="([^"]+)"', song_data["lyricsHtml"])))
chord_data = {}
for chord in chord_names:
    result = guess_chord_notes(chord)
    if result:
        chord_data[chord] = result

song_data["chordData"] = chord_data

# Write JSON
out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'songs', 'Antonico.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(song_data, f, indent=4, ensure_ascii=False)

print(f"Written {out_path}")
print(f"Chords: {list(chord_data.keys())}")
