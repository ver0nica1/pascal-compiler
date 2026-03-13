# Analizador Léxico de Pascal

Analizador léxico desarrollado en **Python** con **PLY** para reconocer un subconjunto del lenguaje **Pascal**.

## Descripción
El proyecto implementa un lexer encargado de leer un archivo fuente en Pascal y dividirlo en **tokens**, identificando palabras reservadas, identificadores, literales, operadores y símbolos del lenguaje.

## Características
- Reconocimiento de palabras reservadas
- Identificación de variables e identificadores
- Soporte para números enteros y reales
- Reconocimiento de constantes de texto
- Detección de operadores y símbolos
- Manejo de comentarios y errores léxicos

## Archivos
- `lexer.py`: analizador léxico
- `input.pas`: archivo de prueba

## Requisitos
- Python 3
- PLY

## Instalación
````bash
pip install ply