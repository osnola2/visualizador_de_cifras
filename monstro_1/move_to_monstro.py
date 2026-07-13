import os
import subprocess
import shutil

BASE_DIR = r'C:\Users\User\Desktop\Python\Musica'
MONSTRO_DIR = os.path.join(BASE_DIR, 'monstro_1')

if not os.path.exists(MONSTRO_DIR):
    os.makedirs(MONSTRO_DIR)

# Get all items in BASE_DIR
items = os.listdir(BASE_DIR)
items_to_move = [item for item in items if item not in ('.git', 'monstro_1')]

for item in items_to_move:
    src = os.path.join(BASE_DIR, item)
    dst = os.path.join(MONSTRO_DIR, item)
    
    # Try git mv first, if fails (e.g. not tracked), fallback to shutil.move
    res = subprocess.run(['git', 'mv', item, 'monstro_1/'], cwd=BASE_DIR, capture_output=True)
    if res.returncode != 0:
        print(f'git mv failed for {item}, moving manually.')
        shutil.move(src, dst)
    else:
        print(f'git mv success for {item}')

print("Move complete.")
