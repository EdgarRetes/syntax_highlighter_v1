import os
import re
import time
import json
import multiprocessing as mp
from pathlib import Path

def detectar_lenguaje(filename):
    if filename.endswith('.cpp'):
        return 'Cpp'
    elif filename.endswith('.hs'):
        return 'Haskell'
    elif filename.endswith('.pas'):
        return 'Pascal'
    return None

def leer_codigo(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def simular_tokenizado_html(codigo, lenguaje):
    return f"""
<!DOCTYPE html>
<html>
<head><title>Tokenized Code - {lenguaje}</title></head>
<body><pre><code>
{codigo}
</code></pre></body>
</html>
"""

def procesar_archivo(path):
    start = time.time()
    lenguaje = detectar_lenguaje(str(path))
    if not lenguaje:
        return None
    codigo = leer_codigo(path)
    html = simular_tokenizado_html(codigo, lenguaje)
    output_path = Path("salidas_html") / (path.stem + f".{lenguaje}.html")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    end = time.time()
    return {'archivo': str(path), 'lenguaje': lenguaje, 'tiempo': end - start}

def version_secuencial(directorio):
    resultados = []
    for root, _, files in os.walk(directorio):
        for file in files:
            if file.endswith(('.cpp', '.hs', '.pas')):
                result = procesar_archivo(Path(root) / file)
                if result:
                    resultados.append(result)
    return resultados

def version_paralela(directorio):
    rutas = []
    for root, _, files in os.walk(directorio):
        for file in files:
            if file.endswith(('.cpp', '.hs', '.pas')):
                rutas.append(Path(root) / file)
    with mp.Pool(mp.cpu_count()) as pool:
        resultados = pool.map(procesar_archivo, rutas)
    return [r for r in resultados if r is not None]

if __name__ == '__main__':
    carpeta = 'archivos_fuente'

    print("Ejecutando versión secuencial...")
    t0 = time.time()
    secuencial = version_secuencial(carpeta)
    t1 = time.time()
    tiempo_secuencial = t1 - t0

    print("Ejecutando versión paralela...")
    t2 = time.time()
    paralela = version_paralela(carpeta)
    t3 = time.time()
    tiempo_paralela = t3 - t2

    speedup = round(tiempo_secuencial / tiempo_paralela, 2) if tiempo_paralela else None

    print(f"\nTiempo secuencial: {tiempo_secuencial:.4f}s")
    print(f"Tiempo paralelo:   {tiempo_paralela:.4f}s")
    print(f"Speedup: {speedup}x")

    with open("resumen_resultados.json", 'w') as f:
        json.dump({
            'tiempo_secuencial': tiempo_secuencial,
            'tiempo_paralela': tiempo_paralela,
            'speedup': speedup,
            'procesados': len(paralela)
        }, f, indent=2)