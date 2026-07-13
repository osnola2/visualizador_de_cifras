import os

template_path = r'_TemplateApp\script.js'
with open(template_path, 'r', encoding='utf-8') as f:
    template_content = f.read()

# Get the part after the injection tag
parts = template_content.split('// {{CHORD_DATA_INJECTION}}')
if len(parts) > 1:
    t_content = parts[1]
else:
    t_content = template_content

dirs = [d for d in os.listdir('.') if os.path.isdir(d) and d.endswith('App') and d != '_TemplateApp']

for d in dirs:
    script_path = os.path.join(d, 'script.js')
    if os.path.exists(script_path):
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract chordData
        script_parts = content.split('document.addEventListener', 1)
        if len(script_parts) == 2:
            chord_data = script_parts[0]
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(chord_data + "\n" + t_content.lstrip())
                
print("Patched successfully!")
