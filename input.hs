module Main where

import System.IO

-- Función para obtener las letras de un nombre
obtenerLetras :: String -> [Char]
obtenerLetras = filter (/= ' ')

-- Función principal
main :: IO ()
main = do
    putStr "Por favor, ingresa tu nombre: "
    hFlush stdout
    nombreUsuario <- getLine
    
    if null nombreUsuario
        then putStrLn "No ingresaste ningún nombre. ¡Hasta luego!"
        else do
            putStrLn $ "\n¡Hola, " ++ nombreUsuario ++ "!"
            putStrLn "Las letras de tu nombre son:"
            mapM_ (\c -> putStrLn $ "- " ++ [c]) (obtenerLetras nombreUsuario)
            
            putStr "¿Cuántos años tienes?: "
            hFlush stdout
            edadStr <- getLine
            let edad = read edadStr :: Int
                minEdad = 18
            
            if edad >= minEdad
                then putStrLn "¡Eres mayor de edad!"
                else putStrLn $ "Te faltan " ++ show (minEdad - edad) ++ " años para ser mayor de edad."
            
            putStrLn "\n¡Programa terminado!"