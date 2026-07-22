import os
import sys
import json
import re

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from tools.chord_parser import parse_chord as guess_chord_notes
from tools.generate_catalog import generate_catalog

SONG_TITLE = "Hotel Coração Partido"
SONG_ARTIST = "Vitor Wutski"
SONG_COMPOSER = "Vitor Wutski"
FILE_NAME = "HotelCoracaoPartido"

raw_lines = [
    ("chord", "[intro]   D7M   C#m7   F#7"),
    ("chord", "Bm7"),
    ("lyric", "lua azul"),
    ("chord", "            F#m7"),
    ("lyric", "você me deu a montanha"),
    ("chord", "    Em7     A7    D7M"),
    ("lyric", "sapato de camurça azul"),
    ("chord", "        C#m7      F#7   Bm7"),
    ("lyric", "você não passa de um cão de caça"),
    ("chord", "E7(9)"),
    ("lyric", "rio azul"),
    ("chord", "G7M            F#m7"),
    ("lyric", "te seguro no meu coração enquanto"),
    ("chord", "    Em7     A7   A7/C#  D7M   C#m7   F#7"),
    ("lyric", "não posso segurar nos meus braços"),
    ("chord", "        Bm  [entrada do teclado]"),
    ("lyric", "me beije rápido"),
    ("chord", "    F#m     [G] Am - Am6"),
    ("lyric", "me ame com ternura"),
    ("chord", "    G           Em"),
    ("lyric", "coração de madeira"),
    ("chord", "        Bm7     Em7        Bm7"),
    ("lyric", "você perdeu aquela sensação de amor"),
    ("chord", "  Em7   F#m7  Bm7    [1ªvez: C#m   F#7 (recomeça)]"),
    ("lyric", "hotel Coração Partido"),
    ("empty", ""),
    ("chord", "[final:]"),
    ("empty", ""),
    ("chord", "Em7      Bm7    C#m7  F#7"),
    ("lyric", "  amor queimando"),
    ("chord", "         Bm7   Em7"),
    ("lyric", "amor queimando"),
    ("chord", "         Bm7     C#m7  F#7"),
    ("lyric", "amor queimando"),
    ("chord", "         Bm7   Em7"),
    ("lyric", "amor queimando"),
    ("chord", "         Bm7     C#m7  F#7  Bm7"),
    ("lyric", "amor queimando")
]

CHORD_REGEX = re.compile(r'^[A-G][b#]?(?:m|maj|min|dim|aug|sus|add|M|\d|\+|-|°|º|ø|/\d+[-+b#]?|\([-+b#/\dA-Za-z°ºø]+\))*(?:/[A-G][b#]?)?$')

def clean_chord_token(tok):
    if not tok:
        return ""
    if CHORD_REGEX.match(tok):
        return tok
    if tok.startswith('(') and tok.endswith(')') and CHORD_REGEX.match(tok[1:-1]):
        return tok[1:-1]
    stripped = tok.strip('(),.[]')
    if CHORD_REGEX.match(stripped):
        return stripped
    return ""

unique_chords = set()
html_lines = []

for ltype, lcontent in raw_lines:
    if ltype == "empty":
        html_lines.append("")
    elif ltype == "lyric":
        html_lines.append(f'<span class="lyric-line">{lcontent}</span>')
    elif ltype == "chord":
        # Parse tokens
        # We want to replace valid chords with span while keeping spacing and text annotations like [intro]
        tokens = re.split(r'(\s+)', lcontent)
        new_tokens = []
        for tok in tokens:
            if not tok.strip():
                new_tokens.append(tok)
                continue
            clean = clean_chord_token(tok)
            if clean:
                unique_chords.add(clean)
                # Replace exact occurrence
                idx = tok.find(clean)
                pref = tok[:idx]
                suff = tok[idx + len(clean):]
                new_tokens.append(f'{pref}<span class="chord" data-chord="{clean}">{clean}</span>{suff}')
            else:
                new_tokens.append(tok)
        html_lines.append("".join(new_tokens))

lyrics_html = "\n".join(html_lines) + "\n"

print(f"Detected {len(unique_chords)} unique chords: {sorted(list(unique_chords))}")

chord_data = {}
for ch in sorted(list(unique_chords)):
    res = guess_chord_notes(ch)
    if res:
        notes, display, types = res
        chord_data[ch] = {
            "name": ch,
            "notes": notes,
            "displayNotes": display,
            "noteTypes": types
        }
    else:
        print(f"Warning: could not parse chord {ch}")

song_data = {
    "title": SONG_TITLE,
    "artist": SONG_ARTIST,
    "composer": SONG_COMPOSER,
    "lyricsHtml": lyrics_html,
    "chordData": chord_data
}

# Write JSON
json_path = os.path.join(BASE_DIR, "data", "songs", f"{FILE_NAME}.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(song_data, f, indent=4, ensure_ascii=False)
print(f"Saved {json_path}")

# Write JS
js_path = os.path.join(BASE_DIR, "data", "songs", f"{FILE_NAME}.js")
js_content = f"window.SONG_DATA = {json.dumps(song_data, indent=4, ensure_ascii=False)};\n"
with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_content)
print(f"Saved {js_path}")

# Update index.html
hub_path = os.path.join(BASE_DIR, "index.html")
with open(hub_path, "r", encoding="utf-8") as f:
    hub_content = f.read()

# Check all existing songs in data/songs
import unicodedata
def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

songs_dir = os.path.join(BASE_DIR, "data", "songs")
songs = []
for file in os.listdir(songs_dir):
    if file.endswith(".json"):
        f_name = file[:-5]
        j_path = os.path.join(songs_dir, file)
        try:
            with open(j_path, "r", encoding="utf-8") as jf:
                jdata = json.load(jf)
                s_title = jdata.get("title", f_name)
                s_artist = jdata.get("artist", "")
                s_composer = jdata.get("composer", "")
                songs.append((f_name, s_title, s_artist, s_composer))
        except Exception as e:
            pass

songs.sort(key=lambda item: remove_accents(item[1]).lower())

cards_html = []
for f_name, s_title, s_artist, s_composer in songs:
    display_artist = s_artist
    if s_composer and s_composer != s_artist:
        display_artist = f'{s_artist} <span style="font-size: 0.85em; opacity: 0.85; font-weight: 400;">(Comp: {s_composer})</span>'
        
    cards_html.append(f'''            <a href="viewer.html?song={f_name}" class="song-link">
                {s_title}
                <span class="song-artist">{display_artist}</span>
            </a>''')

cards_block = "\n    \n".join(cards_html)
new_hub = re.sub(r'(<div class="song-list"[^>]*>)(.*?)(</div>\s*</body>)', r'\1\n        <!-- Songs will be injected here -->\n' + cards_block + r'\n    \3', hub_content, flags=re.DOTALL)

with open(hub_path, "w", encoding="utf-8") as f:
    f.write(new_hub)
print("Updated index.html")

generate_catalog()
print("Catalog updated successfully!")
