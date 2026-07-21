import os
import json

DATA_DIR = r'C:\Users\User\Desktop\Python\Musica\data\songs'
for fname in os.listdir(DATA_DIR):
    if fname.endswith('.json'):
        json_path = os.path.join(DATA_DIR, fname)
        js_path = os.path.join(DATA_DIR, fname.replace('.json', '.js'))
        with open(json_path, 'r', encoding='utf-8') as f:
            content = f.read()
        js_content = "window.SONG_DATA = " + content + ";\n"
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"Converted {fname} -> .js")
