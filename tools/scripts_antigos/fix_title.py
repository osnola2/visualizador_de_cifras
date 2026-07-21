import os

viewer_path = r'C:\Users\User\Desktop\Python\Musica\public\viewer.html'
with open(viewer_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the title tag content
import re
html = re.sub(r'<title>.*?</title>', '<title>Visualizador de Cifras</title>', html)

with open(viewer_path, 'w', encoding='utf-8') as f:
    f.write(html)
