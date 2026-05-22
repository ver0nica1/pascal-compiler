"""
Compilador Pascal - Punto de entrada principal
Ejecuta los tres análisis en orden:
  1. Léxico   → errores de caracteres ilegales
  2. Sintáctico → errores de estructura gramatical
  3. Semántico → errores de uso, tipos y declaraciones
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import lexer as pascal_lexer
import parser as pascal_parser
import semantico as pascal_semantico
import parser_sem

SEP  = "=" * 60
SEP2 = "-" * 60


def leer_archivo(filename):
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except FileNotFoundError:
        print(f"ERROR: Archivo '{filename}' no encontrado.")
        sys.exit(1)


def analisis_lexico(data):
    pascal_lexer.lexer_errors = []
    pascal_lexer.lexer.lineno = 1
    pascal_lexer.lexer.input(data)

    tokens = []
    while True:
        tok = pascal_lexer.lexer.token()
        if not tok:
            break
        tokens.append(tok)

    num_lineas = len(data.splitlines())
    return tokens, list(pascal_lexer.lexer_errors), num_lineas


def analisis_sintactico(data):
    pascal_lexer.lexer_errors = []
    pascal_lexer.lexer.lineno = 1
    pascal_parser.errors_list.clear()
    pascal_parser.parser.parse(data, lexer=pascal_lexer.lexer, tracking=True)
    return list(pascal_lexer.lexer_errors) + list(pascal_parser.errors_list)


def analisis_semantico(data):
    pascal_lexer.lexer_errors = []
    pascal_lexer.lexer.lineno = 1
    parser_sem.errors_list.clear()

    ast = parser_sem.parser.parse(data, lexer=pascal_lexer.lexer, tracking=True)
    errores_parse = list(pascal_lexer.lexer_errors) + list(parser_sem.errors_list)

    analizador = pascal_semantico.AnalizadorSemantico()
    pascal_semantico.registrar_builtins(analizador)

    if ast is not None and len(errores_parse) == 0:
        analizador.analizar(ast)

    analizador.errores_parse = errores_parse
    return analizador


def imprimir_encabezado(filename, num_tokens, num_lineas):
    print(SEP)
    print(f"  COMPILADOR PASCAL")
    print(f"  Archivo : {filename}")
    print(f"  Tokens  : {num_tokens}    Líneas: {num_lineas}")
    print(SEP)


def imprimir_seccion_lexica(errores):
    print(f"\n{'[ 1 ] ANÁLISIS LÉXICO':^60}")
    print(SEP2)
    if not errores:
        print("  [OK] Sin errores léxicos.")
    else:
        print(f"  [ERROR] {len(errores)} error(es) léxico(s) encontrado(s):\n")
        for i, e in enumerate(errores, 1):
            print(f"    {i}. {e}")


def imprimir_seccion_sintactica(errores):
    print(f"\n{'[ 2 ] ANÁLISIS SINTÁCTICO':^60}")
    print(SEP2)
    if not errores:
        print("  [OK] Sin errores sintácticos.")
    else:
        print(f"  [ERROR] {len(errores)} error(es) sintáctico(s) encontrado(s):\n")
        for i, e in enumerate(errores, 1):
            print(f"    {i}. {e}")


def imprimir_seccion_semantica(analizador):
    errores = getattr(analizador, 'errores_parse', []) + analizador.errores

    print(f"\n{'[ 3 ] ANÁLISIS SEMÁNTICO':^60}")
    print(SEP2)

    if getattr(analizador, 'errores_parse', []):
        print(f"  [OMITIDO] Análisis semántico no ejecutado por errores de parseo:")
        for i, e in enumerate(analizador.errores_parse, 1):
            print(f"    {i}. {e}")
    elif not analizador.errores:
        print("  [OK] Sin errores semánticos.")
    else:
        print(f"  [ERROR] {len(analizador.errores)} error(es) semántico(s) encontrado(s):\n")
        for i, e in enumerate(analizador.errores, 1):
            print(f"    {i}. {e}")


def imprimir_tabla_simbolos(analizador):
    print(f"\n{'[ 4 ] TABLA DE SÍMBOLOS':^60}")
    print(SEP2)
    analizador.tabla.imprimir_tabla()


def imprimir_resumen(err_lex, err_sin, analizador):
    err_sem = getattr(analizador, 'errores_parse', []) + analizador.errores
    total   = len(err_lex) + len(err_sin) + len(err_sem)

    print(f"\n{'[ RESUMEN FINAL ]':^60}")
    print(SEP2)
    print(f"  Errores léxicos    : {len(err_lex)}")
    print(f"  Errores sintácticos: {len(err_sin)}")
    print(f"  Errores semánticos : {len(err_sem)}")
    print(SEP2)
    if total == 0:
        print("  [OK] COMPILACIÓN EXITOSA — el código es correcto.")
    else:
        print(f"  [FALLO] Se encontraron {total} error(es) en total.")
    print(SEP)


if __name__ == '__main__':
    filename = sys.argv[1] if len(sys.argv) > 1 else 'input.pas'
    data     = leer_archivo(filename)

    tokens, err_lex, num_lineas = analisis_lexico(data)
    err_sin                     = analisis_sintactico(data)
    analizador                  = analisis_semantico(data)

    imprimir_encabezado(filename, len(tokens), num_lineas)
    imprimir_seccion_lexica(err_lex)
    imprimir_seccion_sintactica(err_sin)
    imprimir_seccion_semantica(analizador)
    imprimir_tabla_simbolos(analizador)
    imprimir_resumen(err_lex, err_sin, analizador)
