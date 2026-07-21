import urllib.request
import re
import sys
import json
import os
import unicodedata
import html as html_lib

BASE_DIR = r"C:\Users\User\Desktop\Python\Musica"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
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
    return tok.strip('(),.[]')

def is_chord_line(line):
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith('[') and stripped.endswith(']'):
        return False
    tokens = stripped.split()
    if not tokens:
        return False
    has_chord = False
    for token in tokens:
        clean_token = clean_chord_token(token)
        if not clean_token:
            continue
        if CHORD_REGEX.match(clean_token):
            has_chord = True
            continue
        if re.match(r'^\d+x?$', clean_token, re.IGNORECASE) or clean_token in ('|', '||', '/', '-', 'bis', 'x', ':', 'e', '+') or re.match(r'^[|/\-:]+$', clean_token):
            continue
        if token.lower().rstrip(':') in ('intro', 'solo', 'final', 'refrão', 'refrao', 'ponte', 'tom', 'riff') or token.lower() in ('[intro]', '[solo]', '[final]', '[refrão]', '[refrao]', '[ponte]', '[riff]'):
            continue
        return False
    return has_chord

def is_tablature_line(line):
    s = line.strip()
    if not s:
        return False
    if re.match(r'^Parte\s+\d+\s+de\s+\d+$', s, re.IGNORECASE):
        return True
    if re.match(r'^\[Tab\s*-.*\]$', s, re.IGNORECASE):
        return True
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
    if re.match(r'^[eEaAdDgGbBxX]{6}\.?$', s):
        return True
    return False

def parse_plaintext_tab(tab_content, song_title, song_artist):
    unique_chords = set()
    tab_content = tab_content.expandtabs(4)

    def replace_chord_token(match):
        ch = match.group(0)
        clean_ch = clean_chord_token(ch)
        if clean_ch and CHORD_REGEX.match(clean_ch):
            unique_chords.add(clean_ch)
            idx = ch.find(clean_ch)
            prefix = html_lib.escape(ch[:idx])
            suffix = html_lib.escape(ch[idx + len(clean_ch):])
            return f'{prefix}<span class="chord" data-chord="{clean_ch}">{clean_ch}</span>{suffix}'
        return html_lib.escape(ch)

    lines = tab_content.split('\n')
    new_lines = []
    song_started = False
    for line in lines:
        line = line.rstrip('\r')
        if is_tablature_line(line):
            continue
        s = line.strip()
        if not song_started:
            if re.match(r'^\[.*\]$', s) or is_chord_line(line):
                song_started = True
            else:
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
    t, a, l, c = parse_plaintext_tab(tab_content, song_title, song_artist)
    return t, a, "", l, c

def parse_sambacifras(url):
    print(f"Parsing Samba Cifras URL: {url} ...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req)
        raw = response.read()
        html = raw.decode('utf-8', errors='replace')
    except Exception as e:
        print(f"Error fetching Samba Cifras URL ({e})")
        return None

    title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE | re.DOTALL)
    song_title = title_match.group(1).strip() if title_match else "Unknown Title"

    song_artist = "Unknown Artist"
    art_m = re.search(r'<article[^>]*class=["\'][^"\']*sambista-([^/"\']+)["\'][^>]*>', html, re.IGNORECASE)
    if art_m:
        slug = art_m.group(1).split()[0]
        song_artist = " ".join(w.capitalize() for w in slug.split("-"))

    song_composer = ""
    m = re.search(r'<div[^>]*class="[^"]*entry-content[^"]*"[^>]*>(.*?)(?:<footer|<div class="entry-|$)', html, re.IGNORECASE | re.DOTALL)
    if not m:
        print("Could not find entry-content container in Samba Cifras page.")
        return None

    content = m.group(1)
    p_matches = re.findall(r'<p[^>]*>(.*?)</p>', content, re.IGNORECASE | re.DOTALL)

    unique_chords = set()
    new_lines = []

    for p_html in p_matches:
        p_html = re.sub(r'<br\s*/?>', '\n', p_html, flags=re.IGNORECASE)
        clean_p = re.sub(r'<[^>]+>', '', p_html)
        clean_p = html_lib.unescape(clean_p)
        clean_p = clean_p.replace('\xa0', ' ').replace('&nbsp;', ' ')
        
        for line in clean_p.split('\n'):
            line = line.rstrip()
            if not line.strip():
                if new_lines and new_lines[-1] != "":
                    new_lines.append("")
                continue
            
            if line.strip().startswith('(') and line.strip().endswith(')') and len(new_lines) == 0:
                if not song_composer:
                    song_composer = line.strip().strip('()')
                continue
                
            if is_chord_line(line):
                def replace_chord_token(match):
                    ch = match.group(0)
                    clean_ch = clean_chord_token(ch)
                    if clean_ch and CHORD_REGEX.match(clean_ch):
                        unique_chords.add(clean_ch)
                        idx = ch.find(clean_ch)
                        prefix = html_lib.escape(ch[:idx])
                        suffix = html_lib.escape(ch[idx + len(clean_ch):])
                        return f'{prefix}<span class="chord" data-chord="{clean_ch}">{clean_ch}</span>{suffix}'
                    return html_lib.escape(ch)
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

    return song_title, song_artist, song_composer, lyrics_content, chord_data

