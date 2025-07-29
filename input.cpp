#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
using namespace std;

// Función auxiliar para invertir una cadena
string invertirCadena(const string& str) {
    string invertida = str;
    reverse(invertida.begin(), invertida.end());
    return invertida;
}

// Función para contar vocales
int contarVocales(const string& str) {
    int count = 0;
    for (char c : str) {
        char ch = tolower(c);
        if (ch == 'a' || ch == 'e' || ch == 'i' || ch == 'o' || ch == 'u') {
            count++;
        }
    }
    return count;
}

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

    cout << "\nTu nombre al revés es: " << invertirCadena(nombre_usuario) << endl;
    cout << "Tiene " << contarVocales(nombre_usuario) << " vocales." << endl;

    // Extra: guardar letras en vector
    vector<char> letras;
    for (char c : nombre_usuario) {
        if (isalpha(c)) {
            letras.push_back(c);
        }
    }

    cout << "Letras almacenadas en el vector: ";
    for (char l : letras) {
        cout << l << " ";
    }
    cout << endl;

    // Verificar si hay alguna letra duplicada
    bool duplicado = false;
    for (size_t i = 0; i < letras.size(); i++) {
        for (size_t j = i + 1; j < letras.size(); j++) {
            if (letras[i] == letras[j]) {
                duplicado = true;
                break;
            }
        }
        if (duplicado) break;
    }

    if (duplicado) {
        cout << "Tu nombre tiene letras repetidas." << endl;
    } else {
        cout << "Tu nombre no tiene letras repetidas." << endl;
    }

    cout << "\n¡Programa terminado!" << endl;
    return 0;
}
