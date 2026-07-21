import re

script_path = r'C:\Users\User\Desktop\Python\Musica\public\assets\js\script.js'
with open(script_path, 'r', encoding='utf-8') as f:
    js = f.read()

# Replace the inner });\n\ndocument.addEventListener('DOMContentLoaded', () => { with nothing.
js = js.replace("    });\n});\n\ndocument.addEventListener('DOMContentLoaded', () => {\n", "    });\n\n")

# Now the bottom of the file is:
#         });
#     }
# }
# Which is correct for closing 	ogglePianoBtn.addEventListener and if (togglePianoBtn), and then unction initViewer().

with open(script_path, 'w', encoding='utf-8') as f:
    f.write(js)