def parse_bananacifras(url):
    print(f"Parsing Banana Cifras URL via Jina HTML proxy: {url} ...")
    url_clean = url.replace("https://", "http://")
    jina_url = "https://r.jina.ai/" + url_clean
    req = urllib.request.Request(jina_url, headers={'User-Agent': 'Mozilla/5.0', 'X-Return-Format': 'html'})
    try:
        response = urllib.request.urlopen(req)
        raw = response.read()
        html = raw.decode('utf-8', errors='replace')
    except Exception as e:
        print(f"Error fetching Jina URL ({e})")
        return None

    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
    song_title = "Unknown Title"
    song_artist = "Unknown Artist"
    if title_match:
        t_clean = title_match.group(1)
        m = re.search(r'^(.*?)\s+CHORDS\s+(?:by\s+)?(.*?)(\s+-\s+.*)?$', t_clean, re.IGNORECASE)
        if m:
            song_title = m.group(1).strip()
            song_artist = m.group(2).strip()
            song_artist = re.sub(r'\s*-\s*Banana.*$', '', song_artist, flags=re.IGNORECASE).strip()
        else:
            song_title = t_clean.split('CHORDS')[0].strip()

    pre_match = re.search(r'<pre id="song-pre"[^>]*>(.*?)</pre>', html, re.IGNORECASE | re.DOTALL)
    if not pre_match or not pre_match.group(1).strip():
        print("Could not find populated <pre id=\"song-pre\"> inside Banana Cifras HTML, fetching rendered Jina Markdown...")
        return parse_bananacifras_markdown(url, song_title, song_artist)

    pre_content = pre_match.group(1)
    unique_chords = set()

    lines = pre_content.split('\n')
    new_lines = []

    for line in lines:
        line = line.rstrip('\r\n')
        plain = re.sub(r'<[^>]+>', '', line).strip()
        if not plain:
            if new_lines and new_lines[-1] != "":
                new_lines.append("")
            continue

        if is_tablature_line(plain) or re.search(r'^[eBGDAEbebgda]?\s*\|[-0-9~/hb\s]{4,}', plain) or '---|' in plain or '|---' in plain:
            continue

        if '<i>' in line or '</i>' in line:
            line_clean = re.sub(r'</?[ub]>', '', line)
            
            def replace_i_chord(match):
                ch = match.group(1).strip()
                clean_ch = clean_chord_token(ch)
                if clean_ch and CHORD_REGEX.match(clean_ch):
                    unique_chords.add(clean_ch)
                    return f'<span class="chord" data-chord="{clean_ch}">{clean_ch}</span>'
                return html_lib.escape(ch)

            formatted = re.sub(r'<i>(.*?)</i>', replace_i_chord, line_clean, flags=re.IGNORECASE)
            new_lines.append(formatted)
        else:
            line_clean = re.sub(r'<[^>]+>', '', line)
            line_clean = html_lib.unescape(line_clean)
            escaped = html_lib.escape(line_clean)
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

    return song_title, song_artist, "", lyrics_content, chord_data


