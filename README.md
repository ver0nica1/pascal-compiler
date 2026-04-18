# Analizador Léxico y Sintáctico de Pascal

Analizador léxico y sintáctico desarrollado en **Python** con **PLY** (Python Lex-Yacc) para reconocer un subconjunto del lenguaje de programación **Pascal**.

## Descripción
El proyecto implementa un compilador frontal (Front-end) compuesto por un **Lexer** que lee el archivo fuente dividiéndolo en tokens (palabras reservadas, identificadores, operadores) y un **Parser** que evalúa la estructura gramatical (sintaxis) del programa, asegurándose de que siga las reglas de bloques, expresiones y sentencias de Pascal.

## Características
- **Lexer:** Reconocimiento de palabras reservadas, variables, identificadores, tipos numéricos, cadenas, símbolos y manejo de comentarios.
- **Parser:** Gramática de programas Pascal, incluyendo subprogramas, bloques `begin...end`, condicionales, ciclos (`for`, `while`, `repeat`) y expresiones aritméticas/lógicas.
- **Manejo de Errores Mejorado:** Recolecta todos los errores léxicos y sintácticos indicando en qué línea suceden. Finaliza imprimiendo un resumen con el total de líneas analizadas y un listado de todos los errores encontrados en lugar de detenerse en el primero.

## Archivos Principales
- `lexer.py`: Analizador léxico (identificación de tokens).
- `parser.py`: Analizador sintáctico y script principal de ejecución.
- `input.pas`: Archivo de código fuente Pascal de prueba.

## Requisitos
- Python 3
- Librería `ply`

## Instalación
```bash
pip install ply
```

## Ejecución
Para analizar el archivo por defecto (`input.pas`):
```bash
python parser.py
```

Para analizar un archivo específico:
```bash
python parser.py mi_archivo.pas
```

## Ejemplo de Salida (Con Errores)
```text
Se analizaron 6 líneas.
Se encontraron 2 error(es):
 - ERROR LÉXICO en línea 5: carácter ilegal '@'
 - ERROR SINTÁCTICO en línea 5: no se esperaba el token '5'
```

## Ejemplo de Salida (Éxito)
```text
Se analizaron 45 líneas correctamente.
[OK] El parser reconoció correctamente el programa Pascal
```