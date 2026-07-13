import urllib.request
import re
import sys
import json
import os
import unicodedata
import html as html_lib

BASE_DIR = r"C:\Users\User\Desktop\Python\Musica"
DATA_DIR = os.path.join(BASE_DIR, "data", "songs")
HUB_HTML = os.path.join(BASE_DIR, "index.html")

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def generate_file_name(title):
    clean = remove_accents(title)
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', clean)
    clean = "".join(word.capitalize() for word in clean.split())
    return clean

from chord_parser import parse_chord as guess_chord_notes

CHORD_REGEX = re.compile(r'^[A-G][b#]?(?:m|maj|min|dim|aug|sus|add|M|\d|\+|-)*(?:/[A-G][b#]?)?$')

def is_chord_line(line):
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith('[') and stripped.endswith(']'):
        return False
    tokens = stripped.split()
    if not tokens:
        return False
    for token in tokens:
        clean_token = token.strip('(),.')
        if not CHORD_REGEX.match(clean_token):
            return False
    return True

def is_tablature_line(line):
    s = line.strip()
    if not s:
        return False
    if re.match(r'^[a-gA-GX]?\s*\|[-xX0-9]', s):
        return True
    if '|-' in s and '-|' in s:
        return True
    if '---' in s or '|--' in s or '--|' in s:
        return True
    if s.startswith('***') or s == 'X':
        return True
    if re.match(r'^\|\s*[hpb/\\~v]\s+[A-Za-z]', s):
        return True
    return False

def parse_plaintext_tab(tab_content, song_title, song_artist):
    unique_chords = set()

    def replace_chord_token(match):
        ch = match.group(0)
        clean_ch = ch.strip('(),.')
        unique_chords.add(clean_ch)
        return f'<span class="chord" data-chord="{clean_ch}">{clean_ch}</span>'

    lines = tab_content.split('\n')
    new_lines = []
    for line in lines:
        line = line.rstrip('\r')
        if is_tablature_line(line):
            continue
        if line.strip() == "":
            if not new_lines or new_lines[-1] != "":
                new_lines.append("")
        elif is_chord_line(line):
            formatted = re.sub(r'\S+', replace_chord_token, line)
            new_lines.append(formatted)
        else:
            escaped = html_lib.escape(line)
            new_lines.append(f'<span class="lyric-line">{escaped}</span>')

    while new_lines and new_lines[-1] == "":
        new_lines.pop()

    lyrics_content = '\n'.join(new_lines)

    chord_data = {}
    for chord in sorted(unique_chords):
        notes, display, types = guess_chord_notes(chord)
        chord_data[chord] = {
            "name": chord,
            "notes": notes,
            "displayNotes": display,
            "noteTypes": types
        }

    return song_title, song_artist, lyrics_content, chord_data

