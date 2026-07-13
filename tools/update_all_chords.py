import os
import re
import json
import sys

sys.path.append(r'C:\Users\User\Desktop\Python\Musica')
from tools.chord_parser import parse_chord

BASE_DIR = r'C:\Users\User\Desktop\Python\Musica'
app_dirs = [d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d)) and d.endswith('App') and d != '_TemplateApp']

for d in app_dirs:
    script_path = os.path.join(BASE_DIR, d, 'script.js')
    if not os.path.exists(script_path): continue
    
    with open(script_path, 'r', encoding='utf-8') as f:
        js = f.read()
        
    match = re.search(r'const chordData = (\{.*?\n\});', js, re.DOTALL)
    if not match: continue
    
    # We will find all chord keys like "chordName": {
    # Actually, let's just find all data-chord="XXX" in index.html to know what chords are needed!
    index_path = os.path.join(BASE_DIR, d, 'index.html')
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    chords = set(re.findall(r'data-chord="([^"]+)"', html))
    
    new_chord_data = {}
    for c in chords:
        notes, display, types = parse_chord(c)
        new_chord_data[c] = {
            'name': c,
            'notes': notes,
            'displayNotes': display,
            'noteTypes': types
        }
        
    # Format to JS object string
    js_obj = "{\n"
    for c, data in new_chord_data.items():
        js_obj += f'    "{c}": {json.dumps(data)},\n'
    js_obj += "};"
    
    new_js = js[:match.start()] + "const chordData = " + js_obj + js[match.end():]
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(new_js)
    print(f'Updated {d}')
