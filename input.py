def main():

    nombre_usuario = input("Por favor, ingresa tu nombre: ")

    if not nombre_usuario:
        print("No ingresaste ningún nombre. ¡Hasta luego!")
        return 

    print(f"\n¡Hola, {nombre_usuario}!") 

    print("Las letras de tu nombre son:")

    letras_nombre = [] 
    for letra in nombre_usuario:
        if letra != ' ':
            letras_nombre.append(letra) 
    if letras_nombre:
        for l in letras_nombre:
            print(f"- {l}")

    edad = input("¿Cuántos años tienes?: ")
    min_edad = 18

    if int(edad) >= min_edad:
        print("¡Eres mayor de edad!")
    else:
        diff = min_edad - int(edad)
        print("Te faltan", diff, "años para ser mayor de edad.")

    
    print("\n¡Programa terminado!")


main() 