from pathlib import Path
import random

def generar_archivos(base_dir=".", cantidad=2000):
    base_dir = Path(base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    lenguajes = {
        'cpp': '#include<iostream>\nint main() { return 0; }',
        'hs': 'main = putStrLn "Hola mundo"',
        'pas': 'program Hello; begin writeln(\'Hello, world!\'); end.',
        'py': 'print("Hola mundo")'
    }

    for i in range(cantidad):
        lang = random.choice(list(lenguajes.keys()))
        contenido = lenguajes[lang]
        filename = base_dir / f"input_{i}.{lang}"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(contenido)

generar_archivos("inputs", 2000) 
