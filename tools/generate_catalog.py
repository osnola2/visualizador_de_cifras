import os
import json
import re
import sys

def remove_accents(text):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")

def generate_catalog():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_songs_dir = os.path.join(base_dir, "data", "songs")
    catalog_js_path = os.path.join(base_dir, "data", "catalog.js")
    catalog_json_path = os.path.join(base_dir, "data", "catalog.json")
    
    songs = []
    
    if not os.path.exists(data_songs_dir):
        print(f"Directory not found: {data_songs_dir}")
        return
        
    for filename in sorted(os.listdir(data_songs_dir)):
        if not filename.endswith(".json"):
            continue
            
        file_path = os.path.join(data_songs_dir, filename)
        song_id = filename[:-5]
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                jdata = json.load(f)
                
            title = jdata.get("title", song_id)
            artist = jdata.get("artist", "Desconhecido")
            composer = jdata.get("composer", "")
            chord_data = jdata.get("chordData", {})
            chords_count = len(chord_data)
            
            # Clean artist html if any
            artist = re.sub(r'<[^>]+>', '', artist).strip()
            if not artist:
                artist = "Desconhecido"
                
            songs.append({
                "id": song_id,
                "title": title,
                "artist": artist,
                "composer": composer,
                "chordsCount": chords_count
            })
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            
    # Sort A-Z by default
    songs.sort(key=lambda x: remove_accents(x["title"]).lower())
    
    # Write JSON
    with open(catalog_json_path, "w", encoding="utf-8") as f:
        json.dump(songs, f, indent=4, ensure_ascii=False)
        
    # Write JS
    js_content = f"// Gerado automaticamente por tools/generate_catalog.py\nconst SONGS_CATALOG = {json.dumps(songs, indent=4, ensure_ascii=False)};\n"
    with open(catalog_js_path, "w", encoding="utf-8") as f:
        f.write(js_content)
        
    print(f"Generated catalog with {len(songs)} songs at {catalog_js_path} and {catalog_json_path}")

if __name__ == "__main__":
    generate_catalog()
