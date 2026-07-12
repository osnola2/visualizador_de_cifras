import urllib.request
import re
import sys
import json
import os

def fetch_and_parse(url, output_dir):
    print(f"Fetching {url} ...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        response = urllib.request.urlopen(req)
        html = response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return

    # Extract Song Title and Artist
    title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.IGNORECASE)
    artist_match = re.search(r'<h2[^>]*>.*?<a[^>]*>(.*?)</a>.*?</h2>', html, re.IGNORECASE)
    
    song_title = title_match.group(1).strip() if title_match else "Unknown Title"
    song_artist = artist_match.group(1).strip() if artist_match else "Unknown Artist"
    
    # Extract Lyrics and Chords block
    pre_match = re.search(r'<pre>(.*?)</pre>', html, re.DOTALL | re.IGNORECASE)
    if not pre_match:
        print("Could not find <pre> tag. Page format might be different.")
        return
        
    pre_content = pre_match.group(1)
    
    # Strip <span class="cnt">...</span> which contains tab ASCII art
    pre_content = re.sub(r'<span class="cnt">.*?</span>', '', pre_content, flags=re.DOTALL)
    
    # Strip <span class="tablatura"> and </span> tags, keeping their content
    pre_content = re.sub(r'<span class="tablatura">', '', pre_content)
    pre_content = re.sub(r'</span>', '', pre_content)
    
    # Replace <b>Chord</b> with our format
    unique_chords = set()
    def chord_replacer(match):
        chord_name = match.group(1).strip()
        chord_name = re.sub(r'<[^>]+>', '', chord_name)
        unique_chords.add(chord_name)
        return f'<span class="chord" data-chord="{chord_name}">{chord_name}</span>'

    formatted_content = re.sub(r'<b>(.*?)</b>', chord_replacer, pre_content)
    
    # Generate chordData boilerplate
    chord_data_js = "const chordData = {\n"
    for idx, chord in enumerate(sorted(unique_chords)):
        chord_data_js += f'    "{chord}": {{\n'
        chord_data_js += f'        name: "{chord}",\n'
        chord_data_js += f'        notes: ["C3", "E3", "G3"], // TODO: Fill correct notes\n'
        chord_data_js += f'        displayNotes: ["C", "E", "G"], // TODO: Fill correct display\n'
        chord_data_js += f'        noteTypes: ["triad", "triad", "triad"]\n'
        chord_data_js += '    }'
        if idx < len(unique_chords) - 1:
            chord_data_js += ','
        chord_data_js += '\n'
    chord_data_js += "};\n"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, "lyrics_formatted.html"), "w", encoding="utf-8") as f:
        f.write(formatted_content)
        
    with open(os.path.join(output_dir, "chordData_boilerplate.js"), "w", encoding="utf-8") as f:
        f.write(chord_data_js)
        
    with open(os.path.join(output_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump({"title": song_title, "artist": song_artist}, f)
        
    print(f"Extraction complete for '{song_title}' by {song_artist}.")
    print(f"Found {len(unique_chords)} unique chords.")
    print(f"Files saved to {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python cifraclub_scraper.py <url> <output_dir>")
        sys.exit(1)
    fetch_and_parse(sys.argv[1], sys.argv[2])