def fetch_jina_markdown(url):
    proxy_url = "https://r.jina.ai/" + url
    req = urllib.request.Request(proxy_url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    text = response.read().decode('utf-8')

    song_title = "Unknown Title"
    song_artist = "Unknown Artist"

    title_match = re.search(r'Title:\s*(.*?)\s*(?:\n|$)', text, re.IGNORECASE)
    if title_match:
        full_title = title_match.group(1).strip()
        if "-" in full_title:
            parts = full_title.split("-", 1)
            song_artist = parts[0].strip()
            t = parts[1].strip()
            t = re.sub(r'\s*\((Chords|Tab|Tabs)\).*', '', t, flags=re.IGNORECASE).strip()
            t = re.sub(r'\s*\[(Chords|Tab|Tabs)\].*', '', t, flags=re.IGNORECASE).strip()
            song_title = t
        else:
            song_title = full_title

    code_match = re.search(r'```(?:[a-zA-Z]*\n)?(.*?)```', text, re.DOTALL)
    if not code_match:
        print("Could not find code block in markdown.")
        return None

    tab_content = code_match.group(1)
    return parse_plaintext_tab(tab_content, song_title, song_artist)

def fetch_and_parse(url):
    print(f"Fetching {url} ...")
    
    # If Ultimate Guitar or non-CifraClub site where direct fetch often blocks 403, support fallback
    if "ultimate-guitar.com" in url:
        result = fetch_jina_markdown(url)
        if not result:
            print("Failed to extract tab from Ultimate Guitar.")
            return
        song_title, song_artist, lyrics_content, chord_data = result
    else:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            response = urllib.request.urlopen(req)
            html = response.read().decode('utf-8')
        except Exception as e:
            print(f"Error direct fetching URL ({e}), trying Jina AI proxy...")
            result = fetch_jina_markdown(url)
            if not result:
                return
            song_title, song_artist, lyrics_content, chord_data = result
            html = None

        if html is not None:
            title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE)
            artist_match = re.search(r'<h2[^>]*>.*?<a[^>]*>(.*?)</a>.*?</h2>', html, re.IGNORECASE)
            
            song_title = title_match.group(1).strip() if title_match else "Unknown Title"
            song_artist = artist_match.group(1).strip() if artist_match else "Unknown Artist"
            
            pre_match = re.search(r'<pre>(.*?)</pre>', html, re.DOTALL | re.IGNORECASE)
            if not pre_match:
                print("Could not find <pre> tag. Page format might be different.")
                return
                
            pre_content = pre_match.group(1)
            pre_content = re.sub(r'<span class="cnt">.*?</span>', '', pre_content, flags=re.DOTALL)
            pre_content = re.sub(r'<span class="tablatura">', '', pre_content)
            pre_content = re.sub(r'</span>', '', pre_content)
            
            unique_chords = set()
            def chord_replacer(match):
                chord_name = match.group(1).strip()
                chord_name = re.sub(r'<[^>]+>', '', chord_name)
                unique_chords.add(chord_name)
                return f'<span class="chord" data-chord="{chord_name}">{chord_name}</span>'

            formatted_content = re.sub(r'<b>(.*?)</b>', chord_replacer, pre_content)
            
            lines = formatted_content.split('\n')
            new_lines = []
            for line in lines:
                if line.strip() == "":
                    new_lines.append(line)
                elif '<span class="chord"' in line:
                    new_lines.append(line)
                else:
                    new_lines.append(f'<span class="lyric-line">{line}</span>')
            lyrics_content = '\n'.join(new_lines)
            
            chord_data = {}
            for chord in sorted(unique_chords):
                notes, display, types = guess_chord_notes(chord)
                chord_data[chord] = {
                    "name": chord,
                    "notes": notes,
                    "displayNotes": display,
                    "noteTypes": types
                }

    file_name = generate_file_name(song_title)
    json_path = os.path.join(DATA_DIR, f"{file_name}.json")
    js_path = os.path.join(DATA_DIR, f"{file_name}.js")
    
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    song_json = {
        "title": song_title,
        "artist": song_artist,
        "lyricsHtml": "\n" + lyrics_content + "\n",
        "chordData": chord_data
    }
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(song_json, f, ensure_ascii=False, indent=4)
        
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("window.SONG_DATA = " + json.dumps(song_json, ensure_ascii=False, indent=4) + ";\n")
        
    update_hub(song_title, song_artist, file_name)
    
    print(f"\n Successfully processed '{song_title}' by {song_artist}!")
    print(f" Saved data to: {json_path} and {js_path}")

def update_hub(title, artist, file_name):
    if not os.path.exists(HUB_HTML):
        return
        
    with open(HUB_HTML, "r", encoding="utf-8") as f:
        hub_content = f.read()
        
    card_pattern = re.compile(r'<a\s+href="viewer\.html\?song=([^"]+)"\s+class="song-link">\s*(.*?)\s*<span\s+class="song-artist">(.*?)</span>\s*</a>', re.DOTALL)
    
    songs = []
    seen = set()
    for match in card_pattern.finditer(hub_content):
        f_name = match.group(1).strip()
        s_title = match.group(2).strip()
        s_artist = match.group(3).strip()
        if f_name not in seen:
            seen.add(f_name)
            songs.append((f_name, s_title, s_artist))
            
    if file_name not in seen:
        songs.append((file_name, title, artist))
    else:
        # Update title/artist if already present
        songs = [(f, t, a) if f != file_name else (file_name, title, artist) for (f, t, a) in songs]
        
    songs.sort(key=lambda item: remove_accents(item[1]).lower())
    
    cards_html = []
    for f_name, s_title, s_artist in songs:
        cards_html.append(f'''            <a href="viewer.html?song={f_name}" class="song-link">
                {s_title}
                <span class="song-artist">{s_artist}</span>
            </a>''')
            
    cards_block = "\n    \n".join(cards_html)
    
    # Replace contents of <div class="song-list"...>...</div>
    new_hub = re.sub(r'(<div class="song-list"[^>]*>)(.*?)(</div>\s*</body>)', r'\1\n        <!-- Songs will be injected here -->\n' + cards_block + r'\n    \3', hub_content, flags=re.DOTALL)
    
    with open(HUB_HTML, "w", encoding="utf-8") as f:
        f.write(new_hub)
    print(" Updated Hub (index.html) in alphabetical order")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gerar_musica.py <tab_url>")
        sys.exit(1)
    fetch_and_parse(sys.argv[1])
