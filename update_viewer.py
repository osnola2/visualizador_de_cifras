import os
import re

viewer_path = r'C:\Users\User\Desktop\Python\Musica\public\viewer.html'
with open(viewer_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fix CSS/JS paths
html = html.replace('href="style.css"', 'href="assets/css/style.css"')
html = html.replace('src="../modules/', 'src="assets/modules/')
html = html.replace('src="script.js"', 'src="assets/js/script.js"')

# Fix placeholders
html = html.replace('{{SONG_TITLE}}', '<span id="song-title-el">Carregando...</span>')
html = html.replace('{{SONG_ARTIST}}', '<span id="song-artist-el">Aguarde...</span>')
html = html.replace('{{LYRICS_CONTENT}}', '')

with open(viewer_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("viewer.html updated.")
