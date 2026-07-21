import os

HUB_HTML = r'C:\Users\User\Desktop\Python\Musica\public\index.html'

html = '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Visualizador de Cifras - Hub</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #0f172a;
            color: #fff;
            margin: 0;
            padding: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        h1 {
            color: #38bdf8;
            margin-bottom: 2rem;
        }
        .song-list {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            width: 100%;
            max-width: 600px;
        }
        .song-link {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.5rem;
            background: rgba(255,255,255,0.05);
            border-radius: 8px;
            text-decoration: none;
            color: #fff;
            font-size: 1.2rem;
            font-weight: bold;
            transition: background 0.2s, transform 0.1s;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .song-link:hover {
            background: rgba(255,255,255,0.1);
            transform: translateY(-2px);
            border-color: #38bdf8;
        }
        .song-artist {
            font-size: 0.9rem;
            color: #94a3b8;
            font-weight: normal;
        }
    </style>
</head>
<body>
    <h1>Catálogo de Músicas</h1>
    <div class="song-list" id="song-list-container">
        <!-- Songs will be injected here -->
    </div>
</body>
</html>'''

with open(HUB_HTML, 'w', encoding='utf-8') as f:
    f.write(html)
