import os, glob, shutil

for f in glob.glob('*App/style.css'):
    if not f.startswith('_TemplateApp'):
        shutil.copy('_TemplateApp/style.css', f)
print("Styles copied successfully.")