def parse_bananacifras_markdown(url, default_title="Unknown Title", default_artist="Unknown Artist"):
    print(f"Parsing Banana Cifras rendered markdown via Jina: {url} ...")
    url_clean = url.replace("https://", "http://")
    jina_url = "https://r.jina.ai/" + url_clean
    req = urllib.request.Request(jina_url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req)
        text = response.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"Error fetching Jina Markdown ({e})")
        return None

    song_title = default_title
    song_artist = default_artist

    title_match = re.search(r'Title:\s*(.*?)\s*(?:\n|$)', text, re.IGNORECASE)
    if title_match:
        full_title = title_match.group(1).strip()
        m = re.search(r'^(.*?)\s+CHORDS\s+(?:by\s+)?(.*?)(\s+-\s+.*)?$', full_title, re.IGNORECASE)
        if m:
            song_title = m.group(1).strip()
            song_artist = m.group(2).strip()
            song_artist = re.sub(r'\s*-\s*Banana.*$', '', song_artist, flags=re.IGNORECASE).strip()
        else:
            song_title = full_title.split('CHORDS')[0].strip()

    # Split into segments by double space, newline, or right before a new chord block that follows text
    segments = re.split(r'\s{2,}|\n+|(?<=[a-zA-Zãõçáéíóúâêô.,!?"\'\)\d])\s+(?="_[A-Z])', text)
    new_lines = []
    unique_chords = set()

    song_started = False
    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue
        if seg.startswith("Title:") or seg == "Markdown Content:" or seg.strip() == song_title.strip():
            continue
        if "http://" in seg or "https://" in seg or "bananacifras.com" in seg or seg.startswith("[") or "]" in seg or "Capo No" in seg or "Transpose" in seg or "Font size" in seg or "Split into" in seg or "Show tabs" in seg or "Keep screen" in seg or "Left-Handed" in seg or "Zoom-" in seg or "Color" in seg or "Background" in seg:
            continue
        if seg in ["Show all", "Related tracks"] or seg.startswith("Related tracks") or seg == "Guitar" or seg == "O sol [Guitar]":
            break
        if re.match(r'^[A-G][b#]?\d*\+?(/[\d/]+)?$', seg): # Skip chord diagrams/tables at bottom
            break

        chords = re.findall(r'_([A-Z][a-zA-Z0-9/#+-\.]*)_', seg)
        lyric = re.sub(r'_[A-Z][a-zA-Z0-9/#+-\.]*_', '', seg).strip()

        if chords or lyric:
            song_started = True
            if chords:
                chord_spans = []
                for ch in chords:
                    clean_ch = clean_chord_token(ch)
                    if clean_ch and CHORD_REGEX.match(clean_ch):
                        unique_chords.add(clean_ch)
                        chord_spans.append(f'<span class="chord" data-chord="{clean_ch}">{clean_ch}</span>')
                    else:
                        chord_spans.append(html_lib.escape(ch))
                new_lines.append(" ".join(chord_spans))
            if lyric:
                new_lines.append(f'<span class="lyric-line">{html_lib.escape(lyric)}</span>')

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

    return song_title, song_artist, "", lyrics_content, chord_data



