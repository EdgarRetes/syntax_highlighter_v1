#include <bits/stdc++.h>
using namespace std;

// Inicio programa
int main() {
    string nombre_usuario;
    cout << "Por favor, ingresa tu nombre: ";
    getline(cin, nombre_usuario);

    if (nombre_usuario.empty()) {
        cout << "No ingresaste ningún nombre. ¡Hasta luego!" << endl;
        return 0;
    }

    cout << "\n¡Hola, " << nombre_usuario << "!" << endl;
    cout << "Las letras de tu nombre son:" << endl;

    for (char c : nombre_usuario) {
        if (c != ' ') {
            cout << "- " << c << endl;
        }
    }

    string edad_str;
    cout << "¿Cuántos años tienes?: ";
    getline(cin, edad_str);
    int edad = stoi(edad_str);
    int min_edad = 18;

    if (edad >= min_edad) {
        cout << "¡Eres mayor de edad!" << endl;
    } else {
        int diff = min_edad - edad;
        cout << "Te faltan " << diff << " años para ser mayor de edad." << endl;
    }

    cout << "\n¡Programa terminado!" << endl;
    return 0;
}
