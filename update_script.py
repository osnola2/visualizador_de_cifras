import os

script_path = r'C:\Users\User\Desktop\Python\Musica\public\assets\js\script.js'
with open(script_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Remove the injection tag and DOMContentLoaded start
js = js.replace('// {{CHORD_DATA_INJECTION}}', '')
js = js.replace("document.addEventListener('DOMContentLoaded', () => {\n", "")

# We need to find the end of the old DOMContentLoaded block, which is the last line });
# Actually, the last line is });
if js.strip().endswith('});'):
    js = js[:js.rfind('});')]

new_header = '''let chordData = {};

document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const songId = urlParams.get('song');

    if (!songId) {
        document.getElementById('song-title-el').textContent = 'Nenhuma música selecionada';
        document.getElementById('song-artist-el').textContent = '';
        return;
    }

    try {
        const response = await fetch(../data/songs/.json);
        if (!response.ok) throw new Error('Música não encontrada');
        const data = await response.json();
        
        document.getElementById('song-title-el').textContent = data.title;
        document.getElementById('song-artist-el').textContent = data.artist;
        document.getElementById('lyrics-content').innerHTML = data.lyricsHtml;
        chordData = data.chordData;
        
        initViewer();
    } catch (e) {
        document.getElementById('song-title-el').textContent = 'Erro ao carregar';
        document.getElementById('song-artist-el').textContent = e.message;
    }
});

function initViewer() {
'''

new_js = new_header + js + "\n}\n"

with open(script_path, 'w', encoding='utf-8') as f:
    f.write(new_js)

print("script.js updated.")