def fetch_and_parse(url):
    if os.path.exists(url):
        print(f"Processing local file: {url} ...")
        with open(url, "r", encoding="utf-8") as f:
            text = f.read()
        
        lines = [l.strip() for l in text.split('\n') if l.strip()]
        song_title = lines[0] if lines else os.path.splitext(os.path.basename(url))[0]
        song_artist = "Unknown Artist"
        song_composer = ""
        
        file_name = generate_file_name(song_title)
        existing_json = os.path.join(DATA_DIR, f"{file_name}.json")
        if os.path.exists(existing_json):
            try:
                with open(existing_json, "r", encoding="utf-8") as ef:
                    ej = json.load(ef)
                    song_title = ej.get("title", song_title)
                    song_artist = ej.get("artist", song_artist)
                    song_composer = ej.get("composer", song_composer)
            except Exception:
                pass
                
        if song_artist == "Unknown Artist" and "Estrada do Sol" in song_title:
            song_artist = "Tom Jobim"
            song_composer = "Tom Jobim / Dolores Duran"
            
        t, a, l, c = parse_plaintext_tab(text, song_title, song_artist)
        song_title, song_artist, lyrics_content, chord_data = t, a, l, c
        
        json_path = os.path.join(DATA_DIR, f"{file_name}.json")
        js_path = os.path.join(DATA_DIR, f"{file_name}.js")
        
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
            
        song_json = {
            "title": song_title,
            "artist": song_artist,
            "composer": song_composer,
            "lyricsHtml": "\n" + lyrics_content + "\n",
            "chordData": chord_data
        }
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(song_json, f, ensure_ascii=False, indent=4)
            
        with open(js_path, "w", encoding="utf-8") as f:
            f.write("window.SONG_DATA = " + json.dumps(song_json, ensure_ascii=False, indent=4) + ";\n")
            
        update_hub(song_title, song_artist, file_name, song_composer)
        
        print(f"\n Successfully processed '{song_title}' by {song_artist} from local file!")
        print(f" Saved data to: {json_path} and {js_path}")
        return

    print(f"Fetching {url} ...")
    
    # If Ultimate Guitar or non-CifraClub site where direct fetch often blocks 403, support fallback
    if "ultimate-guitar.com" in url:
        result = fetch_jina_markdown(url)
        if not result:
            print("Failed to extract tab from Ultimate Guitar.")
            return
        song_title, song_artist, song_composer, lyrics_content, chord_data = result
        html = None
    elif "bananacifras.com" in url:
        result = parse_bananacifras(url)
        if not result:
            print("Failed to extract tab from Banana Cifras.")
            return
        song_title, song_artist, song_composer, lyrics_content, chord_data = result
        html = None
    elif "sambacifras.com.br" in url:
        result = parse_sambacifras(url)
        if not result:
            print("Failed to extract tab from Samba Cifras.")
            return
        song_title, song_artist, song_composer, lyrics_content, chord_data = result
        html = None
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
            song_title, song_artist, song_composer, lyrics_content, chord_data = result
            html = None

        if html is not None:
            title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE)
            artist_match = re.search(r'<h2[^>]*>.*?<a[^>]*>(.*?)</a>.*?</h2>', html, re.IGNORECASE)
            
            song_title = html_lib.unescape(title_match.group(1).strip()) if title_match else "Unknown Title"
            song_artist = html_lib.unescape(artist_match.group(1).strip()) if artist_match else "Unknown Artist"
            
            composer_match = re.search(r'<p class="cifra-composer">.*?de\s*(.*?)(?:\.|<a)', html, re.IGNORECASE)
            song_composer = html_lib.unescape(composer_match.group(1).strip()) if composer_match else ""
            
            pre_match = re.search(r'<pre>(.*?)</pre>', html, re.DOTALL | re.IGNORECASE)
            if not pre_match:
                print("Could not find <pre> tag. Page format might be different.")
                return
                
            pre_content = pre_match.group(1)
            pre_content = re.sub(r'<span class="cnt">.*?</span>', '', pre_content, flags=re.DOTALL)
            pre_content = re.sub(r'<span class="tablatura">', '', pre_content)
            pre_content = re.sub(r'</span>', '', pre_content)
            # Remove guitar position annotations like "(na 5ª casa)" that confuse chord detection
            pre_content = re.sub(r'\s*\(na\s+\d+[ªº]?\s*casa\)', '', pre_content, flags=re.IGNORECASE)
            
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
                    # Check if this is a chord line that wasn't wrapped in <b> tags
                    plain = re.sub(r'<[^>]+>', '', line)
                    if is_chord_line(plain):
                        def bare_chord_replacer(match):
                            ch = match.group(0)
                            clean_ch = clean_chord_token(ch)
                            if clean_ch and CHORD_REGEX.match(clean_ch):
                                unique_chords.add(clean_ch)
                                idx = ch.find(clean_ch)
                                prefix = html_lib.escape(ch[:idx])
                                suffix = html_lib.escape(ch[idx + len(clean_ch):])
                                return f'{prefix}<span class="chord" data-chord="{clean_ch}">{clean_ch}</span>{suffix}'
                            return html_lib.escape(ch)
                        formatted = re.sub(r'\S+', bare_chord_replacer, line)
                        new_lines.append(formatted)
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
        "composer": song_composer,
        "lyricsHtml": "\n" + lyrics_content + "\n",
        "chordData": chord_data
    }
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(song_json, f, ensure_ascii=False, indent=4)
        
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("window.SONG_DATA = " + json.dumps(song_json, ensure_ascii=False, indent=4) + ";\n")
        
    update_hub(song_title, song_artist, file_name, song_composer)
    
    print(f"\n Successfully processed '{song_title}' by {song_artist}!")
    print(f" Saved data to: {json_path} and {js_path}")

