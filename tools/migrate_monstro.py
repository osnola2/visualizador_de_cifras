import os
import re
import json

BASE_DIR = r'C:\Users\User\Desktop\Python\Musica'
MONSTRO_DIR = os.path.join(BASE_DIR, 'monstro_1')
DATA_DIR = os.path.join(BASE_DIR, 'data', 'songs')
HUB_HTML = os.path.join(BASE_DIR, 'public', 'index.html')

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

app_dirs = [d for d in os.listdir(MONSTRO_DIR) if os.path.isdir(os.path.join(MONSTRO_DIR, d)) and d.endswith('App') and d != '_TemplateApp']

for d in app_dirs:
    app_path = os.path.join(MONSTRO_DIR, d)
    index_path = os.path.join(app_path, 'index.html')
    script_path = os.path.join(app_path, 'script.js')
    
    if not os.path.exists(index_path) or not os.path.exists(script_path):
        continue
        
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()
        
    with open(script_path, 'r', encoding='utf-8') as f:
        js = f.read()
        
    title_match = re.search(r'<h1 class="song-title">(.*?)</h1>', html)
    artist_match = re.search(r'<h2 class="song-artist">(.*?)</h2>', html)
    lyrics_match = re.search(r'<pre id="lyrics-content">(.*?)</pre>', html, re.DOTALL)
    
    chord_data_match = re.search(r'const chordData = (\{.*?\n\});', js, re.DOTALL)
    
    if not (title_match and artist_match and lyrics_match and chord_data_match):
        print(f"Skipping {d}: Missing data")
        continue
        
    title = title_match.group(1).strip()
    artist = artist_match.group(1).strip()
    lyricsHtml = lyrics_match.group(1).strip('\n')
    chordData_str = chord_data_match.group(1)
    
    # Strip trailing commas
    chordData_str = re.sub(r',\s*\}', '}', chordData_str)
    
    try:
        chordData = json.loads(chordData_str)
    except Exception as e:
        print(f"Failed to parse chordData for {d}: {e}")
        try:
            fixed = re.sub(r'(\s)([a-zA-Z0-9_]+):', r'\1"\2":', chordData_str)
            chordData = json.loads(fixed)
        except:
            print(f"Fallback failed for {d}")
            continue
            
    # Save to JSON
    file_name = d.replace('App', '')
    json_path = os.path.join(DATA_DIR, f"{file_name}.json")
    
    song_json = {
        "title": title,
        "artist": artist,
        "lyricsHtml": "\n" + lyricsHtml + "\n",
        "chordData": chordData
    }
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(song_json, f, ensure_ascii=False, indent=4)
        
    # Update hub
    with open(HUB_HTML, "r", encoding="utf-8") as f:
        hub_content = f.read()
    
    card_html = f'''
            <a href="viewer.html?song={file_name}" class="song-link">
                {title}
                <span class="song-artist">{artist}</span>
            </a>'''
            
    if f'viewer.html?song={file_name}' not in hub_content:
        hub_content = hub_content.replace('</div>\n</body>', card_html + '\n    </div>\n</body>')
        with open(HUB_HTML, "w", encoding="utf-8") as f:
            f.write(hub_content)
            
    print(f"Migrated {d}")
