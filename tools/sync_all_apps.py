import os
import re
import shutil
import glob

BASE_DIR = r"C:\Users\User\Desktop\Python\Musica"
TEMPLATE_DIR = os.path.join(BASE_DIR, "_TemplateApp")

def sync_apps():
    template_index = os.path.join(TEMPLATE_DIR, "index.html")
    template_script = os.path.join(TEMPLATE_DIR, "script.js")
    template_css = os.path.join(TEMPLATE_DIR, "style.css")
    
    with open(template_index, "r", encoding="utf-8") as f:
        t_html = f.read()
    with open(template_script, "r", encoding="utf-8") as f:
        t_js = f.read()

    app_dirs = [d for d in os.listdir(BASE_DIR) if os.path.isdir(d) and d.endswith("App") and d != "_TemplateApp"]
    
    success_count = 0
    error_count = 0

    for d in app_dirs:
        app_path = os.path.join(BASE_DIR, d)
        index_path = os.path.join(app_path, "index.html")
        script_path = os.path.join(app_path, "script.js")
        
        try:
            # 1. Read existing
            with open(index_path, "r", encoding="utf-8") as f:
                old_html = f.read()
            with open(script_path, "r", encoding="utf-8") as f:
                old_js = f.read()
                
            # 2. Extract Data
            title_match = re.search(r'<h1 class="song-title">(.*?)</h1>', old_html)
            artist_match = re.search(r'<h2 class="song-artist">(.*?)</h2>', old_html)
            lyrics_match = re.search(r'<pre id="lyrics-content">(.*?)</pre>', old_html, re.DOTALL)
            
            if not (title_match and artist_match and lyrics_match):
                print(f"Skipping {d}: Could not extract title/artist/lyrics from index.html")
                error_count += 1
                continue
                
            title = title_match.group(1).strip()
            artist = artist_match.group(1).strip()
            lyrics = lyrics_match.group(1).strip('\n')
            
            chord_data_match = re.search(r'(const chordData = \{.*?\n\};)', old_js, re.DOTALL)
            if not chord_data_match:
                print(f"Skipping {d}: Could not extract chordData from script.js")
                error_count += 1
                continue
                
            chord_data = chord_data_match.group(1)
            
            # 3. Inject into Template
            new_html = t_html.replace("{{SONG_TITLE}}", title)
            new_html = new_html.replace("{{SONG_ARTIST}}", artist)
            # Ensure newline around lyrics like the original
            new_html = new_html.replace("{{LYRICS_CONTENT}}", "\n" + lyrics + "\n")
            
            new_js = t_js.replace("// {{CHORD_DATA_INJECTION}}", chord_data)
            
            # 4. Write back
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(new_html)
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(new_js)
            
            # 5. Copy CSS directly
            shutil.copy2(template_css, os.path.join(app_path, "style.css"))
            
            print(f"Synced successfully: {d}")
            success_count += 1
            
        except Exception as e:
            print(f"Error syncing {d}: {e}")
            error_count += 1

    print(f"\nSync complete. {success_count} synced, {error_count} failed.")

if __name__ == "__main__":
    sync_apps()
