import os
import re

viewer_path = r'C:\Users\User\Desktop\Python\Musica\public\viewer.html'
with open(viewer_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fix CSS/JS paths
html = re.sub(r'href="style\.css\?[^"]*"', 'href="assets/css/style.css"', html)
html = re.sub(r'href="\.\./modules/piano-keyboard\.css\?[^"]*"', 'href="assets/modules/piano-keyboard.css"', html)
html = re.sub(r'src="script\.js\?[^"]*"', 'src="assets/js/script.js"', html)
html = html.replace('href="../index.html"', 'href="index.html"')

# We also need to copy piano-keyboard.css
with open(viewer_path, 'w', encoding='utf-8') as f:
    f.write(html)
