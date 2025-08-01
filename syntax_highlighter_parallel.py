import os
import re
import time
import multiprocessing as mp
from pathlib import Path
from main import load_lexical_rules, tokenize_code, generate_html_output

def detectar_lenguaje(filename):
    if filename.endswith('.cpp'):
        return 'Cpp'
    elif filename.endswith('.hs'):
        return 'Haskell'
    elif filename.endswith('.pas'):
        return 'Pascal'
    elif filename.endswith('.py'):
        return 'Python'
    return None

# Se cargan las reglas una sola vez
LEXICAL_RULES = load_lexical_rules("lexical_definitions.txt")

def procesar_archivo(path):
    lenguaje = detectar_lenguaje(path.name)
    if lenguaje is None or lenguaje not in LEXICAL_RULES:
        return None

    start = time.time()
    tokens = tokenize_code(path, LEXICAL_RULES[lenguaje])
    elapsed = time.time() - start

    generate_html_output(str(path), lenguaje, tokens, elapsed)
    return str(path) + ".html"

def main():
    carpeta_entrada = Path("inputs")
    archivos = list(carpeta_entrada.glob("*"))
    archivos = [archivo for archivo in archivos if detectar_lenguaje(archivo.name)]

    print(f"[INFO] Procesando {len(archivos)} archivos...\n")

    # --- Modo secuencial ---
    print("[INFO] Iniciando procesamiento secuencial...")
    start_secuencial = time.time()
    resultados_secuencial = []
    for archivo in archivos:
        resultado = procesar_archivo(archivo)
        resultados_secuencial.append(resultado)
    tiempo_secuencial = time.time() - start_secuencial
    print(f"[INFO] Procesamiento secuencial completado en {tiempo_secuencial:.2f} segundos.")
    print(f"[INFO] Archivos procesados: {len([r for r in resultados_secuencial if r])}\n")

    # --- Modo paralelo ---
    print("[INFO] Iniciando procesamiento paralelo...")
    start_paralelo = time.time()
    with mp.Pool(mp.cpu_count()) as pool:
        resultados_paralelo = pool.map(procesar_archivo, archivos)
    tiempo_paralelo = time.time() - start_paralelo
    print(f"[INFO] Procesamiento paralelo completado en {tiempo_paralelo:.2f} segundos.")
    print(f"[INFO] Archivos procesados: {len([r for r in resultados_paralelo if r])}\n")

    # --- Comparación ---
    print("[INFO] Comparación de tiempos:")
    print(f"  • Secuencial: {tiempo_secuencial:.2f} segundos")
    print(f"  • Paralelo:   {tiempo_paralelo:.2f} segundos")

if __name__ == "__main__":
    main()
