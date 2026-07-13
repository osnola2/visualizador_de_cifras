import os

code = '''import urllib.request
import re
import sys
import json
import os
import unicodedata

BASE_DIR = r"C:\Users\User\Desktop\Python\Musica"
DATA_DIR = os.path.join(BASE_DIR, "data", "songs")
HUB_HTML = os.path.join(BASE_DIR, "public", "index.html")

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

def generate_file_name(title):
    clean = remove_accents(title)
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', clean)
    clean = "".join(word.capitalize() for word in clean.split())
    return clean

from chord_parser import parse_chord as guess_chord_notes

def fetch_and_parse(url):
    print(f"Fetching {url} ...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        response = urllib.request.urlopen(req)
        html = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return

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
    
    lines = formatted_content.split('\\n')
    new_lines = []
    for line in lines:
        if line.strip() == "":
            new_lines.append(line)
        elif '<span class="chord"' in line:
            new_lines.append(line)
        else:
            new_lines.append(f'<span class="lyric-line">{line}</span>')
    lyrics_content = '\\n'.join(new_lines)
    
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
    
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    song_json = {
        "title": song_title,
        "artist": song_artist,
        "lyricsHtml": "\\n" + lyrics_content + "\\n",
        "chordData": chord_data
    }
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(song_json, f, ensure_ascii=False, indent=4)
        
    update_hub(song_title, song_artist, file_name)
    
    print(f"\\n Successfully processed '{song_title}' by {song_artist}!")
    print(f" Saved data to: {json_path}")

def update_hub(title, artist, file_name):
    if not os.path.exists(HUB_HTML):
        return
        
    with open(HUB_HTML, "r", encoding="utf-8") as f:
        hub_content = f.read()
        
    if f'viewer.html?song={file_name}' in hub_content:
        return
        
    card_html = f\'\'\'
            <a href="viewer.html?song={file_name}" class="song-link">
                {title}
                <span class="song-artist">{artist}</span>
            </a>\'\'\'
            
    if '        </div>\\n    </div>\\n</body>' in hub_content:
        hub_content = hub_content.replace('        </div>\\n    </div>\\n</body>', card_html + '\\n        </div>\\n    </div>\\n</body>')
    else:
        hub_content = hub_content.replace('</div>\\n</body>', card_html + '\\n    </div>\\n</body>')
    
    with open(HUB_HTML, "w", encoding="utf-8") as f:
        f.write(hub_content)
    print(" Added new song to Hub (public/index.html)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gerar_musica.py <cifraclub_url>")
        sys.exit(1)
    fetch_and_parse(sys.argv[1])
'''

with open(r'C:\Users\User\Desktop\Python\Musica\tools\gerar_musica.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("gerar_musica.py rewritten.")
