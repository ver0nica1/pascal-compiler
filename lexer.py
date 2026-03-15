import ply.lex as lex
import re
import sys

# Analizador léxico para un subconjunto de Pascal

tokens = (

    # 35 palabras reservadas de la documentación básica de pascal basic syntax

    'AND', 'ARRAY', 'BEGIN', 'CASE', 'CONST',
    'DIV', 'DO', 'DOWNTO', 'ELSE', 'END',
    'FILE', 'FOR', 'FUNCTION', 'GOTO', 'IF',
    'IN', 'LABEL', 'MOD', 'NIL', 'NOT',
    'OF', 'OR', 'PACKED', 'PROCEDURE', 'PROGRAM',
    'RECORD', 'REPEAT', 'SET', 'THEN', 'TO',
    'TYPE', 'UNTIL', 'VAR', 'WHILE', 'WITH',

    # Tipos de dato

    'INTEGER', 'REAL', 'BOOLEAN', 'CHAR', 'STRING',

    # Literales

    'NUMBER',
    'CHARCONST',

    # Identificador

    'ID',

    # Operadores y símbolos

    'PLUS',
    'MINUS',
    'TIMES',
    'DIVISION',
    'EQ',
    'NE',
    'LT',
    'GT',
    'LE',
    'GE',
    'ASSIGN',
    'RANGE',
    'DOT',
    'COMMA',
    'SEMICOLON',
    'COLON',
    'LPAR',
    'RPAR',
    'LBR',
    'RBR'
)

t_PLUS      = r'\+'
t_MINUS     = r'\-'
t_TIMES     = r'\*'
t_DIVISION  = r'/'
t_EQ        = r'='
t_LT        = r'<'
t_GT        = r'>'
t_DOT       = r'\.'
t_COMMA     = r','
t_SEMICOLON = r';'
t_COLON     = r':'
t_LPAR      = r'\('
t_RPAR      = r'\)'
t_LBR       = r'\['
t_RBR       = r'\]'

# Palabras reservadas

def t_PROCEDURE(t):
    r'procedure\b'
    return t

def t_FUNCTION(t):
    r'function\b'
    return t

def t_BOOLEAN(t):
    r'boolean\b'
    return t

def t_INTEGER(t):
    r'integer\b'
    return t

def t_PROGRAM(t):
    r'program\b'
    return t

def t_DOWNTO(t):
    r'downto\b'
    return t

def t_PACKED(t):
    r'packed\b'
    return t

def t_RECORD(t):
    r'record\b'
    return t

def t_REPEAT(t):
    r'repeat\b'
    return t

def t_STRING(t):
    r'string\b'
    return t

def t_ARRAY(t):
    r'array\b'
    return t

def t_BEGIN(t):
    r'begin\b'
    return t

def t_CONST(t):
    r'const\b'
    return t

def t_LABEL(t):
    r'label\b'
    return t

def t_UNTIL(t):
    r'until\b'
    return t

def t_WHILE(t):
    r'while\b'
    return t

def t_CASE(t):
    r'case\b'
    return t

def t_CHAR(t):
    r'char\b'
    return t

def t_ELSE(t):
    r'else\b'
    return t

def t_FILE(t):
    r'file\b'
    return t

def t_GOTO(t):
    r'goto\b'
    return t

def t_REAL(t):
    r'real\b'
    return t

def t_THEN(t):
    r'then\b'
    return t

def t_TYPE(t):
    r'type\b'
    return t

def t_WITH(t):
    r'with\b'
    return t

def t_AND(t):
    r'and\b'
    return t

def t_DIV(t):
    r'div\b'
    return t

def t_END(t):
    r'end\b'
    return t

def t_FOR(t):
    r'for\b'
    return t

def t_MOD(t):
    r'mod\b'
    return t

def t_NIL(t):
    r'nil\b'
    return t

def t_NOT(t):
    r'not\b'
    return t

def t_SET(t):
    r'set\b'
    return t

def t_VAR(t):
    r'var\b'
    return t

def t_DO(t):
    r'do\b'
    return t

def t_IF(t):
    r'if\b'
    return t

def t_IN(t):
    r'in\b'
    return t

def t_OF(t):
    r'of\b'
    return t

def t_OR(t):
    r'or\b'
    return t

def t_TO(t):
    r'to\b'
    return t

# Literales

def t_CHARCONST(t):
    r'\'[^\']*\'|"[^"]*"'
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?([eE][+-]?\d+)?'
    if '.' in t.value or 'e' in t.value.lower():
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    return t

# Operadores compuestos (como funciones, después de ID)

def t_ASSIGN(t):
    r':='
    return t

def t_NE(t):
    r'<>'
    return t

def t_LE(t):
    r'<='
    return t

def t_GE(t):
    r'>='
    return t

def t_RANGE(t):
    r'\.\.'
    return t

# Nueva línea

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

t_ignore = ' \t\r'

# Comentarios

def t_COMMENT(t):
    r'\(\*(.|\n)*?\*\)|{[^}]*}'
    t.lexer.lineno += t.value.count('\n')

# Error léxico

def t_error(t):
    print(f"[ERROR LÉXICO] Línea {t.lexer.lineno}: carácter ilegal '{t.value[0]}'")
    t.lexer.skip(1)

# Función de prueba

def test(data, lexer):
    lexer.input(data)
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)

# Construye el lexer

lexer = lex.lex(reflags=re.IGNORECASE)

# main

if __name__ == '__main__':
    if len(sys.argv) > 1:
        fin = sys.argv[1]
    else:
        fin = 'input.pas'
    f = open(fin, 'r')
    data = f.read()
    lexer.input(data)
    test(data, lexer)