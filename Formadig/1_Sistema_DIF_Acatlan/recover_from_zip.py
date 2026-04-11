import zipfile
import os
import shutil

zip_path = r"C:\Users\erick\Downloads\Formadig (4).zip"
extract_to = r"C:\Users\erick\Downloads"

count = 0
with zipfile.ZipFile(zip_path, 'r') as z:
    for f in z.namelist():
        if f.endswith('.html'):
            z.extract(f, extract_to)
            count += 1
            print(f"Restaurado: {f}")

print(f"Total archivos HTML recuperados de Github: {count}")
