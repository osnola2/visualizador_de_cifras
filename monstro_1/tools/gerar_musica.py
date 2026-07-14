import urllib.request
import re
import sys
import json
import os
import unicodedata
import shutil

BASE_DIR = r"C:\Users\User\Desktop\Python\Musica\monstro_1"
TEMPLATE_DIR = os.path.join(BASE_DIR, "_TemplateApp")
HUB_HTML = os.path.join(BASE_DIR, "index.html")

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def generate_folder_name(title):
    # Remove accents, keep alphanumeric, TitleCase
    clean = remove_accents(title)
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', clean)
    clean = "".join(word.capitalize() for word in clean.split())
    return f"{clean}App"

from chord_parser import parse_chord as guess_chord_notes
import html as html_lib

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
        clean_p = re.sub(r'<[^>]+>', '', p_html)
        clean_p = clean_p.replace('\xa0', ' ').replace('&nbsp;', ' ')
        line = clean_p.rstrip()
        
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
                clean_ch = ch.strip('(),.')
                if clean_ch:
                    unique_chords.add(clean_ch)
                    return f'<span class="chord" data-chord="{clean_ch}">{clean_ch}</span>'
                return ch
            formatted = re.sub(r'\S+', replace_chord_token, line)
            new_lines.append(formatted)
        else:
            escaped = html_lib.escape(line)
            new_lines.append(f'<span class="lyric-line">{escaped}</span>')

    while new_lines and new_lines[-1] == "":
        new_lines.pop()

    lyrics_content = '\n'.join(new_lines)

    return song_title, song_artist, song_composer, lyrics_content, unique_chords

def fetch_and_parse(url):
    print(f"Fetching {url} ...")
    if "sambacifras.com.br" in url:
        result = parse_sambacifras(url)
        if not result:
            print("Failed to extract tab from Samba Cifras.")
            return
        song_title, song_artist, song_composer, lyrics_content, unique_chords = result
        html = None
    else:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        try:
            response = urllib.request.urlopen(req)
            html = response.read().decode('utf-8')
        except Exception as e:
            print(f"Error fetching URL: {e}")
            return

    if html is not None:
        # Extract Song Title and Artist
        title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE)
        artist_match = re.search(r'<h2[^>]*>.*?<a[^>]*>(.*?)</a>.*?</h2>', html, re.IGNORECASE)
        
        song_title = title_match.group(1).strip() if title_match else "Unknown Title"
        song_artist = artist_match.group(1).strip() if artist_match else "Unknown Artist"
        
        # Extract Lyrics and Chords block
        pre_match = re.search(r'<pre>(.*?)</pre>', html, re.DOTALL | re.IGNORECASE)
        if not pre_match:
            print("Could not find <pre> tag. Page format might be different.")
            return
            
        pre_content = pre_match.group(1)
        
        # Strip <span class="cnt">...</span> which contains tab ASCII art
        pre_content = re.sub(r'<span class="cnt">.*?</span>', '', pre_content, flags=re.DOTALL)
        
        # Strip <span class="tablatura"> and </span> tags
        pre_content = re.sub(r'<span class="tablatura">', '', pre_content)
        pre_content = re.sub(r'</span>', '', pre_content)
        
        unique_chords = set()
        def chord_replacer(match):
            chord_name = match.group(1).strip()
            chord_name = re.sub(r'<[^>]+>', '', chord_name)
            unique_chords.add(chord_name)
            return f'<span class="chord" data-chord="{chord_name}">{chord_name}</span>'

        formatted_content = re.sub(r'<b>(.*?)</b>', chord_replacer, pre_content)
        
        # Wrap lyric lines
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
    
    # Generate chordData JS
    chord_data_js = "const chordData = {\n"
    for idx, chord in enumerate(sorted(unique_chords)):
        notes, display, types = guess_chord_notes(chord)
        notes_str = json.dumps(notes)
        display_str = json.dumps(display)
        types_str = json.dumps(types)
        
        chord_data_js += f'    "{chord}": {{\n'
        chord_data_js += f'        name: "{chord}",\n'
        chord_data_js += f'        notes: {notes_str},\n'
        chord_data_js += f'        displayNotes: {display_str},\n'
        chord_data_js += f'        noteTypes: {types_str}\n'
        chord_data_js += '    }'
        if idx < len(unique_chords) - 1:
            chord_data_js += ','
        chord_data_js += '\n'
    chord_data_js += "};\n"

    # Create new app folder
    folder_name = generate_folder_name(song_title)
    output_dir = os.path.join(BASE_DIR, folder_name)
    
    if os.path.exists(output_dir):
        print(f"Warning: Directory {output_dir} already exists. Overwriting files.")
    else:
        os.makedirs(output_dir)
        
    # Copy template files
    for item in os.listdir(TEMPLATE_DIR):
        src = os.path.join(TEMPLATE_DIR, item)
        dst = os.path.join(output_dir, item)
        if os.path.isfile(src):
            shutil.copy2(src, dst)
            
    # Inject into index.html
    index_path = os.path.join(output_dir, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()
        
    html_content = html_content.replace('{{SONG_TITLE}}', song_title)
    html_content = html_content.replace('{{SONG_ARTIST}}', song_artist)
    html_content = html_content.replace('{{LYRICS_CONTENT}}', lyrics_content)
    
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    # Inject into script.js
    script_path = os.path.join(output_dir, "script.js")
    with open(script_path, "r", encoding="utf-8") as f:
        js_content = f.read()
        
    js_content = js_content.replace('// {{CHORD_DATA_INJECTION}}', chord_data_js)
    
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(js_content)
        
    # Add to Hub index.html
    update_hub(song_title, song_artist, folder_name)
    
    print(f"\n Scaffold complete for '{song_title}' by {song_artist}!")
    print(f" Folder created: {output_dir}")
    print(f" Found {len(unique_chords)} unique chords. Chord mapping was automatically guessed where possible.")
    print(f" Don't forget to review the notes in {folder_name}/script.js")


def update_hub(title, artist, folder_name):
    if not os.path.exists(HUB_HTML):
        print("Hub index.html not found.")
        return
        
    with open(HUB_HTML, "r", encoding="utf-8") as f:
        hub_content = f.read()
        
    if folder_name in hub_content:
        print("Song already exists in Hub.")
        return
        
    card_html = f'''
            <a href="{folder_name}/index.html" class="song-link">
                {title}
                <span class="song-artist">{artist}</span>
            </a>'''
            
    # Insert before the end of the song-list
    if '        </div>\n    </div>\n</body>' in hub_content:
        hub_content = hub_content.replace('        </div>\n    </div>\n</body>', card_html + '\n        </div>\n    </div>\n</body>')
    else:
        # Fallback if exactly matching spaces fails
        hub_content = hub_content.replace('</div>\n    </div>\n</body>', card_html + '\n        </div>\n    </div>\n</body>')
    
    with open(HUB_HTML, "w", encoding="utf-8") as f:
        f.write(hub_content)
    print(" Added new song to Hub (index.html)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gerar_musica.py <cifraclub_url>")
        sys.exit(1)
    fetch_and_parse(sys.argv[1])