def update_hub(title, artist, file_name, composer=""):
    if not os.path.exists(HUB_HTML):
        return
        
    with open(HUB_HTML, "r", encoding="utf-8") as f:
        hub_content = f.read()
        
    card_pattern = re.compile(r'<a\s+href="viewer\.html\?song=([^"]+)"\s+class="song-link">\s*(.*?)\s*<span\s+class="song-artist">(.*?)</span>\s*</a>', re.DOTALL)
    
    songs = []
    seen = set()
    catalog_path = os.path.join(BASE_DIR, "data", "catalog.json")
    if os.path.exists(catalog_path):
        try:
            with open(catalog_path, "r", encoding="utf-8") as cf:
                for s in json.load(cf):
                    if s.get("id") not in seen:
                        seen.add(s["id"])
                        songs.append((s["id"], s.get("title", s["id"]), s.get("artist", "")))
        except Exception:
            pass
    for match in card_pattern.finditer(hub_content):
        f_name = match.group(1).strip()
        s_title = match.group(2).strip()
        s_artist = match.group(3).strip()
        s_artist = re.sub(r'<[^>]+>', '', s_artist).strip()
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
        json_file = os.path.join(DATA_DIR, f"{f_name}.json")
        s_composer = ""
        if os.path.exists(json_file):
            try:
                with open(json_file, "r", encoding="utf-8") as jf:
                    jdata = json.load(jf)
                    s_artist = jdata.get("artist", s_artist)
                    s_composer = jdata.get("composer", "")
            except Exception:
                pass
        
        display_artist = s_artist
        if s_composer and s_composer != s_artist:
            display_artist = f'{s_artist} <span style="font-size: 0.85em; opacity: 0.85; font-weight: 400;">(Comp: {s_composer})</span>'
            
        cards_html.append(f'''            <a href="viewer.html?song={f_name}" class="song-link">
                {s_title}
                <span class="song-artist">{display_artist}</span>
            </a>''')
            
    cards_block = "\n    \n".join(cards_html)
    
    # Replace contents of <div class="song-list"...>...</div>
    new_hub = re.sub(r'(<div class="song-list"[^>]*>)(.*?)(</div>\s*</body>)', r'\1\n        <!-- Songs will be injected here -->\n' + cards_block + r'\n    \3', hub_content, flags=re.DOTALL)
    
    with open(HUB_HTML, "w", encoding="utf-8") as f:
        f.write(new_hub)
    print(" Updated Hub (index.html) in alphabetical order")
    try:
        from tools.generate_catalog import generate_catalog
        generate_catalog()
    except Exception as e:
        print(f" Warning: Failed to generate catalog: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gerar_musica.py <tab_url>")
        sys.exit(1)
    fetch_and_parse(sys.argv[1])
