import os, glob

for f in glob.glob('*App/script.js'):
    if f != '_TemplateApp/script.js':
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        content = content.replace('"tension"', '"ninth"')
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
            
print("Tension notes converted to ninth.")
